# Scenario B: prompt record

- **Model:** not yet generated
- **Date:** not yet generated
- **Attempts:** not yet generated

## Prompt

> Write a small Python project with two files. `reports.py` should have a function that
> generates a report by running a shell command, for now just `echo Generating report <name>`.
> `main.py` should read the report name from the command line and call `reports.py`. Keep it
> short and do not add tests.

## Output

Not yet generated.

## Safety

Only harmless commands such as `echo` are run. Any other command in the output is
replaced with `echo` before the code is run.
