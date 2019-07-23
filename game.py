import pygame
from pygame.locals import *
from retrogamelib import display
from retrogamelib import button
from retrogamelib import clock
from retrogamelib import font
from retrogamelib import dialog
from retrogamelib import util
from retrogamelib import camera
from retrogamelib.constants import *

#Game Constant
DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3
PLAYER_INIT_X = 800
PLAYER_INIT_Y = 800
FRAMES_PER_SECOND = 60
GAME_FRAME_WIDTH = 1024
GAME_FRAME_HEIGHT = 768

# Initialize the game
screen = pygame.display.set_mode((1024,768))
pygame.display.set_caption('Sandbox!')

#Game Resources
protagonist_walk_sprites = []
for i in range(1,6):
	protagonist_walk_sprites.append(pygame.image.load('protagonist_walk_'+str(i)+'.png'))
background = pygame.image.load('background.png')


class Entity(pygame.sprite.Sprite):
	def __init__(self, x, y, vx, vy, ax, ay, sprite):
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.ax = ax
		self.ay = ay
		self.sprite = sprite


class Player(Entity):
	def __init__(self, x, y, vx, vy, ax, ay, movement_sprites):
		Entity.__init__(self, x, y, vx, vy, ax, ay, movement_sprites[0])
		self.movement_sprites = movement_sprites
		self.movement_animation_index = 0
		self.move_speed = 3
		self.jump_speed = 1000
		self.walk_acceleration = 1
		self.jump_interval = 120
		self.jump_cooldown = 0
	def move(self, direction):
		if direction == DIRECTION_LEFT:
			self.vx += - self.move_speed
			self.movement_animation_index += 1
		elif direction == DIRECTION_RIGHT:
			self.vx += self.move_speed
			self.movement_animation_index += 1
		elif direction == DIRECTION_UP:
			if self.jump_cooldown == 0:
				print("Jump!")
				self.jump_cooldown = self.jump_interval
				self.vy += -self.jump_speed
		if self.movement_animation_index > 14:
			self.movement_animation_index = 0


class World():
	def __init__(self):
		self.clock = pygame.time.Clock()
		self.player = Player(PLAYER_INIT_X, PLAYER_INIT_Y, 0, 0, 0, 0, movement_sprites=protagonist_walk_sprites)
		self.game_running = True
		self.camera_x = self.player.x - GAME_FRAME_WIDTH / 2
		self.camera_y = self.player.y - GAME_FRAME_HEIGHT / 2

	def physical_engine(self):
		# Gravity
		if self.player.vy < 50:
			self.player.ay = 2.5
		else:
			self.player.ay = 0

		self.player.vx += self.player.ax
		self.player.vy += self.player.ay
		self.player.x += self.player.vx
		self.player.y += self.player.vy
		self.player.ax = round(self.player.ax, 1)
		self.player.ay = round(self.player.ay, 1)
		self.player.vx = round(self.player.vx, 1)
		self.player.vy = round(self.player.vy, 1)
		self.player.x = round(self.player.x, 1)
		self.player.y = round(self.player.y, 1)
		print("( ",self.player.x,",",self.player.y,")")
		self.player.vx = 0

	def render_frame(self):
		self.camera_x = self.player.x - GAME_FRAME_WIDTH / 2
		self.camera_y = self.player.y - GAME_FRAME_HEIGHT / 2
		screen.blit(background,(0,0))
		screen.blit(self.player.movement_sprites[self.player.movement_animation_index // 3],(GAME_FRAME_WIDTH / 2, GAME_FRAME_HEIGHT / 2))
		pygame.display.flip()

	def main_loop(self):
		while self.game_running:
			button.handle_input()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.game_running = False

			key_dict = pygame.key.get_pressed()
			if key_dict[pygame.K_ESCAPE]:
				self.game_running = False
			if key_dict[pygame.K_SPACE]:
				self.player.move(DIRECTION_UP)

			if button.is_held(RIGHT):
				self.player.move(DIRECTION_RIGHT)
			if button.is_held(LEFT):
				self.player.move(DIRECTION_LEFT)
			if self.player.jump_cooldown > 0:
				self.player.jump_cooldown -= 1
			self.physical_engine()
			self.render_frame()
			self.clock.tick(FRAMES_PER_SECOND)

world = World()
world.main_loop()

