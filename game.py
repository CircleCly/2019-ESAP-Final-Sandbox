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
map_file = open("map.mp","r")

#Game Resources
protagonist_walk_sprites = []
for i in range(1,6):
	protagonist_walk_sprites.append(pygame.image.load('protagonist_walk_'+str(i)+'.png'))
background = pygame.image.load('background.png')
block_sprites = []
for i in range(0,12):
	block_sprites.append(pygame.image.load("block_"+str(i)+".png"))
skeleton_sprites = []
for i in range(1,5):
	skeleton_sprites.append(pygame.image.load('skeleton'+str(i)+".png"))
#selected_block = pygame.image.load('selected_block.png')

class Entity(pygame.sprite.Sprite):
	def __init__(self, x, y, vx, vy, ax, ay, width, height, sprite):
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.ax = ax
		self.ay = ay
		self.sprite = sprite
		self.width = width
		self.height = height
		self.hitbox = pygame.rect.Rect((x, y), (self.width, self.height))

class Player(Entity):
	def __init__(self, x, y, vx, vy, ax, ay, movement_sprites):
		Entity.__init__(self, x, y, vx, vy, ax, ay, 56, 94, movement_sprites[0])
		self.movement_sprites = movement_sprites
		self.movement_animation_index = 0
		self.move_speed = 5
		self.jump_speed = 17
		self.can_jump = True
		self.width = 56
		self.height = 94

	def move(self, direction):
		key_dict=pygame.key.get_pressed()
		if direction == DIRECTION_LEFT:
			if key_dict[pygame.K_LSHIFT]:
				self.vx  - 2*self.move_speed
			else:
				self.vx = - self.move_speed
			self.movement_animation_index += 1
		elif direction == DIRECTION_RIGHT:
			if key_dict[pygame.K_LSHIFT]:
				self.vx = 2*self.move_speed
			else:
				self.vx = self.move_speed
			self.movement_animation_index += 1
		elif direction == DIRECTION_UP:
			if self.can_jump:
				self.vy = -self.jump_speed
				self.can_jump = False
		elif direction == NO_DIRECTION_X:
			self.vx = 0
		if self.movement_animation_index > 19:
			self.movement_animation_index = 0
		self.sprite = self.movement_sprites[self.movement_animation_index // 4]

class World():
	def __init__(self):
		self.clock = pygame.time.Clock()
		self.player = Player(PLAYER_INIT_X, PLAYER_INIT_Y, 0, 0, 0, 0, movement_sprites=protagonist_walk_sprites)
		self.game_running = True
		self.camera_x = self.player.x - GAME_FRAME_WIDTH / 2
		self.camera_y = self.player.y - GAME_FRAME_HEIGHT / 2
		self.map = []
		for row in range(0, 300):
			line = map_file.readline()
			line = line.split(" ")
			line = [int(x) for x in line if x != "\n"]
			current_row = []
			for col in range(0, len(line)):
				current_block = line[col]
				current_x = col * 20
				current_y = row * 20
				block = Block(current_x, current_y, block_sprites[line[col]], line[col])
				if line[col] == 0 or line[col] == 2:
					block.can_pass_through = True
				current_row.append(block)
			self.map.append(current_row)
		self.current_chunk = []

	def physical_engine(self, destroy):
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
		for row in self.current_chunk:
			for block in row:
				if future_hitbox_x.colliderect(block.hitbox) and not block.can_pass_through:
					will_collide_x = True
				if future_hitbox_y.colliderect(block.hitbox) and not block.can_pass_through:
					will_collide_y = True
		self.player.can_jump = will_collide_y
		if not will_collide_x:
			self.player.x += self.player.vx
		if not will_collide_y:
			self.player.y += self.player.vy
		if destroy == True:
			x=int((pygame.mouse.get_pos()[0]+self.camera_x)//20)
			y=int((pygame.mouse.get_pos()[1]+self.camera_y)//20)
			if y>=300:
				y=299
			if x>=2000:
				x=1999
			if y<0:
				y=0
			if x<0:
				x=0
			if self.map[y][x].hp>0:
				if self.map[y][x].block_type==1:
					self.map[y][x].hp-=50
				elif self.map[y][x].block_type==2:
					self.map[y][x].hp-=100
				elif self.map[y][x].block_type==3:
					self.map[y][x].hp-=35
				elif self.map[y][x].block_type==4:
					self.map[y][x].hp-=35
				elif self.map[y][x].block_type==5:
					self.map[y][x].hp-=100
				elif self.map[y][x].block_type==6:
					self.map[y][x].hp-=25
				elif self.map[y][x].block_type==7:
					self.map[y][x].hp-=15
				elif self.map[y][x].block_type==8:
					self.map[y][x].hp-=15
				elif self.map[y][x].block_type==9:
					self.map[y][x].hp-=10
				elif self.map[y][x].block_type==10:
					self.map[y][x].hp-=5
				elif self.map[y][x].block_type==11:
					self.map[y][x].hp-=35
			if self.map[y][x].hp<=0:
				self.map[y][x].block_type=0
				self.map[y][x].sprite=block_sprites[0]
				self.map[y][x].can_pass_through=True
		return self.map

		self.player.hitbox = pygame.rect.Rect((self.player.x, self.player.y), (self.player.width, self.player.height))

	def update_current_chunk(self):
		self.current_chunk = []
		for r in range(max(0, int(self.camera_y // 20)), min(300, int(self.camera_y // 20 + 40))):
			current_row = []
			for c in range(max(0, int(self.camera_x // 20)), min(2000, int(self.camera_x // 20 + 50))):
				current_row.append(self.map[r][c])
			self.current_chunk.append(current_row)

	def render_frame(self):
		self.camera_x = self.player.x + self.player.width // 2 - GAME_FRAME_WIDTH // 2
		self.camera_y = self.player.y + self.player.height // 2 - GAME_FRAME_HEIGHT // 2
		screen.blit(background,(0, 0))
		current_movement_frame = self.player.sprite
		screen.blit(current_movement_frame, (GAME_FRAME_WIDTH // 2 - self.player.width // 2, GAME_FRAME_HEIGHT // 2 - self.player.height // 2))
		for row in self.current_chunk:
			# If block is in camera range
			for block in row:
				if self.camera_x - block.width <= block.x <= self.camera_x + GAME_FRAME_WIDTH \
					and self.camera_y - block.height <= block.y <= self.camera_y + GAME_FRAME_HEIGHT:
					screen.blit(block.sprite, (block.x - self.camera_x, block.y - self.camera_y, block.width, block.height))
		pygame.display.flip()
	def main_loop(self):
		while self.game_running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.game_running = False
			destroy = False
			pygame.event.get()
			if pygame.mouse.get_pressed()==(1,0,0) or pygame.mouse.get_pressed()==(1,0,1) or \
			pygame.mouse.get_pressed()==(1,1,0) or pygame.mouse.get_pressed()==(1,1,1):
				destroy=True
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
			self.map=self.physical_engine(destroy)
			self.update_current_chunk()
			self.render_frame()
			self.clock.tick(FRAMES_PER_SECOND)
world = World()
world.main_loop()