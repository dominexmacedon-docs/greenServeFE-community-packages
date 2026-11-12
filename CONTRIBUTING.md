# Contributing community modules

Thank you for building for greenServeFE. This repository is the reviewed release registry for community modules.

## Submission model

1. Fork this repository.
2. Add exactly two files for one package version:
   - `submissions/<package-name>/<version>/package.json`
   - `submissions/<package-name>/<version>/<package-name>-<platform>.zip`
3. Open a Pull Request against `main`.
4. Wait for the automated, read-only validation and maintainer review.
5. The repository owner reviews the exact current commit and approves the Pull Request.
6. The owner manually runs **Publish approved package** from the Actions tab, supplying the Pull Request number.

A Pull Request never publishes a release automatically. Approval must apply to the latest head commit. A maintainer runs the publishing workflow only after reviewing and testing the ZIP.

## Why a published submission PR is closed, not merged

The ZIP is used temporarily from the Pull Request for validation and publication, then uploaded as a GitHub Release asset. It is never committed to the default branch. After successful publication, the workflow copies only `package.json` into `submissions/<package-name>/<version>/package.json`, updates `registry/index.json`, comments on the Pull Request, and closes it without merging. The published repository therefore keeps the metadata in the package directory while the binary ZIP exists only in the release.

## Package metadata

Use this exact shape:

```json
{
  "name": "gs-example",
  "version": "1.0.0",
  "description": "A concise description of this greenServeFE module.",
  "author": "github-username",
  "license": "MIT",
  "greenServeFE": ">=1.0.6",
  "platforms": ["linux-x86_64"],
  "entry": "libgs_example.so"
}
```

Required fields: `name`, `version`, `description`, `author`, `license`, `greenServeFE`, and `platforms`. The `entry` field is optional. Use a lowercase package name containing letters, numbers, and single hyphens. Versions must be strict Semantic Versioning: `MAJOR.MINOR.PATCH`, optionally followed by a prerelease or build identifier. Do not prefix versions with `v`.

Each submission contains one platform archive, so `platforms` must contain exactly one platform identifier. The package name and version must match the submission directory. The archive filename is `<package-name>-<platform>.zip`; it deliberately does not contain the version. For example, package `gs_test` (if using a valid lowercase-hyphen package name, `gs-test`) for `linux-x86_64` is uploaded as `gs-test-linux-x86_64.zip`.

## ZIP requirements

- Submit one complete ZIP, named `<package-name>-<platform>.zip` (for example, `test-g-linux-x86_64.zip`).
- Maximum submitted ZIP size: 90 MiB.
- Maximum expanded size: 512 MiB.
- Maximum entries: 10,000.
- No encrypted entries, symbolic links, absolute paths, parent-directory traversal, duplicate paths, or ZIP bombs.
- Include the files needed by users to install, build, or understand the module.
- Do not include credentials, private keys, tokens, personal data, or unrelated files.
- Validation inspects the archive but does not execute its contents.

The ZIP may contain source code, headers, shared libraries, documentation, examples, and other module files. State the archive's supported platform accurately.

## Versioning policy

Follow Semantic Versioning:
- PATCH: compatible bug fixes.
- MINOR: backward-compatible features.
- MAJOR: breaking changes.
- PRERELEASE: optional testing versions such as `1.2.0-rc.1`.

The release tag and release title are both `<package-name>-v<version>`, for example `test-g-v1.0.0`. The version is represented by the tag and metadata; it is not added to the ZIP filename. Published versions and their release assets are immutable. Never reuse a version number, even for a corrected archive.

## Review and publication

Automated checks confirm metadata, paths, ZIP integrity, archive safety, and size limits. They cannot prove that a module is safe or correct. Maintainers must inspect the source and test the module in an isolated environment before approval.

The owner must approve the current Pull Request head commit. After that, run:

**Actions → Publish approved package → Run workflow → enter the Pull Request number.**

The workflow creates a GitHub Release containing:
- The original platform ZIP, retaining its version-independent filename.
- A SHA-256 checksum file with the same archive filename plus `.sha256`.

It stores `package.json` at `submissions/<package-name>/<version>/package.json` in the repository and updates `registry/index.json`. The metadata file is not duplicated as a release asset. The release tag identifies the package version. The registry's `latest` value is calculated using Semantic Versioning, not string sorting. Prereleases do not supersede a stable release.

## Registry consumers

The public catalogue is:

`https://raw.githubusercontent.com/MacoraOne/greenServeFE-community-packages/main/registry/index.json`

Each package entry lists every published version, its release tag, platform-specific download URL, checksum, metadata, and the latest version. Consumers should verify SHA-256 after downloading.

## Scope

Only community module submissions belong in this registry. Do not modify the repository's workflows, scripts, registry files, schemas, or policies in a package submission Pull Request.
