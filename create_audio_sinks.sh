#!/usr/bin/env bash
set -euo pipefail

########################################
# EDITABLE CONFIG
########################################
# List of sink names you want to create
SINKS=(
  "Discord"
  "Slippi Audio"
)

# If a sink with the same name exists, should we unload + recreate it?
OVERWRITE=true

# Optional: make a persistent PipeWire config (user scope)
# If true and you run: ./sinks.sh persist
PERSIST_PATH="${HOME}/.config/pipewire/pipewire.conf.d/virtual-sinks.conf"
########################################

# --- helpers ---
log() { echo "[sinks] $*"; }
err() { echo "[sinks][ERR] $*" >&2; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { err "Missing required command: $1"; exit 1; }
}

# Returns module id for a null sink with a given node.name (sink_name)
get_module_id_by_sink_name() {
  # Works with PulseAudio-on-PipeWire as well
  pactl list short modules 2>/dev/null \
    | awk -v name="$1" '
        $0 ~ /module-null-sink/ && $0 ~ ("sink_name=" name) { print $1 }'
}

# Returns 0 if sink exists, 1 otherwise
sink_exists() {
  local name="$1"
  # Look for a sink or a monitor sink containing that name
  pactl list short sinks 2>/dev/null | awk '{print $2}' | grep -Fxq "$name" && return 0
  pactl list short sinks 2>/dev/null | awk '{print $2}' | grep -Fq "${name}.monitor" && return 0
  # Some setups show only the monitor; also try listing nodes via pw-cli if present
  if command -v pw-cli >/dev/null 2>&1; then
    pw-cli ls Node 2>/dev/null | grep -Fq "node.name = \"$name\"" && return 0
  fi
  return 1
}

load_sink() {
  local name="$1"
  # Overwrite existing?
  if sink_exists "$name"; then
    if [[ "$OVERWRITE" == "true" ]]; then
      log "Sink '$name' exists → unloading for clean recreate"
      unload_sink "$name" || true
    else
      log "Sink '$name' already exists → leaving as-is"
      return 0
    fi
  fi

  log "Creating sink '$name'"
  pactl load-module module-null-sink sink_name="$name" sink_properties="device.description=$name" >/dev/null
}

unload_sink() {
  local name="$1"
  local mod_id
  mod_id="$(get_module_id_by_sink_name "$name" || true)"
  if [[ -n "${mod_id:-}" ]]; then
    log "Unloading sink '$name' (module $mod_id)"
    pactl unload-module "$mod_id" >/dev/null || true
  else
    log "No module found for '$name' (already gone?)"
  fi
}

persist_write() {
  mkdir -p "$(dirname "$PERSIST_PATH")"
  log "Writing persistent PipeWire config: $PERSIST_PATH"
  {
    echo "context.modules = ["
    for name in "${SINKS[@]}"; do
      cat <<EOF
  { name = libpipewire-module-null-sink
    args = {
      node.name = "$name"
      node.description = "$name"
    }
  },
EOF
    done
    echo "]"
  } > "$PERSIST_PATH"

  log "Restarting PipeWire to apply (you can also reboot)"
  systemctl --user restart pipewire || true
}

usage() {
  cat <<EOF
Usage: $0 [command]

Commands:
  create     Create sinks defined in the SINKS array (default)
  unload     Unload/remove those sinks
  recreate   Unload then create
  persist    Write a PipeWire config to auto-create sinks on login (and restart PipeWire)
  status     Show matching sinks/modules

Examples:
  $0
  $0 create
  $0 unload
  $0 persist
EOF
}

status() {
  echo "=== pactl sinks ==="
  pactl list short sinks | grep -E "$(printf '%s|' "${SINKS[@]}")" || true
  echo
  echo "=== pactl modules (null-sink) ==="
  pactl list short modules | grep module-null-sink || true
  if command -v pw-cli >/dev/null 2>&1; then
    echo
    echo "=== pw-cli nodes ==="
    pw-cli ls Node | awk '/^ *id/ {id=$2} /node.name =/ {print "id=" id, $0}' | grep -E "$(printf '%s|' "${SINKS[@]}")" || true
  fi
}

main() {
  require_cmd pactl
  local cmd="${1:-create}"

  case "$cmd" in
    create|"")
      for s in "${SINKS[@]}"; do load_sink "$s"; done
      ;;
    unload)
      for s in "${SINKS[@]}"; do unload_sink "$s"; done
      ;;
    recreate)
      for s in "${SINKS[@]}"; do unload_sink "$s"; done
      for s in "${SINKS[@]}"; do load_sink "$s"; done
      ;;
    persist)
      persist_write
      ;;
    status)
      status
      ;;
    *)
      usage; exit 1 ;;
  esac

  log "Done."
}

main "$@"
