import pygame
from .text_box import TextBox


pygame.init()


def main():

    screen = pygame.display.set_mode((500, 400))
    pygame.display.set_caption('lol')
    clock = pygame.time.Clock()

    tb = TextBox((0, 0), (500, 400), font=('Courier New', 18))

    running = True
    while running:
        clock.tick(60)
        dt = clock.get_time()
        screen.fill((0, 0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        tb.update(screen, events, dt)

        pygame.display.flip()
    pygame.quit()
