#!/usr/bin/env bash
set -euo pipefail

echo "================== wpctl status (summary) =================="
wpctl status

echo
echo "================== pw-link -l (links) ======================"
pw-link -l || echo "pw-link not available? (pipewire-utils not installed?)"

echo
echo "================== pw-cli ls Node (filtered) ==============="
# Show each node's id, class, name, description (enough to identify apps/devices)
pw-cli ls Node | grep -E \
  'id [0-9]+, type PipeWire:Interface:Node|node.name =|node.description =|media.class ='
