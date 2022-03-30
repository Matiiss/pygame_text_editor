"""A module containing TextData class for storing text data, along with text colors."""
import itertools
import re

from .sample_color_config import dct


class TextData:
    word_split = re.compile(r'\w+|[.\[\]{}]')

    def __init__(
            self,
            text: str = '',
            default_color: tuple[int, int, int] = (255, 255, 255),
            color_config: dict | None = dct
    ):
        text_rows = text.splitlines()
        self.data = []
        for row in text_rows:
            split_row = self.word_split.findall(row)
            print(split_row)


if __name__ == '__main__':
    txt = 'print("how are you?")\n'
    TextData(txt)
