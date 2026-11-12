# greenServeFE Community Packages

A reviewed release registry for community-built greenServeFE modules.

## Release naming

Community releases follow the same naming convention as the official greenServeFE module releases:

- **Release tag:** `<package-name>-v<version>` (for example, `test-g-v1.0.0`)
- **Release title:** `<package-name>-v<version>` (for example, `test-g-v1.0.0`)
- **ZIP asset:** `<package-name>-<platform>.zip` (for example, `test-g-linux-x86_64.zip`)

The ZIP filename does **not** contain the version. The release tag and `package.json` identify the version. The ZIP keeps its platform-specific name, just like the official greenServeFE module releases.

## Submit a module

For review, submit exactly these two files in the Pull Request:

```text
submissions/
└── test-g/
    └── 1.0.0/
        ├── package.json
        └── test-g-linux-x86_64.zip
```

The ZIP contains the module files, for example `test-g.so`. Do not upload the shared library separately. The ZIP is used by the publishing workflow and is not retained in the repository's `main` branch. After publication, only `package.json` remains in the version directory; the ZIP is attached to the GitHub Release.

See [CONTRIBUTING.md](CONTRIBUTING.md) for metadata requirements, archive limits, review, and publication instructions.

## Registry catalogue

`https://raw.githubusercontent.com/MacoraOne/greenServeFE-community-packages/main/registry/index.json`
