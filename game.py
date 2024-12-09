import pygame
import sys

FRAME_RATE = 120
WIDTH, HEIGHT = 576, 1024

def get_floor_x(floor_x_pos):
    if floor_x_pos + WIDTH == 0:
        return 0
    else:
        return floor_x_pos - 1

def main():
    clock = pygame.time.Clock()
    
    # Initialize lib
    pygame.init()
    # Create window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # import background 
    bg_surface = pygame.image.load('assets/sprites/background-day.png').convert()
    bg_surface = pygame.transform.scale2x(bg_surface)
    
    # import floor
    floor_surface = pygame.image.load('assets/sprites/base.png').convert()
    floor_surface = pygame.transform.scale2x(floor_surface)
    floor_x_pos = 0
    floor_surface_2 = pygame.image.load('assets/sprites/base.png').convert()
    floor_surface_2 = pygame.transform.scale2x(floor_surface_2)
    # game loop
    while True:
        screen.blit(bg_surface,(0,0))
        screen.blit(floor_surface,(floor_x_pos,900))
        screen.blit(floor_surface_2,(floor_x_pos+WIDTH,900))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        floor_x_pos = get_floor_x(floor_x_pos)
        clock.tick(FRAME_RATE)
        # Update window
        pygame.display.update()

    pygame.quit()
if __name__ == '__main__':
    main()
