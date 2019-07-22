import pygame
from pygame.locals import *

screen = pygame.display.set_mode((1024,768))
pygame.display.set_caption('first demo')


clock = pygame.time.Clock()
protagonist_walk_sprites = []
for i in range(1,6):
	protagonist_walk_sprites.append(pygame.image.load('protagonist_walk_'+str(i)+'.png'))

protagonist_x = 300
protagonist_y = 300
walk_animation_index = 0


running = True
while running:
    clock.tick(10)
    screen.fill((200, 200, 200))
    # bilt - block image transform.
    # Take car pixels and put them centered at (250, 250)
    # This is drawing to a buffer that is not displayed to the user
    screen.blit(protagonist_walk_sprites[walk_animation_index], (protagonist_x, protagonist_y))
    # Let us display the buffer to the user
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            key_dict = pygame.key.get_pressed()
            if key_dict[pygame.K_ESCAPE]:
                running = False
            if key_dict[pygame.K_UP]:
                protagonist_y -= 10
                walk_animation_index +=1
            if key_dict[pygame.K_RIGHT]:
                protagonist_x += 10
                walk_animation_index +=1
            if key_dict[pygame.K_DOWN]:
                protagonist_y += 10
                walk_animation_index +=1
            if key_dict[pygame.K_LEFT]:
                protagonist_x -= 10
                walk_animation_index += 1
            if walk_animation_index > 4:
            	walk_animation_index = 0
       
