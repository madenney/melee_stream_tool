#!/usr/bin/env python3
"""
Central knobs for your scripts.
Tweak REQUIRED_* and OPTIONAL_* as your setup evolves.
"""

# The config file lives next to the scripts
CONFIG_FILENAME = "config.json"

# Devices (resolved via init wizard to regexes stored in config.json)
REQUIRED_DEVICE_KEYS = [
    "mic",       # Audio/Source   (your voice input)
    "phones",    # Audio/Sink     (your monitoring headphones)
]

# Apps you may want running during verify (optional warnings only)
# These are matched against pactl application.name for sink-inputs/sources (best-effort).
OPTIONAL_APPS = [
    "Discord",
    "OBS",
    "Spotify",
    "Slippi",
]

# How long verify should wait (in seconds) after reset for devices to appear
VERIFY_DEVICE_WAIT_SECONDS = 2
