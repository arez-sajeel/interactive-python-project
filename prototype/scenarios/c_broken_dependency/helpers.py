import re


def title_to_slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def count_words(text):
    return len(text.split())
