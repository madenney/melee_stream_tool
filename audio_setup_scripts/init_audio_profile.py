#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
from typing import List, Dict
from script_config import CONFIG_FILENAME

SCRIPT_DIR = Path(__file__).resolve().parent
CFG_PATH = SCRIPT_DIR / CONFIG_FILENAME

def sh(cmd: List[str]) -> str:
    return subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE).stdout

def load_nodes() -> List[Dict]:
    # PipeWire JSON dump (nodes only)
    out = sh(["pw-dump", "-N"])
    return json.loads(out)

def list_candidates(nodes, media_class_prefix: str):
    items = []
    for n in nodes:
        props = n.get("info", {}).get("props", {})
        mclass = props.get("media.class", "")
        if mclass.startswith(media_class_prefix):
            items.append({
                "id": n.get("id"),
                "name": props.get("node.name", ""),
                "nick": props.get("node.nick", ""),
                "class": mclass
            })
    return items

def pick(label: str, items: List[Dict]):
    print(f"\nSelect {label}:")
    for i, it in enumerate(items, 1):
        shown = it['nick'] or it['name'] or f"node#{it['id']}"
        print(f"  [{i}] {shown}  ({it['class']})")
    while True:
        s = input(f"Enter number for {label} (or blank to skip): ").strip()
        if not s:
            return None
        if s.isdigit() and 1 <= int(s) <= len(items):
            return items[int(s) - 1]
        print("Invalid choice.")

def main():
    nodes = load_nodes()
    sources = list_candidates(nodes, "Audio/Source")
    sinks   = list_candidates(nodes, "Audio/Sink")

    mic = pick("MIC (Audio/Source)", sources)
    phones = pick("HEADPHONES (Audio/Sink)", sinks)

    # App name regex for Discord (optional at this stage)
    discord_rx = input("\nRegex for Discord application.name (default: ^Discord$): ").strip() or r"^Discord$"

    cfg = {
        "mic": {
            "nick_regex": (mic or {}).get("nick", ""),
            "name_regex": (mic or {}).get("name", ""),
            "port": "capture_FL"  # best-effort default; apply script will auto-pick anyway
        },
        "phones": {
            "nick_regex": (phones or {}).get("nick", ""),
            "name_regex": (phones or {}).get("name", ""),
            "port": "playback_FL"
        },
        "discord": {"app_regex": discord_rx},
        "version": 1
    }

    CFG_PATH.write_text(json.dumps(cfg, indent=2))
    print(f"\nSaved {CFG_PATH}\n")

if __name__ == "__main__":
    main()
