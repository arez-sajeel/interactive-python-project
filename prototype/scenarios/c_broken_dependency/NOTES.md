# Scenario C: notes

**Origin:** GPT-6 (ChatGPT), attempts 1 and 2 combined. See PROMPT.md.

**Defect category:** Broken dependency

**Occurred naturally:** no. Attempt 1 was correct, and in attempt 2 ChatGPT renamed
`slugify` to `title_to_slug` in both files. The defect was made by taking only the
renamed `helpers.py` from attempt 2 and keeping `main.py` from attempt 1, as if the
change had been applied to one file but not the other. This counts as injected.

**Defect:** `main.py` line 1 imports `slugify`, which `helpers.py` no longer defines, so the
program stops with an `ImportError`. ChatGPT's updated `main.py` from attempt 2 is in
`solution/main.py`.

**Observations from ChatGPT's output:**

- Attempt 1 stated the output as "9 words", but the sample body has 8 words and the code
  correctly prints `getting-started-with-python: 8 words`.
- Bandit: no findings.
- pylint: `title` and `body` in the `__main__` block shadow the parameters of `summarise`
  (W0621, twice), plus missing docstrings.

**Expected cross-file calls:**

1. `main.summarise` → `helpers.slugify` (not defined)
2. `main.summarise` → `helpers.count_words`
