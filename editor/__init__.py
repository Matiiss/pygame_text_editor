"""Main module that contains the main function to run the application."""

import pygame
from .text_box import TextBox


def main() -> None:
    """Main function to run the application."""
    pygame.init()

    screen = pygame.display.set_mode((500, 400))
    pygame.display.set_caption('lol')
    clock = pygame.time.Clock()

    main_text_box = TextBox((0, 0), (500, 400), font=('Courier New', 18))

    running = True
    while running:
        clock.tick(60)
        delta_time = clock.get_time()
        screen.fill((0, 0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        main_text_box.update(screen, events, delta_time)

        pygame.display.flip()
    pygame.quit()
