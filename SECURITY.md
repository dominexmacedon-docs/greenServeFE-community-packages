# Security policy

## Reporting vulnerabilities

Do not publish exploitable vulnerabilities, credentials, private keys, access tokens, or personal data in a Pull Request or issue. Contact the repository owner privately through GitHub's available private contact channel.

## Untrusted submissions

All submitted ZIP files and their contents are untrusted until reviewed. Automated validation checks archive structure and metadata only. It never imports, builds, installs, or executes submitted code.

Maintainers should inspect source files and test modules in an isolated environment without production credentials, sensitive files, or privileged host access. Review native binaries as carefully as source code.

## Release integrity

Every published ZIP has a SHA-256 checksum attached to its GitHub Release and recorded in the registry. Consumers should verify the checksum before installation. Published versions are immutable; fixes require a new version.
