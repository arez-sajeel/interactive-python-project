import subprocess


def generate_report(name):
    subprocess.run(f"echo Generating report {name}", shell=True, check=True)
