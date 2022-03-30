"""A module containing TextData class for storing text data, along with text colors."""
import itertools
import re
import operator

from sample_color_config import dct


class TextData:
    word_split = re.compile(r'\w+|[.\[\]{}() ]')
    group_key = operator.itemgetter('data')

    def __init__(
            self,
            text: str = '',
            default_color: dict | None = None,
            color_config: dict | None = dct
    ):
        if default_color is None:
            default_color = {'fg': (255, 255, 255), 'bg': None}

        self.default_color = default_color
        self.color_config = color_config
        self.data = self.format_text(text)

    def format_text(self, text):
        temp_data = list()
        text_rows = text.splitlines()
        for row in text_rows:
            split_row = self.word_split.findall(row)
            temp_row = list()
            matched_row = (
                {
                    'text': word,
                    'data': self.color_config.get(word, self.default_color)
                } for word in split_row)
            for data, group in itertools.groupby(matched_row, self.group_key):
                temp_row.append(
                    {
                        'text': ''.join(w.get('text', '') for w in group),
                        'data': data
                    }
                )
            temp_data.append(temp_row)
        return temp_data


if __name__ == '__main__':
    txt = 'print("how are you?")\nprint()'
    TextData(txt)
