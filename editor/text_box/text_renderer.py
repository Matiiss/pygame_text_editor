"""A module containing TextRenderer class for rendering text."""

from .text_data import TextData


class TextRenderer:
    def __init__(
            self,
            surface,
            text_data: TextData
    ):
        self.surf = surface
        self.rect = self.surf.get_rect()
        self.text_data = text_data
