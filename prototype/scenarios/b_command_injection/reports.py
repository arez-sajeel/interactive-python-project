import subprocess


def build_command(name):
    return f"echo Generating report {name}"


def generate_report(name):
    command = build_command(name)
    subprocess.run(command, shell=True, check=False)
