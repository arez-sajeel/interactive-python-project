from helpers import title_to_slug, count_words


def summarise(title, body):
    return f"{title_to_slug(title)}: {count_words(body)} words"


if __name__ == "__main__":
    title = "Getting Started with Python"
    body = "Python is a simple and versatile programming language."
    print(summarise(title, body))
