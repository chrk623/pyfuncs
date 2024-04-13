import re
import string


def sentence_split(text):
    return re.split(r"(?<=[^A-Z].[.?]) +(?=[A-Z])", text)


def remove_punct(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def word_in_text(text, words):
    if isinstance(words, string):
        words = [words]
    for _text in text.lower().split():
        if _text in words:
            return True
    return False
