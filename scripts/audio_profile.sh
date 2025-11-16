#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-}"

if [[ -z "$PROFILE" ]]; then
  cat <<EOF
Usage: $0 normal|tournament

Profiles:
  normal      Simple desktop mode (Arctis + UMC mic)
  tournament  Create tournament virtual sinks and set master mix

Debug helpers:
  # See sinks/sources
  wpctl status | sed -n '/Sinks:/,/Sources:/p'

  # See nodes with names and classes
  pw-cli ls Node | grep -E 'id [0-9]+, type PipeWire:Interface:Node|node.name =|media.class ='
EOF
  exit 1
fi

# ===== STABLE NODE NAMES (from wpctl / pw-cli) ============================
# Hardware you actually own:
ARCTIS_NODE_NAME="alsa_output.usb-SteelSeries_Arctis_Nova_7X-00.analog-stereo"
UMC_SOURCE_NODE_NAME="alsa_input.usb-BEHRINGER_UMC404HD_192k-00.analog-surround-40"

# Our two virtual sinks:
EVERYTHING_SINK_NAME="Tournament_Everything"
COMMENTARY_SINK_NAME="Tournament_Commentary"
# ==========================================================================

find_node_id_by_name() {
  local target="$1"
  pw-cli ls Node | awk -v target="$target" '
    /^[ \t]*id [0-9]+, type PipeWire:Interface:Node/ {
      gsub(",", "", $2);
      id = $2;
    }
    /node.name = "/ {
      match($0, /node.name = "([^"]+)"/, m);
      if (m[1] == target) {
        print id;
        exit;
      }
    }
  '
}

set_default_sink_by_node_name() {
  local node_name="$1"
  local label="$2"

  local id
  id="$(find_node_id_by_name "$node_name" || true)"

  if [[ -z "${id:-}" ]]; then
    echo "ERROR: Could not find sink node with name:"
    echo "  $node_name"
    echo "Run this to inspect nodes:"
    echo "  pw-cli ls Node | grep -E 'node.name =|media.class ='"
    exit 1
  fi

  echo "  → Setting default sink to node [$id] ($label)"
  wpctl set-default "$id"
}

set_default_source_by_node_name() {
  local node_name="$1"
  local label="$2"

  local id
  id="$(find_node_id_by_name "$node_name" || true)"

  if [[ -z "${id:-}" ]]; then
    echo "WARNING: Could not find source node with name:"
    echo "  $node_name"
    echo "Default source unchanged."
    return 0
  fi

  echo "  → Setting default source to node [$id] ($label)"
  wpctl set-default "$id"
}

# Create a null sink with a nice description so its monitor shows up as
# "Monitor of <desc>" in Discord / OBS / etc.
ensure_null_sink() {
  local sink_name="$1"
  local sink_desc="$2"

  # Does a Pulse sink with this name already exist?
  if pactl list short sinks 2>/dev/null | awk '{print $2}' | grep -qx "$sink_name"; then
    echo "  • Null sink '$sink_name' already exists"
    return 0
  fi

  echo "  • Creating null sink '$sink_name' ($sink_desc)"
  pactl load-module module-null-sink \
    sink_name="$sink_name" \
    sink_properties="device.description=$sink_desc" >/dev/null

  # Give PipeWire a moment to see it
  sleep 0.2
}

unload_null_sink() {
  local sink_name="$1"

  # Find any module-null-sink instances that created this sink
  local modules
  modules="$(pactl list short modules 2>/dev/null | awk -v name="$sink_name" '
    $2 == "module-null-sink" && $0 ~ ("sink_name=" name) { print $1 }
  ')"

  if [[ -z "${modules:-}" ]]; then
    # Nothing to unload
    return 0
  fi

  echo "  • Unloading null sink '$sink_name' (modules: $modules)"
  for m in $modules; do
    pactl unload-module "$m" || true
  done
}

case "$PROFILE" in
  normal)
    echo "=== NORMAL PROFILE ==="
    echo "Tearing down tournament virtual sinks and restoring simple routing:"

    # 1) Remove our tournament null sinks
    unload_null_sink "$EVERYTHING_SINK_NAME"
    unload_null_sink "$COMMENTARY_SINK_NAME"

    # 2) Restore defaults to real hardware
    echo "  - Default sink   = Arctis headset"
    echo "  - Default source = UMC404HD (desktop mic)"

    set_default_sink_by_node_name "$ARCTIS_NODE_NAME" "Arctis headset"
    set_default_source_by_node_name "$UMC_SOURCE_NODE_NAME" "UMC404HD desktop mic"
    ;;

  tournament)
    echo "=== TOURNAMENT PROFILE ==="
    echo "Setting up virtual sinks for tournament routing:"

    # 1) Make sure the two null sinks exist, with nice descriptions
    ensure_null_sink "$EVERYTHING_SINK_NAME"  "TE_Everything"
    ensure_null_sink "$COMMENTARY_SINK_NAME"  "TE_Commentary"

    echo
    echo "Setting defaults:"
    echo "  - Default sink  = $EVERYTHING_SINK_NAME (master 'everything' mix)"
    set_default_sink_by_node_name "$EVERYTHING_SINK_NAME" "$EVERYTHING_SINK_NAME"

    echo "  - Default source = UMC404HD mic (good default for main Discord / talk stuff)"
    set_default_source_by_node_name "$UMC_SOURCE_NODE_NAME" "UMC404HD desktop mic"
    echo

    cat <<EOF
Tournament wiring plan (matches how you're actually using things):

Virtual sinks created:
  • $EVERYTHING_SINK_NAME
      - "Tournament Everything"
      - Holds ALL playback: game audio, music, Discord outputs, etc.
      - Monitor appears as: "Monitor of Tournament Everything"
  • $COMMENTARY_SINK_NAME
      - "Tournament Commentary"
      - Holds ONLY commentators' voices (both you + co-casters)
      - Monitor appears as: "Monitor of Tournament Commentary"

How to wire (manual):

1) Headset monitoring (what YOU hear)
   - In qpwgraph:
       Monitor of Tournament Everything  -->  $ARCTIS_NODE_NAME
   - Now your Arctis hears the full mix.

2) Stream bot Discord (acct-1 via launch.sh)
   - This is the one you start with:
       ~/Projects/discord_swap/launch.sh 1
   - In that Discord's Voice & Video settings:
       • INPUT device  = "Monitor of Tournament Everything"
            → It sends game + music (and whatever else you route into Everything)
       • OUTPUT device = "Tournament Commentary"
            → Its output (commentary from remote casters) goes into the Commentary sink.

3) Your normal everyday Discord (non-launch.sh)
   - Use your normal profile / normal app.
   - Voice & Video:
       • INPUT device  = "UMC404HD 192k Analog Surround 4.0"
            → Your desktop mic (you as commentator)
       • OUTPUT device = "Tournament Everything"
            → So you also hear everything through the master mix.

4) OBS setup
   - Add an Audio Input Capture in OBS whose device is:
       "Monitor of Tournament Commentary"
     This becomes your "Commentary" audio track in OBS.
   - For game/music, either:
       a) Capture it via the same PipeWire audio device
          (Monitor of Tournament Everything) as a separate source, OR
       b) Let it come via the stream audio you're already feeding.

5) Going back to normal life:
   - Run:
       ./audio_profile.sh normal
   - This:
       • Tears down Tournament_Everything + Tournament_Commentary
       • Resets default sink to Arctis
       • Resets default source to UMC mic

Debug tip:
  - To see the sinks/sources/monitors:
      wpctl status | sed -n '/Sinks:/,/Sources:/p'
  - To see node names and classes:
      pw-cli ls Node | grep -E 'id [0-9]+, type PipeWire:Interface:Node|node.name =|media.class ='

EOF
    ;;

  *)
    echo "Unknown profile: $PROFILE (use: normal | tournament)"
    exit 1
    ;;
esac

echo
echo "Current defaults:"
wpctl status | sed -n '/Default Configured Node Names/,$p'
