import helpers


def summarise(title, body):
    words = helpers.word_count(body)
    slug = helpers.make_slug(title)
    return f"{slug}: {words} words"


def main():
    print(summarise("Hello World", "One two three"))


if __name__ == "__main__":
    main()
