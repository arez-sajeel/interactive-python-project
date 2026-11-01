from main import summarise


def test_summarise():
    assert summarise("Hello World", "One two three") == "hello-world: 3 words"


def test_summarise_strips_punctuation():
    assert summarise("Getting Started with Python!", "a b") == "getting-started-with-python: 2 words"
