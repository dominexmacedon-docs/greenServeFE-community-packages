#!/usr/bin/env python3
"""Add one immutable release version to registry/index.json."""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)


def semver_key(value):
    match = SEMVER_RE.fullmatch(value)
    if not match:
        raise SystemExit(f"Invalid SemVer version in registry: {value}")
    major, minor, patch = map(int, match.group(1, 2, 3))
    pre = match.group(4)
    if pre is None:
        return (major, minor, patch, 1, ())
    parts = []
    for item in pre.split("."):
        if item.isdigit():
            if len(item) > 1 and item.startswith("0"):
                raise SystemExit(f"Invalid numeric prerelease identifier: {value}")
            parts.append((0, int(item)))
        else:
            parts.append((1, item))
    return (major, minor, patch, 0, tuple(parts))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    name, version = metadata["name"], metadata["version"]
    platforms = metadata.get("platforms", [])
    if len(platforms) != 1:
        raise SystemExit("Exactly one platform is required for each submitted archive.")
    platform = platforms[0]
    if args.tag != f"{name}-v{version}":
        raise SystemExit("Release tag does not match package name and version.")
    if not re.fullmatch(r"[0-9a-f]{64}", args.sha256):
        raise SystemExit("Invalid SHA-256 digest.")

    archive_name = f"{name}-{platform}.zip"
    index_path = Path("registry/index.json")
    registry = json.loads(index_path.read_text(encoding="utf-8"))
    packages = registry.setdefault("packages", {})
    package = packages.setdefault(name, {"name": name, "latest": None, "versions": {}})
    versions = package.setdefault("versions", {})
    if version in versions:
        raise SystemExit(f"{name} {version} is already present in the registry; versions are immutable.")

    release_base = f"https://github.com/{args.repository}/releases/download/{args.tag}"
    record = {
        "version": version,
        "tag": args.tag,
        "platform": platform,
        "download": f"{release_base}/{archive_name}",
        "checksum": f"{release_base}/{archive_name}.sha256",
        "sha256": args.sha256,
        "metadata": metadata,
        "published_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    versions[version] = record
    package["latest"] = max(versions, key=semver_key)
    package["versions"] = dict(sorted(versions.items(), key=lambda item: semver_key(item[0]), reverse=True))
    registry["registry"] = "greenServeFE-community"
    registry["schemaVersion"] = 1
    registry["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    index_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Registry updated: {name}; latest={package['latest']}")


if __name__ == "__main__":
    main()
