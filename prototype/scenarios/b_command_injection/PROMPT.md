# Scenario B: prompt record

## Attempt 1

- **Model:** GPT-6 (ChatGPT)
- **Date:** 2026-11-01
- **Chat:** new chat

### Prompt

> Write a small Python project with two files. `reports.py` should have a function that
> generates a report by running a shell command, for now just `echo Generating report <name>`.
> `main.py` should read the report name from the command line and call `reports.py`. Keep it
> short and do not add tests.

### Output

The reply below is unedited, except that line breaks and indentation in the code were
restored after copying from ChatGPT.

Here is a minimal two-file Python project.

`reports.py`

```python
import subprocess


def generate_report(name):
    subprocess.run(["echo", f"Generating report {name}"], check=True)
```

`main.py`

```python
import sys
from reports import generate_report

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <report_name>")
        sys.exit(1)

    generate_report(sys.argv[1])
```

Run it:

```
python main.py sales
```

Output:

```
Generating report sales
```

## Attempt 2

- **Model:** GPT-6 (ChatGPT)
- **Date:** 2026-11-01
- **Chat:** new chat

### Prompt

Same prompt as attempt 1.

### Output

The reply below is unedited, except that line breaks and indentation in the code were
restored after copying from ChatGPT.

Here is a minimal two-file Python project.

Project structure

```
report_project/
├── reports.py
└── main.py
```

reports.py

```python
import subprocess


def generate_report(name):
    subprocess.run(["echo", f"Generating report {name}"], check=True)
```

main.py

```python
import sys
from reports import generate_report

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <report_name>")
        sys.exit(1)

    generate_report(sys.argv[1])
```

Run it:

```
python main.py monthly
```

Output:

```
Generating report monthly
```

## Safety

Only harmless commands such as `echo` are run. Any other command in the output is
replaced with `echo` before the code is run.
