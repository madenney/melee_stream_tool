#!/usr/bin/env python3
import json, re, subprocess, sys, time
from pathlib import Path
from typing import List, Optional, Tuple

def sh(cmd, check=True):
    return subprocess.run(cmd, check=check, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def pw_ports(section: str) -> List[str]:
    out = sh(["pw-link", "-l"]).splitlines()
    collecting = False; ports=[]
    for ln in out:
        s = ln.strip()
        if s == "outputs:": collecting = (section == "outputs"); continue
        if s == "inputs:":  collecting = (section == "inputs");  continue
        if collecting and ":" in s: ports.append(s)
    return ports

def ports_by_node_regex(section: str, node_regex: str) -> List[Tuple[str,str]]:
    nre = re.compile(node_regex or ".*")
    out = []
    for p in pw_ports(section):
        node, suffix = p.rsplit(":", 1)
        if nre.search(node):
            out.append((node, suffix))
    return out

def pick_best_port(ports: List[Tuple[str,str]], preferred: List[str]) -> Optional[str]:
    # exact matches first
    for want in preferred:
        for node, suf in ports:
            if suf == want:
                return f"{node}:{suf}"
    # prefix wildcards (like capture_*, playback_*)
    for want in preferred:
        if want.endswith("*"):
            pref = want[:-1]
            for node, suf in ports:
                if suf.startswith(pref):
                    return f"{node}:{suf}"
    # fallback: first available
    if ports:
        node, suf = ports[0]
        return f"{node}:{suf}"
    return None

def connect(a: str, b: str):
    subprocess.run(["pw-link", a, b], check=False)

def apply_profile(script_dir: Path):
    cfg_path = script_dir / "config.json"
    if not cfg_path.exists():
        print("[apply] Missing config.json next to scripts.")
        sys.exit(1)
    cfg = json.loads(cfg_path.read_text())

    # give PipeWire a moment if we just reset
    time.sleep(1.5)

    mic_rx = cfg["mic"]["nick_regex"] or cfg["mic"]["name_regex"] or ".*"
    hp_rx  = cfg["phones"]["nick_regex"] or cfg["phones"]["name_regex"] or ".*"

    mic_ports = ports_by_node_regex("outputs", mic_rx)
    hp_ports  = ports_by_node_regex("inputs",  hp_rx)

    mic_preference = [
        "capture_FL", "capture_MONO",
        "input_FL", "input_1", "input_MONO",
        "capture_*", "input_*"
    ]
    hp_preference  = [
        "playback_FL", "playback_MONO",
        "output_FL", "output_1",
        "playback_*", "output_*"
    ]

    mic_out = pick_best_port(mic_ports, mic_preference)
    hp_in   = pick_best_port(hp_ports,  hp_preference)

    if not mic_out:
        print("[apply] Couldn’t resolve MIC port. Re-run init or check device is connected.")
        sys.exit(2)
    if not hp_in:
        print("[apply] Couldn’t resolve HEADPHONES port. Re-run init or check device is connected.")
        sys.exit(3)

    print(f"[apply] Linking {mic_out}  →  {hp_in}")
    connect(mic_out, hp_in)

if __name__ == "__main__":
    apply_profile(Path(__file__).resolve().parent)
