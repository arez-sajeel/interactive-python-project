def slugify(text):
    return "-".join(text.lower().split())


def word_count(text):
    return len(text.split())
