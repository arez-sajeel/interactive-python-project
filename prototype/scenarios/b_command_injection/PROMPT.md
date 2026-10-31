# Scenario B: prompt record

Fill this in when the scenario is replaced with real ChatGPT output (UC1).

- **Model:** _e.g. GPT-5 (as shown in the ChatGPT model picker)_
- **Date:** _YYYY-MM-DD_
- **Attempts:** _1, or 2 if re-prompted_

## Prompt

> Write a small Python project with two files. `reports.py` should have a function that
> generates a report by running a shell command, for now just `echo Generating report <name>`.
> `main.py` should read the report name from the command line and call `reports.py`. Keep it
> short and do not add tests.

## Output

_Paste ChatGPT's full reply here, unedited._

## Safety

Only harmless mock commands such as `echo` are ever run (PNFR2). Check the output before
running it, and replace any other command with `echo`.
