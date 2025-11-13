#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

# Local imports
from reset_audio import reset_audio
import verify_config
import apply_audio_profile
import init_audio_profile
from script_config import CONFIG_FILENAME

SCRIPT_DIR = Path(__file__).resolve().parent
CFG_PATH = SCRIPT_DIR / CONFIG_FILENAME

def ensure_config(force_init: bool) -> None:
    """
    Ensures config.json exists. If -i passed or file missing, run the init wizard.
    """
    if force_init or not CFG_PATH.exists():
        print("[main] Running interactive config initializer…")
        init_audio_profile.main()  # writes config.json next to scripts
        if not CFG_PATH.exists():
            print("[main] ERROR: init completed but no config.json found.")
            sys.exit(2)

def main():
    parser = argparse.ArgumentParser(description="Audio setup orchestrator")
    parser.add_argument("-i", "--init", action="store_true",
                        help="Run the init wizard before continuing.")
    parser.add_argument("--no-reset", action="store_true",
                        help="Skip resetting PipeWire (advanced).")
    args = parser.parse_args()

    # 1) Reset audio (unless skipped)
    if not args.no_reset:
        print("[main] Resetting PipeWire…")
        reset_audio()

    # 2) Ensure config exists (or run init if requested)
    ensure_config(force_init=args.init)

    # 3) Verify config (devices + optional app warnings)
    print("[main] Verifying config.json…")
    ok, issues, warnings = verify_config.verify(SCRIPT_DIR)

    if warnings:
        print("\n[main] WARNINGS:")
        for w in warnings:
            print("  -", w)

    if not ok:
        print("\n[main] Config is INVALID:")
        for i in issues:
            print("  -", i)
        print("\n[main] Launch any missing apps (if applicable), then the init wizard will run again.")
        init_audio_profile.main()
        print("[main] Re-verifying…")
        ok, issues, warnings = verify_config.verify(SCRIPT_DIR)
        if not ok:
            print("\n[main] Still invalid. Exiting so you can fix hardware/app state.")
            sys.exit(3)

    # 4) Apply profile (currently: mic → headphones)
    print("\n[main] Applying profile…")
    apply_audio_profile.apply_profile(SCRIPT_DIR)

    print("\n[main] ✅ Done.")

if __name__ == "__main__":
    main()
