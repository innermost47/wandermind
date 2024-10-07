import re


def split_text_on_punctuation(text):
    return re.split(r"([.!?:,;])", text)
