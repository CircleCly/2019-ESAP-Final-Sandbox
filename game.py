import pygame
import random
from block import *

#Game Constant
DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3
NO_DIRECTION_X = 4
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
		self.jump_speed = 17
		self.walk_acceleration = 1
		self.can_jump = True
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
			if self.can_jump:
				self.vy += -self.jump_speed
				self.can_jump = False
		elif direction == NO_DIRECTION_X:
			self.vx = 0
		if self.movement_animation_index > 19:
			self.movement_animation_index = 0

class World():
	def __init__(self):
		self.clock = pygame.time.Clock()
		self.player = Player(PLAYER_INIT_X, PLAYER_INIT_Y, 0, 0, 0, 0, movement_sprites=protagonist_walk_sprites)
		self.game_running = True
		self.camera_x = self.player.x - GAME_FRAME_WIDTH / 2
		self.camera_y = self.player.y - GAME_FRAME_HEIGHT / 2
		self.blocks = []
		for i in range(0, 9):
			for j in range(0, 1000):
				self.blocks.append(Block(self.player.x - 5000 + j * 20, self.player.y + 600 + i * 20, dirt_block, "dirt_block"))

	def physical_engine(self):
		# Gravity
		if self.player.vy < 5:
			self.player.ay = 0.5
		else:
			self.player.ay = 0
		self.player.vx += self.player.ax
		self.player.vy += self.player.ay
		future_hitbox_x = pygame.rect.Rect((self.player.x + self.player.vx, self.player.y), (self.player.width, self.player.height))
		future_hitbox_y = pygame.rect.Rect((self.player.x, self.player.y + self.player.vy), (self.player.width, self.player.height))
		will_collide_x = False
		will_collide_y = False
		for block in self.blocks:
			if future_hitbox_x.colliderect(block.hitbox):
				will_collide_x = True
			if future_hitbox_y.colliderect(block.hitbox):
				will_collide_y = True
		self.player.can_jump = will_collide_y
		if not will_collide_x:
			self.player.x += self.player.vx
		if not will_collide_y:
			self.player.y += self.player.vy
		self.player.hitbox = pygame.rect.Rect((self.player.x, self.player.y), (self.player.width, self.player.height))

	def render_frame(self):
		self.camera_x = self.player.x + self.player.width // 2 - GAME_FRAME_WIDTH // 2
		self.camera_y = self.player.y + self.player.height // 2 - GAME_FRAME_HEIGHT // 2
		screen.blit(background,(0, 0))
		current_movement_frame = self.player.movement_sprites[self.player.movement_animation_index // 4]
		screen.blit(current_movement_frame, (GAME_FRAME_WIDTH // 2 - self.player.width // 2, GAME_FRAME_HEIGHT // 2 - self.player.height // 2))
		for block in self.blocks:
			# If block is in camera range
			if self.camera_x - block.width <= block.x <= self.camera_x + GAME_FRAME_WIDTH \
				and self.camera_y - block.height <= block.y <= self.camera_y + GAME_FRAME_HEIGHT:
				screen.blit(block.sprite, (block.x - self.camera_x, block.y - self.camera_y, block.width, block.height))
		pygame.display.flip()

	def main_loop(self):
		while self.game_running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.game_running = False
			key_dict = pygame.key.get_pressed()
			if key_dict[pygame.K_ESCAPE]:
				self.game_running = False
			if key_dict[pygame.K_SPACE]:
				self.player.move(DIRECTION_UP)
			if key_dict[pygame.K_d]:
				self.player.move(DIRECTION_RIGHT)
			if key_dict[pygame.K_a]:
				self.player.move(DIRECTION_LEFT)
			if not key_dict[pygame.K_d] and not key_dict[pygame.K_a]:
				self.player.move(NO_DIRECTION_X)
			self.physical_engine()
			self.render_frame()
			self.clock.tick(FRAMES_PER_SECOND)


world = World()
world.main_loop()

