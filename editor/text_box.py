import pygame
import string
import typing as t
import time
import math


class TextBox:
    def __init__(
            self,
            pos,
            size,
            bg=(33, 33, 36),
            fg=(255, 255, 255),
            font=(None, 16)
    ):
        self.surf = pygame.Surface(size)
        # self.surf.fill(bg)

        self.rect = self.surf.get_rect(topleft=pos)

        self.fg = fg
        self.bg = bg

        font_name, font_size = font
        try:
            self.font = pygame.font.Font(font_name, font_size)
        except FileNotFoundError:
            self.font = pygame.font.SysFont(font_name or "", font_size)

        self.x_off, self.y_off = 5, 5

        cursor_coefficient = 0.1
        char_height = self.font.render(string.ascii_letters, True, self.fg).get_height()
        self.cursor = pygame.Rect(
            self.x_off, self.y_off, cursor_coefficient * font_size, char_height)
        self.text_data = [[]]

        self.continuous_press = None
        self.continuous_press_start = 0
        self.continuous_press_time_passed = math.inf
        self.continuous_press_interval = 50

        self.mouse_pos = pygame.mouse.get_pos()
        self.cursor_set = False

    def update(self, surf, events, dt):
        self.draw(surf)
        self.input(events, dt)
        self.mouse_pos = pygame.mouse.get_pos()
        self.set_cursor()

        self.surf.fill(self.bg)
        self.draw_text()
        self.draw_cursor()

    def draw(self, surf):
        surf.blit(self.surf, self.rect)

    def input(self, events, dt):
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
                if self.continuous_press is not None and event.key in self.continuous_press[0]:
                    self.continuous_press = None
                    self.continuous_press_time_passed = math.inf

        if self.continuous_press is not None:
            if (time.time() * 1000 - self.continuous_press_start
                    >= self.continuous_press[-1]):
                if (self.continuous_press_time_passed
                        >= self.continuous_press_interval):
                    self.continuous_press[-2]()
                    self.continuous_press_time_passed = 0
                self.continuous_press_time_passed += dt

    def set_cursor(self):
        if self.rect.collidepoint(self.mouse_pos):
            if not self.cursor_set:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                self.cursor_set = True
        else:
            if self.cursor_set:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.cursor_set = False

    def continuous_call(*keys, delay=500):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                self.continuous_press_start = time.time() * 1000
                self.continuous_press = (
                    set(keys), lambda: func(self, *args, **kwargs), delay
                )
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    def write(self, character):
        w, h = self.char_size(character)
        col, row = self.cursor_position
        self.text_data[row].insert(col, character)
        self.cursor.left += w

    def char_size(self, character):
        surf = self.font.render(character, True, self.fg)
        return surf.get_size()

    def draw_cursor(self):
        pygame.draw.rect(self.surf, self.fg, self.cursor)

    def draw_text(self):
        y = self.y_off
        for row in self.text_data:
            text = ''.join(row)
            surf = self.font.render(text, True, self.fg)
            self.surf.blit(surf, (self.x_off, y))
            y += surf.get_height()

    @continuous_call(pygame.K_RETURN)
    def newline(self):
        col, row = self.cursor_position
        to_new_line = self.text_data[row][col:]
        self.text_data[row] = self.text_data[row][:col]
        self.text_data.insert(row + 1, to_new_line)
        new_y = self.cursor.y + self.cursor.height
        self.cursor.topleft = (self.x_off, new_y)

    @property
    def cursor_position(self):
        x, y, w, h = self.cursor
        x -= self.x_off
        y -= self.y_off
        row = y // h
        text_row = self.text_data[row]
        text_width = 0
        for col, char in enumerate(text_row, start=1):
            text_width += self.char_size(char)[0]
            if text_width == x:
                return col, row
        return 0, row

    @cursor_position.setter
    def cursor_position(self, position):
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
    def move_by_key(self, key):
        x, y, _, h = self.cursor
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

    def get_line_length(self, row):
        if 0 <= row < len(self.text_data):
            return len(self.text_data[row])
        return 0

    def delete_char(self, position):
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
    def delete(self):
        self.delete_char(self.cursor_position)

    @continuous_call(pygame.K_BACKSPACE)
    def backspace(self):
        col, row = self.cursor_position
        self.cursor_position = (col - 1, row)
        if (col, row) != (0, 0):
            self.delete_char(self.cursor_position)

    @continuous_call(pygame.K_TAB)
    def tab(self):
        self.write(' ' * 4)

    def insert_cursor_xy(self, pos):
        pass
