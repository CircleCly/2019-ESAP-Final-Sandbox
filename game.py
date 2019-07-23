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
from block import *

#Game Constant
DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3
NO_DIRECTION_X = 4
NO_COLLISION = 5
PLAYER_INIT_X = 800
PLAYER_INIT_Y = 800
FRAMES_PER_SECOND = 60
GAME_FRAME_WIDTH = 800
GAME_FRAME_HEIGHT = 600
# Initialize the game
screen = pygame.display.set_mode((GAME_FRAME_WIDTH,GAME_FRAME_HEIGHT))
pygame.display.set_caption('Sandbox!')

#Game Resources
protagonist_walk_sprites = []
for i in range(1,6):
	protagonist_walk_sprites.append(pygame.image.load('protagonist_walk_'+str(i)+'.png'))
background = pygame.image.load('background.png')
dirt_block = pygame.image.load('dirt_block.png')

def get_collision_direction(rect1, rect2):
	#Detect where does rect2 crashes into rect1
	x1 = rect1.x
	y1 = rect1.y
	w1 = rect1.width
	h1 = rect1.height
	x2 = rect2.x
	y2 = rect2.y
	w2 = rect2.width
	h2 = rect2.height
	if y2 + h2 > y1 and y2 < y1 + w1 and x2 + w2 >= x1:
		return DIRECTION_LEFT
	elif x2 + w2 > x1 and y2 + h2 >= y1 and x2 < x1 + y1:
		return DIRECTION_UP
	elif y2 + h2 > y1 and y2 < y1 + w1 and x2 <= x1 + w1:
		return DIRECTION_RIGHT
	elif x2 + w2 > x1 and x2 < x1 + y1 and y2 >= y1 + w1:
		return DIRECTION_DOWN
	else:
		return NO_COLLISION

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
		self.jump_speed = 7
		self.walk_acceleration = 1
		self.jump_interval = 120
		self.jump_cooldown = 0
		self.width = 56
		self.height = 94
		self.hitbox = pygame.rect.Rect((x, y), (self.width, self.height))

	def move(self, direction):
		if direction == DIRECTION_LEFT:

			self.vx = - self.move_speed
			self.movement_animation_index += 1
		elif direction == DIRECTION_RIGHT:
			self.vx = self.move_speed
			self.movement_animation_index += 1
		elif direction == DIRECTION_UP:
			if self.jump_cooldown == 0:
				self.jump_cooldown = self.jump_interval
				self.vy += -self.jump_speed
		elif direction == NO_DIRECTION_X:
			self.vx = 0
		if self.movement_animation_index > 14:
			self.movement_animation_index = 0

class World():
	def __init__(self):
		self.clock = pygame.time.Clock()
		self.player = Player(PLAYER_INIT_X, PLAYER_INIT_Y, 0, 0, 0, 0, movement_sprites=protagonist_walk_sprites)
		self.game_running = True
		self.camera_x = self.player.x - GAME_FRAME_WIDTH / 2
		self.camera_y = self.player.y - GAME_FRAME_HEIGHT / 2
		self.blocks = []
		for i in range(0, 60):
			for j in range(0, 30):
				self.blocks.append(Block(self.player.x + j * 20, self.player.y + 600 + i * 20, dirt_block, "dirt_block"))

	def physical_engine(self):
		# Gravity
		if self.player.vy < 50:
			self.player.ay = 1
		else:
			self.player.ay = 0
		# 	future_hitbox = pygame.rect.Rect((self.player.x + self.player.vx),(self.player.width, self.player.height))
		#	for block in self.blocks:
		# 	if get_collision_direction(future_hitbox, block) == NO_COLLISION:
		for block in self.blocks:
			if get_collision_direction(block, self.player) == DIRECTION_UP and self.player.vy >= 0:
				self.player.ay = 0
				self.player.vy = 0
			elif get_collision_direction(block, self.player) == DIRECTION_LEFT and self.player.vx >= 0:
				self.player.ax = 0
				self.player.vx = 0
			elif get_collision_direction(block, self.player) == DIRECTION_DOWN and self.player.vy <= 0:
				self.player.ay = 0
				self.player.vy = 0
			elif get_collision_direction(block, self.player) == DIRECTION_RIGHT and self.player.vx <= 0:
				self.player.ay = 0
				self.player.vy = 0
		self.player.vx += self.player.ax
		self.player.vy += self.player.ay
		self.player.x += self.player.vx
		self.player.y += self.player.vy
		self.player.hitbox = pygame.rect.Rect((self.player.x, self.player.y), (self.player.width, self.player.height))
		self.player.ax = round(self.player.ax, 1)
		self.player.ay = round(self.player.ay, 1)
		self.player.vx = round(self.player.vx, 1)
		self.player.vy = round(self.player.vy, 1)
		self.player.x = round(self.player.x, 1)
		self.player.y = round(self.player.y, 1)
		print("Player's hitbox's position : ( ", self.player.hitbox.x, ",", self.player.hitbox.y, ")")
		print("Player's position : ( ",self.player.x,",",self.player.y,")")


	def render_frame(self):
		self.camera_x = self.player.x + self.player.width // 2 - GAME_FRAME_WIDTH // 2
		self.camera_y = self.player.y + self.player.height // 2 - GAME_FRAME_HEIGHT // 2
		screen.blit(background,(0, 0))
		current_movement_frame = self.player.movement_sprites[self.player.movement_animation_index // 3]
		screen.blit(current_movement_frame, (GAME_FRAME_WIDTH // 2 - self.player.width // 2, GAME_FRAME_HEIGHT // 2 - self.player.height // 2))
		for block in self.blocks:
			# If block is in camera range
			if self.camera_x - block.width <= block.x <= self.camera_x + GAME_FRAME_WIDTH \
				and self.camera_y - block.height <= block.y <= self.camera_y + GAME_FRAME_HEIGHT:
				screen.blit(block.sprite, (block.x - self.camera_x, block.y - self.camera_y, block.width, block.height))
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
			elif button.is_held(LEFT):
				self.player.move(DIRECTION_LEFT)
			else:
				self.player.move(NO_DIRECTION_X)
			if self.player.jump_cooldown > 0:
				self.player.jump_cooldown -= 1
			self.physical_engine()
			self.render_frame()
			self.clock.tick(FRAMES_PER_SECOND)

world = World()
world.main_loop()

