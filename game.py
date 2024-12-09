import pygame
import sys
import random
from collections import deque
from agent import Agent
import numpy as np
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
    to_remove = list()
    for i in range(len(pip_list)):
        pipe = pip_list[i]
        if pipe.centerx <100:
            score += 0.5
            to_remove.append(pipe)
    for pipe in to_remove:
        pip_list.remove(pipe)
    return score//1, True, score

def reset_game():
    return deque(maxlen=4), (100,512), 0, 0



def feed_agent(agent, pipe_list, bird_rect, reward):
    # Feed and train agent 
    # 5 neurons at the begining:
    #   bottom_pipe_y
    #   top_pipe_y
    #   pipe_x - 100
    #   bird_y
    # return next move
    try:
        bottom_pipe_y = pipe_list[0].topleft[1]
        top_pipe_y = pipe_list[1].bottom_left[1]
        pipe_x = pipe_list[0].topleft[0] - 100
    except:
        bottom_pipey = 0 
        top_pipe_y = 0
        pipe_x = 0
    bird_rect = bird_rect.centery
    


    return 0 


def main():
    agent = Agent()
    # Initialize lib
    pygame.init()
 
    # Create window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    score = 0 
    reward = 0

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
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bird_movement = 0
                    bird_movement -= 9
                if event.key == pygame.K_SPACE and not game_active:
                    game_active = True
                    pip_list, bird_rect.center, bird_movement, score = reset_game()
            if event.type == SPAWNPIPE:
                pip_list.extend(create_pipe(pipe_surface, pipe_height))

        if game_active:
            
            # Agent move
            agent_move = feed_agent(agent,pip_list, bird_rect, reward)
            # Action move
            if np.array_equal(agent_move, [1,0]):
                # JUMP
                bird_movement = 0
                bird_movement -= 9

            elif np.array_equal(agent_move, [0,1]):
                # NOT JUMP
                pass

            # Insert bird
            screen.blit(bird_surface, bird_rect)
            
            # Insert pipes
            draw_pipes(pip_list, pipe_surface, screen)
                   
            # Pipes movement
            pip_list = move_pipes(pip_list)

            # Floor movement
            floor_x_pos = get_floor_x(floor_x_pos)
            
            # Bird movement
            bird_movement += gravity
            bird_rect.centery += bird_movement
            
            # Collisions
            reward,game_active,score = check_collisions(pip_list, bird_rect, score)
        
        clock.tick(FRAME_RATE)

        # Update window
        pygame.display.update()

    pygame.quit()
if __name__ == '__main__':
    main()
