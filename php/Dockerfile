# syntax=docker/dockerfile:1.10
# Deplr PHP base image: deplr/php:<line>-fpm-<extension set> (ADR 0095).
#
# Built by .github/workflows/build.yml, natively for amd64 and arm64, from
# the upstream serversideup FPM image pinned by digest. The workflow reads
# the line, the upstream reference and the extension list from catalog.json
# and passes them as build arguments:
#
#   docker buildx build php \
#     --build-arg UPSTREAM=serversideup/php:8.4-fpm-trixie-v5.0.3@sha256:<digest> \
#     --build-arg EXTENSIONS="bcmath exif gd intl" \
#     --build-arg EXPECTED="<every extension of the set>"
#
# Project builds never compile PHP or extensions: they start FROM this image.
# It adds one PHP setting (below) and nothing else: no Node, no application
# code.

# The default is the PHP 8.5 entry of the catalog; CI always passes it.
ARG UPSTREAM=serversideup/php:8.5-fpm-trixie-v5.0.3@sha256:65676b31e690fd0718ea68d92c34167e1b71c54ab67a9930eacc01af1263b70e
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

# Session upload progress stays off whatever the environment says
# (CVE-2026-115560, and the known abuse of CVE-2026-109618/109619). The
# upstream image turns it off through PHP_SESSION_UPLOAD_PROGRESS_ENABLED,
# which an app's environment could set back; this file loads after it. It
# must be in php.ini, not ini_set() or .user.ini: PHP reads it before the
# request body. The build fails if it is not in force.
COPY --chmod=0644 zz-deplr-security.ini /usr/local/etc/php/conf.d/zz-deplr-security.ini
RUN set -eu; \
    value="$(PHP_SESSION_UPLOAD_PROGRESS_ENABLED=1 php -r 'echo var_export(ini_get("session.upload_progress.enabled"), true);')"; \
    if [ "$value" != "''" ] && [ "$value" != "'0'" ]; then \
      echo "session.upload_progress.enabled is $value, expected off" >&2; exit 1; \
    fi

USER www-data
LABEL org.opencontainers.image.title="deplr-php" \
      org.opencontainers.image.source="https://github.com/KhableCom/deplr-php" \
      org.opencontainers.image.description="Deplr PHP FPM base for the Laravel build recipe" \
      org.opencontainers.image.licenses="AGPL-3.0-only"
