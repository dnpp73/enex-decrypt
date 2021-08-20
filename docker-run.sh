#!/usr/bin/env bash

set -Ceu

NAME='enex_decrypt'
IMAGE='enex-decrypt'

if ! docker image inspect "${IMAGE}" > /dev/null 2>&1 ; then
    echo "[ERROR] '${IMAGE}' image not found." 1>&2
    exit 1
fi

CURRENT_DIR=$(cd "$(dirname "${0}")" || exit 1; pwd)

docker container run -it --name "${NAME}" --rm \
-v "${CURRENT_DIR}:/work:ro" \
-v "${CURRENT_DIR}/output:/work/output:rw" \
"${IMAGE}":latest /bin/zsh
