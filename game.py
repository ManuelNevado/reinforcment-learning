import pygame
import sys
import random
from collections import deque
from agent impor Agent

FRAME_RATE = 120
WIDTH, HEIGHT = 576, 1024


def create_pipe(pipe_surface, pipe_height):
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop = (700, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (700, random_pipe_pos-300))
    return bottom_pipe, top_pipe

def draw_pipes(pipe_list, pipe_surface, screen):
    for pipe in pipe_list:
        if pipe.bottom >=1024:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def get_floor_x(floor_x_pos):
    if floor_x_pos + WIDTH == 0:
        return 0
    else:
        return floor_x_pos - 1

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5 
    return pipes

def check_collisions(pip_list, bird_rect, score):
    # bird collition
    if bird_rect.top <= 0 or bird_rect.bottom >= 900:
        print(f"Score: {score}")
        reward = -1
        return reward, False, score
    # pipe collition
    for pipe in pip_list:
        if bird_rect.colliderect(pipe):
            print(f"Score: {score}")    
            reward = -1
            return reward, False, score
    return score//1, True, score

def reset_game():
    return deque(maxlen=4), (100,512), 0, 0



def feed_agent(bottom_pipe_y, top_pipe_y, pipe_x, bird_y, bird_x, reward):
    # Feed and train agent 
    pass

def main():
    agent = Agent()
    # Initialize lib
    pygame.init()
 
    # Create window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    score = 0 

    clock = pygame.time.Clock()
    
    game_active = True


    # GRAVITY
    gravity = 0.20
    bird_movement = 0
    
    # import background 
    bg_surface = pygame.image.load('assets/sprites/background-day.png').convert()
    bg_surface = pygame.transform.scale2x(bg_surface)
    
    # import floor
    floor_surface = pygame.image.load('assets/sprites/base.png').convert()
    floor_surface = pygame.transform.scale2x(floor_surface)
    floor_x_pos = 0
    floor_surface_2 = pygame.image.load('assets/sprites/base.png').convert()
    floor_surface_2 = pygame.transform.scale2x(floor_surface_2)

    # import bird
    bird_surface = pygame.image.load('assets/sprites/yellowbird-midflap.png').convert()
    bird_surface = pygame.transform.scale2x(bird_surface)
    bird_rect = bird_surface.get_rect(center = (100,512))

    # import pipes
    pipe_surface = pygame.image.load('assets/sprites/pipe-green.png').convert()
    pipe_surface = pygame.transform.scale2x(pipe_surface)
    
    pip_list = deque(maxlen=4)
    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE,1200)
    pipe_height = [400,600,800]
    # game loop
    while True:
        # Insert scenery
        screen.blit(bg_surface,(0,0))
        screen.blit(floor_surface,(floor_x_pos,900))
        screen.blit(floor_surface_2,(floor_x_pos+WIDTH,900))
        
        play_step()
        reward = score
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_movement = 0
                    bird_movement -= 9
                if event.key == pygame.K_SPACE and not game_active:
                    game_active = True
                    pip_list, bird_rect.center, bird_movement, score = reset_game()
            if event.type == SPAWNPIPE:
                pip_list.extend(create_pipe(pipe_surface, pipe_height))





        if game_active:
            
            

            # Insert bird
            screen.blit(bird_surface, bird_rect)
            
            
            # Collisions
            game_active = check_collisions(pip_list, bird_rect, score)[1]
                
            # Pipe movement
            pip_list = move_pipes(pip_list)
            draw_pipes(pip_list, pipe_surface, screen)
            
            # Update variables
            floor_x_pos = get_floor_x(floor_x_pos)
            
            # Bird movement
            bird_movement += gravity
            bird_rect.centery += bird_movement
            score += 0.05    
        clock.tick(FRAME_RATE)

        # Update window
        pygame.display.update()

    pygame.quit()
if __name__ == '__main__':
    main()
