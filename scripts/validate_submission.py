#!/usr/bin/env python3
"""Validate community package metadata and ZIP structure without executing it."""

import argparse
import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLATFORM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)
MAX_ZIP_BYTES = 90 * 1024 * 1024
MAX_EXPANDED_BYTES = 512 * 1024 * 1024
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_ENTRIES = 10_000


def fail(message):
    raise SystemExit(f"VALIDATION FAILED: {message}")


def validate_semver(value):
    if not isinstance(value, str):
        fail("version must be a string.")
    match = SEMVER_RE.fullmatch(value)
    if not match:
        fail("version must be strict SemVer (MAJOR.MINOR.PATCH, optional prerelease/build).")
    prerelease = match.group(4)
    if prerelease:
        for identifier in prerelease.split("."):
            if not identifier:
                fail("SemVer prerelease identifiers cannot be empty.")
            if identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0"):
                fail("Numeric SemVer prerelease identifiers cannot contain leading zeroes.")


def validate_metadata(path, expected_name, expected_version):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid UTF-8 JSON metadata: {exc}")
    if not isinstance(data, dict):
        fail("package.json must contain a JSON object.")

    required = ("name", "version", "description", "author", "license", "greenServeFE", "platforms")
    missing = [key for key in required if key not in data]
    if missing:
        fail("missing required metadata fields: " + ", ".join(missing))

    name = data["name"]
    version = data["version"]
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        fail("name must use lowercase letters, numbers, and single hyphens.")
    validate_semver(version)
    if name != expected_name or version != expected_version:
        fail("metadata name/version must exactly match the submission directory.")
    if not isinstance(data["description"], str) or not 10 <= len(data["description"].strip()) <= 300:
        fail("description must contain 10–300 characters.")
    for field in ("author", "license", "greenServeFE"):
        if not isinstance(data[field], str) or not data[field].strip() or len(data[field]) > 160:
            fail(f"{field} must be a non-empty string of at most 160 characters.")

    platforms = data["platforms"]
    if not isinstance(platforms, list) or len(platforms) != 1:
        fail("platforms must contain exactly one platform for the submitted ZIP.")
    if not isinstance(platforms[0], str) or not PLATFORM_RE.fullmatch(platforms[0]):
        fail("platforms contains an invalid platform identifier.")

    if "entry" in data and (not isinstance(data["entry"], str) or not data["entry"].strip() or len(data["entry"]) > 256):
        fail("entry, when supplied, must be a non-empty path string.")
    return data


def validate_zip(path):
    if not path.is_file():
        fail("ZIP archive does not exist.")
    size = path.stat().st_size
    if size <= 0 or size > MAX_ZIP_BYTES:
        fail("ZIP must be non-empty and no larger than 90 MiB.")
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if not infos or len(infos) > MAX_ENTRIES:
                fail("ZIP must contain 1–10,000 entries.")
            seen = set()
            expanded = 0
            regular_files = 0
            for info in infos:
                raw = info.filename
                if not raw or "\\" in raw or raw.startswith("/"):
                    fail(f"unsafe ZIP path: {raw!r}")
                normalized = PurePosixPath(raw)
                if any(part in ("", ".", "..") for part in normalized.parts):
                    fail(f"unsafe ZIP path traversal: {raw!r}")
                if normalized.parts and ":" in normalized.parts[0]:
                    fail(f"drive-qualified ZIP path is not allowed: {raw!r}")
                key = str(normalized)
                if key in seen:
                    fail(f"duplicate ZIP path: {key}")
                seen.add(key)
                if info.flag_bits & 0x1:
                    fail(f"encrypted ZIP entries are not allowed: {key}")
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode):
                    fail(f"symbolic links are not allowed: {key}")
                if info.is_dir():
                    continue
                regular_files += 1
                if info.file_size > MAX_FILE_BYTES:
                    fail(f"individual file exceeds 128 MiB: {key}")
                expanded += info.file_size
                if expanded > MAX_EXPANDED_BYTES:
                    fail("expanded ZIP size exceeds 512 MiB.")
                if info.file_size > 1_048_576 and info.compress_size == 0:
                    fail(f"suspicious compression ratio: {key}")
                if info.compress_size and info.file_size / info.compress_size > 200:
                    fail(f"compression ratio exceeds 200:1: {key}")
            if regular_files == 0:
                fail("ZIP must contain at least one regular file.")
            bad = archive.testzip()
            if bad is not None:
                fail(f"ZIP CRC check failed for: {bad}")
    except zipfile.BadZipFile as exc:
        fail(f"invalid ZIP archive: {exc}")
    print(f"Validated ZIP: {regular_files} files, {expanded} expanded bytes, {size} compressed bytes.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--expected-name", required=True)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()
    metadata = validate_metadata(args.metadata, args.expected_name, args.expected_version)
    expected_zip = f"{metadata['name']}-{metadata['platforms'][0]}.zip"
    if args.zip.name != expected_zip:
        fail(f"ZIP filename must be {expected_zip}; do not include the version in the asset filename.")
    validate_zip(args.zip)
    print(f"Submission is structurally valid: {args.expected_name} {args.expected_version}")
    print("No submitted code was executed.")


if __name__ == "__main__":
    main()
