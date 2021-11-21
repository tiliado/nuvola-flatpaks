#!/bin/bash
set -euo pipefail

for manifest in eu.tiliado.NuvolaCdk.yml eu.tiliado.NuvolaAdk.yml eu.tiliado.NuvolaBase.yml eu.tiliado.NuvolaApp.yml; do
  source="experimental"

  for target in master stable; do
    if [ -f manifests/$source/$manifest ]; then
      set +e
      git diff manifests/$source/$manifest | patch -N manifests/$target/$manifest
      test $? -lt 2 || exit 1
      set -e
    else
      echo skip manifests/$source/$manifest - not found
    fi
    source=$target
  done
done

