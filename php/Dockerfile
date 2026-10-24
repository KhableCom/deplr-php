# syntax=docker/dockerfile:1.10
# Deplr PHP base image: deplr/php:<line>-fpm-<extension set> (ADR 0095).
#
# Built by .github/workflows/build.yml, natively for amd64 and arm64, from
# the upstream serversideup FPM image pinned by digest. The workflow reads
# the line, the upstream reference and the extension list from catalog.json
# and passes them as build arguments:
#
#   docker buildx build php \
#     --build-arg UPSTREAM=serversideup/php:8.4-fpm-trixie-v5.0.2@sha256:<digest> \
#     --build-arg EXTENSIONS="bcmath exif gd intl" \
#     --build-arg EXPECTED="<every extension of the set>"
#
# Project builds never compile PHP or extensions: they start FROM this image.
# It adds nothing else: no Node, no application code, no configuration.

# The default is the PHP 8.5 entry of the catalog; CI always passes it.
ARG UPSTREAM=serversideup/php:8.5-fpm-trixie-v5.0.2@sha256:9d09d987b9a167ac494371e4ba1843d8f0006f859455f5a1d1b60cd9825b3bc0
FROM ${UPSTREAM}

ARG EXTENSIONS
ARG EXPECTED

USER root

# install-php-extensions ships with the serversideup image and removes its
# build dependencies when it finishes. php -m must then list every extension
# of the set. The recipe's vendor stage installs into /app as www-data.
RUN set -eu; \
    if [ -z "${EXTENSIONS}" ] || [ -z "${EXPECTED}" ]; then \
      echo "EXTENSIONS and EXPECTED are required build arguments" >&2; exit 1; \
    fi; \
    install-php-extensions ${EXTENSIONS}; \
    loaded="$(php -m | tr 'A-Z' 'a-z' | sed 's/^zend opcache$/opcache/')"; \
    missing=""; \
    for extension in ${EXPECTED}; do \
      printf '%s\n' "$loaded" | grep -qx "$extension" || missing="$missing $extension"; \
    done; \
    if [ -n "$missing" ]; then echo "extensions not loaded:$missing" >&2; exit 1; fi; \
    install -d -o www-data -g www-data /app; \
    chown www-data:www-data /var/www/html

USER www-data
LABEL org.opencontainers.image.title="deplr-php" \
      org.opencontainers.image.source="https://github.com/kongpda/deplr-php" \
      org.opencontainers.image.description="Deplr PHP FPM base for the Laravel build recipe" \
      org.opencontainers.image.licenses="AGPL-3.0-only"
