from helpers import slugify, count_words


def summarise(title, body):
    return f"{slugify(title)}: {count_words(body)} words"


if __name__ == "__main__":
    title = "Getting Started with Python"
    body = "Python is a simple and versatile programming language."
    print(summarise(title, body))
