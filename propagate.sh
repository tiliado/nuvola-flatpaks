#!/bin/bash
set -euo pipefail

for manifest in eu.tiliado.NuvolaCdk.yml eu.tiliado.NuvolaAdk.yml; do
  source="experimental"

  for target in master stable; do
    set +e
    git diff manifests/$source/$manifest | patch -N manifests/$target/$manifest
    test $? -lt 2 || exit 1
    set -e
    source=$target
  done
done

