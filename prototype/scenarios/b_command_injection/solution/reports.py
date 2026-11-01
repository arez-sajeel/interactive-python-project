import re
import subprocess

SAFE_NAME = re.compile(r"[A-Za-z0-9_-]+")


def generate_report(name):
    if not SAFE_NAME.fullmatch(name):
        raise ValueError(f"Invalid report name: {name!r}")
    subprocess.run(f"echo Generating report {name}", shell=True, check=True)
