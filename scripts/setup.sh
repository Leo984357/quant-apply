#!/usr/bin/env python3
import subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def check_deps():
    missing = []
    for cmd in ["boss", "jobclaw", "python3"]:
        if not subprocess.run(["which", cmd], capture_output=True).returncode == 0:
            missing.append(cmd)
    return missing

def install_boss_agent():
    print("[*] Installing boss-agent-cli...")
    subprocess.run([sys.executable, "-m", "pip", "install", "boss-agent-cli"], check=True)

def install_jobclaw():
    print("[*] Installing jobclaw...")
    os.chdir(ROOT / "tools" / "jobclaw")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    subrun(["pip", "install", "-e", "."])

def install_autoapply():
    print("[*] Setting up AutoApply...")
    os.chdir(ROOT / "tools" / "AutoApply")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    subprocess.run([sys.executable, "setup_env.py"], check=True)
    subprocess.run(["playwright", "install", "chromium"], check=True)

def setup():
    print("=== Quant-Apply Setup ===")
    print("[*] Creating venv...")
    subprocess.run([sys.executable, "-m", "venv", str(ROOT / "venv")], check=True)
    pip = str(ROOT / "venv" / "bin" / "pip")
    subprocess.run([pip, "install", "-r", str(ROOT / "requirements.txt")], check=True)
    print("\n[✓] Done. Next: edit config/profile.yaml and config/search.yaml")
    print("    Then run: python src/cli.py")

if __name__ == "__main__":
    setup()
