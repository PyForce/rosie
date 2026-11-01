# syntax=docker/dockerfile:1.7
# rosie with WebRosie: docker run -p 8080:8080 ghcr.io/pyforce/rosie, then open http://localhost:8080
# Arguments and ROSIE_* variables go to rosie start, for example your own robot:
#   docker run -p 8080:8080 -v ./my-robot:/robot ghcr.io/pyforce/rosie --robot-profile /robot
#
# WebRosie comes from its release zip. To build with a local WebRosie instead:
#   docker build --build-context webrosie=../WebRosie/dist .

ARG WEBROSIE_VERSION=2.1.0
# of webrosie-<version>.zip on its GitHub Release
ARG WEBROSIE_SHA256=581edf5471a9e0e791c347e01ddae8d987eefc5147c5885dad2c827edca6bfb5

FROM python:3.15-slim AS builder

# Pin uv; use a digest as well when your deployment requires immutable inputs.
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/

WORKDIR /app
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

# Resolve and install third-party dependencies in a cacheable layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,readonly \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,readonly \
    uv sync --locked --no-dev --extra robot --no-install-project --no-editable

COPY . /app

# Install the packaged application non-editably for deployment.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --extra robot --no-editable

FROM python:3.15-slim AS webrosie-release
ARG WEBROSIE_VERSION
ARG WEBROSIE_SHA256
RUN python - <<PYTHON
import hashlib, io, sys, urllib.request, zipfile
if not "${WEBROSIE_SHA256}":
    sys.exit("no WEBROSIE_SHA256: pass it, or a local WebRosie with --build-context webrosie=...")
url = "https://github.com/PyForce/WebRosie/releases/download/v${WEBROSIE_VERSION}/webrosie-${WEBROSIE_VERSION}.zip"
data = urllib.request.urlopen(url).read()
if hashlib.sha256(data).hexdigest() != "${WEBROSIE_SHA256}":
    sys.exit(f"{url} doesn't match WEBROSIE_SHA256")
zipfile.ZipFile(io.BytesIO(data)).extractall("/webrosie")
PYTHON

FROM scratch AS webrosie
COPY --from=webrosie-release /webrosie/ /

FROM python:3.15-slim

RUN apt-get update && \
    apt-get install --assume-yes --no-install-recommends nginx tini && \
    rm -rf /var/lib/apt/lists/* && \
    # dialout: serial ports (Arduino boards); for I2C add the host's group: --group-add $(getent group i2c | cut -d: -f3)
    useradd --uid 1000 --create-home --groups dialout rosie

COPY --from=builder /app/.venv /app/.venv
COPY --from=webrosie / /srv/webrosie
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/run.sh /usr/local/bin/rosie-container
ENV PATH="/app/.venv/bin:$PATH"

USER rosie
WORKDIR /home/rosie
EXPOSE 8080
# arguments of docker run go after rosie-container, to rosie start
ENTRYPOINT ["/usr/bin/tini", "--", "rosie-container"]
