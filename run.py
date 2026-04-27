#!/usr/bin/env python3
"""Applymize — Launcher"""
import subprocess, sys
from pathlib import Path

def main():
    app = Path(__file__).parent / "app.py"
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(app),
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "dark",
        "--theme.primaryColor", "#2563EB",
        "--theme.backgroundColor", "#080C16",
        "--theme.secondaryBackgroundColor", "#0F1524",
        "--theme.textColor", "#F1F5F9",
    ])

if __name__ == "__main__":
    main()
