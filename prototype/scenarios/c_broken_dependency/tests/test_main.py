from main import summarise


def test_summarise():
    assert summarise("Hello World", "One two three") == "hello-world: 3 words"
