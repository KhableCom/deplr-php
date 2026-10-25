# deplr-php

PHP FPM base images for [Deplr](https://github.com/KhableCom/deplr)'s Laravel build recipe (Deplr ADR 0095).

```
ghcr.io/khablecom/deplr-php:<line>-fpm-<extension set>    e.g. 8.5-fpm-laravel
```

Each image is a pinned [serversideup/php](https://github.com/serversideup/docker-php) FPM image plus the extensions of its set, checked with `php -m`. Nothing else: no Node, no app code, no configuration. Images are multi-architecture (amd64 and arm64), carry an SBOM and provenance, and each index is signed with cosign (keyless).

## What is here

- `php/Dockerfile`: the base image.
- `catalog.json`: the PHP lines, their upstream images (pinned by digest) and the extension sets. Same format as `infra/build/catalog.json` in Deplr.
- `scripts/record-digests.py`: writes published digests into the catalog.
- `.github/workflows/build.yml`: builds on every pull request (pushes nothing); a manual run on `main` with **push** publishes, signs, and prints the catalog with the new digests.

## Publishing

1. Change `catalog.json` in a pull request (new upstream tag and digest, `digest` back to `null`, raise `version`). Merge it.
2. **Actions > Build > Run workflow** on `main` with **push** ticked.
3. Copy the catalog from the run summary (or its `catalog` artifact) into Deplr as `infra/build/catalog.json`, review it, and merge. Deplr only uses an image once its digest is committed there.

Verify a signature:

```sh
cosign verify ghcr.io/khablecom/deplr-php@sha256:<digest> \
  --certificate-identity-regexp '^https://github.com/KhableCom/deplr-php/\.github/workflows/build\.yml@refs/heads/main$' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

## Security

Builds run on Blacksmith runners (a fresh VM per job, billed to the KhableCom workspace). This repository holds no secrets: publishing uses the run's own `GITHUB_TOKEN`. Pull requests, including from forks, only build. Never point this workflow at a self-hosted runner.

License: AGPL-3.0-only, like Deplr.
