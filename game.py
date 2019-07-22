import pygame
from pygame.locals import *
from retrogamelib import display
from retrogamelib import button
from retrogamelib import clock
from retrogamelib import font
from retrogamelib import dialog
from retrogamelib import util
from retrogamelib.constants import *
screen = pygame.display.set_mode((1024,768))
pygame.display.set_caption('first demo')
clock = pygame.time.Clock()
protagonist_x = 300
protagonist_y = 300
walk_animation_index = 0
protagonist_walk_sprites = []
for i in range(1,6):
	protagonist_walk_sprites.append(pygame.image.load('protagonist_walk_'+str(i)+'.png'))
class World(pygame.sprite.Sprite):
	def __init__(self,clock):
		self.clock=clock
	def player(self,protagonist_x,protagonist_y,walk_animation_index,protagonist_walk_sprites):
		if button.is_held(UP):
			protagonist_y -= 10
			walk_animation_index +=1
		if button.is_held(RIGHT):
			protagonist_x += 10
			walk_animation_index +=1
		if button.is_held(DOWN):
			protagonist_y += 10
			walk_animation_index +=1
		if button.is_held(LEFT):
			protagonist_x -= 10
			walk_animation_index += 1
		if walk_animation_index > 4:
			walk_animation_index = 0
		screen.blit(protagonist_walk_sprites[walk_animation_index], (protagonist_x, protagonist_y))
		L=[protagonist_x,protagonist_y,walk_animation_index]
		return L
world=World(clock)
running = True
while running:
    clock.tick(10)
    screen.fill((200, 200, 200))
    # bilt - block image transform.
    # Take car pixels and put them centered at (250, 250)
    # This is drawing to a buffer that is not displayed to the user
    # Let us display the buffer to the user
    button.handle_input()
    L=world.player(protagonist_x,protagonist_y,walk_animation_index,protagonist_walk_sprites)
    protagonist_x=L[0]
    protagonist_y=L[1]
    walk_animation_index=L[2]
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            key_dict = pygame.key.get_pressed()
            if key_dict[pygame.K_ESCAPE]:
                running = False
