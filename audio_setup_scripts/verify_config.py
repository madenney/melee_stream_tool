#!/usr/bin/env python3
import json, re, subprocess, time
from pathlib import Path
from typing import Tuple, List
from script_config import CONFIG_FILENAME, REQUIRED_DEVICE_KEYS, OPTIONAL_APPS, VERIFY_DEVICE_WAIT_SECONDS

def sh(cmd, check=True):
    return subprocess.run(cmd, check=check, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def pw_ports(section: str) -> List[str]:
    """
    Return lines like 'Node Nick:port_suffix' from pw-link -l for outputs or inputs.
    """
    out = sh(["pw-link", "-l"]).splitlines()
    collecting = False
    ports = []
    for ln in out:
        s = ln.strip()
        if s == "outputs:":
            collecting = (section == "outputs"); continue
        if s == "inputs:":
            collecting = (section == "inputs"); continue
        if collecting and ":" in s:
            ports.append(s)
    return ports

def node_exists_by_regex(section: str, node_regex: str) -> bool:
    """
    True if any port in the section belongs to a node matching regex.
    """
    nre = re.compile(node_regex or ".*")
    for p in pw_ports(section):
        node = p.rsplit(":", 1)[0]
        if nre.search(node):
            return True
    return False

def any_sink_input_app_matches(regex_str: str) -> bool:
    rx = re.compile(regex_str or r"^Discord$")
    full = sh(["pactl", "list", "sink-inputs"])
    for block in full.split("Sink Input #")[1:]:
        for ln in block.splitlines():
            if "application.name" in ln:
                app = ln.split("=", 1)[1].strip().strip('"')
                if rx.search(app):
                    return True
    return False

def verify(script_dir: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Returns (ok, issues, warnings).
    - issues: config invalid (blocking)
    - warnings: advisory (e.g., optional apps not running yet)
    """
    cfg_path = script_dir / CONFIG_FILENAME
    issues, warnings = [], []

    if not cfg_path.exists():
        issues.append(f"Missing {cfg_path.name}.")
        return False, issues, warnings

    cfg = json.loads(cfg_path.read_text())
    # Give PipeWire a moment (in case we just reset)
    time.sleep(VERIFY_DEVICE_WAIT_SECONDS)

    # Check mic device exists in outputs
    mic_rx = cfg.get("mic", {}).get("nick_regex") or cfg.get("mic", {}).get("name_regex") or ""
    if mic_rx:
        if not node_exists_by_regex("outputs", mic_rx):
            issues.append(f"Mic device not found (regex: {mic_rx}). Open pavucontrol and confirm device is present.")
    else:
        issues.append("Mic not configured in config.json.")

    # Check headphones device exists in inputs
    hp_rx = cfg.get("phones", {}).get("nick_regex") or cfg.get("phones", {}).get("name_regex") or ""
    if hp_rx:
        if not node_exists_by_regex("inputs", hp_rx):
            issues.append(f"Headphones/Sink not found (regex: {hp_rx}). Make sure your output device is connected and active.")
    else:
        issues.append("Headphones not configured in config.json.")

    # App warnings (optional)
    for app in OPTIONAL_APPS:
        # We only warn if the app is listed in OPTIONAL_APPS; exact regex is app name
        if not any_sink_input_app_matches(rf"^{re.escape(app)}$"):
            warnings.append(f"App not detected yet: {app}. If needed for routing, start it before applying the profile.")

    return (len(issues) == 0), issues, warnings

if __name__ == "__main__":
    ok, issues, warnings = verify(Path(__file__).resolve().parent)
    print("OK?" , ok)
    if issues:
        print("Issues:")
        for i in issues: print("  -", i)
    if warnings:
        print("Warnings:")
        for w in warnings: print("  -", w)
