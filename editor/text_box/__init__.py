"""This package contains the TextBox class that is used for editing text."""

import string
import math
import itertools

import pygame


class TextBox:
    """Class of a text widget."""
    def __init__(
            self,
            pos,
            size,
            background=(33, 33, 36),
            foreground=(255, 255, 255),
            font=(None, 16)
    ) -> None:
        """Initializes the widget."""
        self.surf = pygame.Surface(size)
        self.rect = self.surf.get_rect(topleft=pos)

        self.foreground = foreground
        self.background = background

        font_name, font_size = font
        try:
            self.font = pygame.font.Font(font_name, font_size)
        except FileNotFoundError:
            self.font = pygame.font.SysFont(font_name or "", font_size)

        self.x_off, self.y_off = 5, 5

        cursor_coefficient = 0.1
        char_height = self.font.render(string.ascii_letters, True, self.foreground).get_height()
        self.cursor = pygame.Rect(
            self.x_off, self.y_off, cursor_coefficient * font_size, char_height)
        self.text_data = [[]]

        self.continuous_press_data: dict = {
            'keys': set(),
            'function': callable,
            'delay': None,
            'interval': None,
            'time_passed': math.inf,
            'start': 0
        }

        self.mouse_pos = pygame.mouse.get_pos()
        self.cursor_set = False

    def update(self, surf: pygame.Surface, events: list, delta_time: int) -> None:
        """Updates all functions of the widget."""
        self.draw(surf)
        self.input(events)
        self.mouse_pos = pygame.mouse.get_pos()
        self.set_cursor()
        self.repeat_key(delta_time)

        self.surf.fill(self.background)
        self.draw_text()
        self.draw_cursor()

    def draw(self, surf: pygame.Surface) -> None:
        """Draws the widget on the given surface."""
        surf.blit(self.surf, self.rect)

    def input(self, events: list) -> None:
        """Handles all input events for the widget."""
        for event in events:
            if event.type == pygame.TEXTINPUT:
                self.write(event.text)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.newline()
                elif event.key in (
                        pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT):
                    self.move_by_key(event.key)
                elif event.key == pygame.K_DELETE:
                    self.delete()
                elif event.key == pygame.K_BACKSPACE:
                    self.backspace()
                elif event.key == pygame.K_TAB:
                    self.tab()

            elif event.type == pygame.KEYUP:
                self.reset_continuous_key(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    self.insert_cursor_xy(event.pos)

    def set_cursor(self) -> None:
        """Changes the mouse cursor depending on whether it is in the widget or not."""
        if self.rect.collidepoint(self.mouse_pos):
            if not self.cursor_set:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                self.cursor_set = True
        else:
            if self.cursor_set:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.cursor_set = False

    @staticmethod
    def continuous_call(*keys, delay: int = 500, interval: int = 50) -> callable:
        """Decorator to manage repeated calls for held keys."""
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                data = self.continuous_press_data
                data['keys'] = set(keys)
                data['function'] = lambda: func(self, *args, **kwargs)
                data['delay'] = delay
                data['interval'] = interval
                data['start'] = pygame.time.get_ticks()
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    def reset_continuous_key(self, key: int) -> None:
        """Resets data for continuous key press."""
        if key in self.continuous_press_data['keys']:
            self.continuous_press_data = {
                'keys': set(),
                'function': callable,
                'delay': None,
                'interval': None,
                'time_passed': math.inf,
                'start': 0
            }

    def repeat_key(self, delta_time: int) -> None:
        """Repeats held key function in an interval after a delay."""
        data = self.continuous_press_data
        if not data['keys']:
            return
        now = pygame.time.get_ticks()
        if now - data['start'] < data['delay']:
            return
        if data['time_passed'] >= data['interval']:
            data['function']()
            data['time_passed'] = 0
        data['time_passed'] += delta_time

    def write(self, character: str) -> None:
        """Adds a character to the text data list, moves cursor."""
        width, _ = self.char_size(character)
        col, row = self.cursor_position
        self.text_data[row].insert(col, character)
        self.cursor.left += width

    def char_size(self, character: str) -> tuple[int, int]:
        """Returns the size (width, height) of the given character."""
        surf = self.font.render(character, True, self.foreground)
        return surf.get_size()

    def draw_cursor(self) -> None:
        """Draws the cursor on the screen."""
        # TODO: implement cursor blinking
        pygame.draw.rect(self.surf, self.foreground, self.cursor)

    def draw_text(self) -> None:
        """Draws text from the text data list."""
        y_pos = self.y_off
        for row in self.text_data:
            text = ''.join(row)
            surf = self.font.render(text, True, self.foreground)
            self.surf.blit(surf, (self.x_off, y_pos))
            y_pos += surf.get_height()

    @continuous_call(pygame.K_RETURN)
    def newline(self) -> None:
        """Creates a new line."""
        col, row = self.cursor_position
        to_new_line = self.text_data[row][col:]
        self.text_data[row] = self.text_data[row][:col]
        self.text_data.insert(row + 1, to_new_line)
        new_y = self.cursor.y + self.cursor.height
        self.cursor.topleft = (self.x_off, new_y)

    @property
    def cursor_position(self) -> tuple[int, int]:
        """Returns the column and row of the current cursor position."""
        x_pos, y_pos, _, height = self.cursor
        x_pos -= self.x_off
        y_pos -= self.y_off
        row = y_pos // height
        text_row = self.text_data[row]
        text_width = 0
        for col, char in enumerate(text_row, start=1):
            text_width += self.char_size(char)[0]
            if text_width == x_pos:
                return col, row
        return 0, row

    @cursor_position.setter
    def cursor_position(self, position: tuple[int, int]) -> None:
        """Sets the cursors position to the given column and row."""
        col, row = position
        if col < 0:
            row -= 1
            col = None
        if row < 0:
            return
        try:
            text_row = self.text_data[row]
            if col and col > len(text_row):
                row += 1
                col = 0
                text_row = self.text_data[row]
            new_x = self.x_off + sum(self.char_size(c)[0] for c in text_row[:col])
        except IndexError:
            return
        new_y = self.y_off + row * self.cursor.height
        self.cursor.topleft = (new_x, new_y)

    @continuous_call(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)
    def move_by_key(self, key: int) -> None:
        """Moves the cursor using arrow keys."""
        pos = current_col, current_row = self.cursor_position
        if key == pygame.K_UP:
            next_col = min(self.get_line_length(current_row - 1), current_col)
            pos = (next_col, current_row - 1)
        elif key == pygame.K_DOWN:
            next_col = min(self.get_line_length(current_row + 1), current_col)
            pos = (next_col, current_row + 1)
        elif key == pygame.K_LEFT:
            pos = (current_col - 1, current_row)
        elif key == pygame.K_RIGHT:
            pos = (current_col + 1, current_row)

        self.cursor_position = pos

    def get_line_length(self, row: int) -> int:
        """Returns the length (in characters) of the given row."""
        if 0 <= row < len(self.text_data):
            return len(self.text_data[row])
        return 0

    def delete_char(self, position: tuple[int, int]) -> None:
        """Deletes a character at a given position."""
        col, row = position
        line = self.text_data[row]
        line_length = len(line)
        if col < line_length:
            line.pop(col)
        elif col >= line_length:
            try:
                next_line = self.text_data[row + 1]
                self.text_data.pop(row + 1)
                self.text_data[row] += next_line
            except IndexError:
                pass

    @continuous_call(pygame.K_DELETE)
    def delete(self) -> None:
        """Deletes a character at the current cursor position."""
        self.delete_char(self.cursor_position)

    @continuous_call(pygame.K_BACKSPACE)
    def backspace(self) -> None:
        """Deletes a character in the column before current cursor position."""
        col, row = self.cursor_position
        self.cursor_position = (col - 1, row)
        if (col, row) != (0, 0):
            self.delete_char(self.cursor_position)

    @continuous_call(pygame.K_TAB)
    def tab(self) -> None:
        """Adds a tab in the current cursor position."""
        self.write(' ' * 4)

    def insert_cursor_xy(self, pos: tuple[int, int]) -> None:
        """Inserts cursor in the closes column and row to the given xy position."""
        x_pos, y_pos = pos
        x_pos -= self.x_off
        y_pos -= self.y_off
        row = min(len(self.text_data) - 1, y_pos // self.cursor.height)
        col = 0

        text_data_row = self.text_data[row]
        temp_width = text_data_row and self.char_size(text_data_row[0])[0] // 2
        pairwise_iterator = itertools.pairwise(text_data_row)

        if text_data_row and x_pos > temp_width:
            for col, (char1, char2) in enumerate(pairwise_iterator, 1):
                char1_width = self.char_size(char1)[0] / 2
                char2_width = self.char_size(char2)[0] / 2
                char_width_sum = round(sum((char1_width, char2_width)))

                if x_pos in range(temp_width, temp_width + char_width_sum + 1):
                    break
                temp_width += char_width_sum
            else:
                col += 1

        self.cursor_position = (col, row)
