import re
import subprocess

SAFE_NAME = re.compile(r"[A-Za-z0-9_-]+")


def build_command(name):
    if not SAFE_NAME.fullmatch(name):
        raise ValueError(f"Invalid report name: {name!r}")
    return f"echo Generating report {name}"


def generate_report(name):
    command = build_command(name)
    subprocess.run(command, shell=True, check=False)
