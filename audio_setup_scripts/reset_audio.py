#!/usr/bin/env python3
import subprocess
import time

def reset_audio():
    """
    Restart PipeWire and Pulse shim cleanly.
    """
    subprocess.run(["systemctl", "--user", "restart", "pipewire", "pipewire-pulse"], check=True)
    time.sleep(2)
