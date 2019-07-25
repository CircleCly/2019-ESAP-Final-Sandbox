import pygame
import random
from block import *
from entities import *

#Game Constant
DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3
NO_DIRECTION_X = 4
PLAYER_INIT_X = 800
PLAYER_INIT_Y = 2900
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
skeleton_sprites.append(pygame.image.load('skeleton_attack_left.png'))
skeleton_sprites.append(pygame.image.load('skeleton_attack_right.png'))
selected_block = pygame.image.load('selected_block.png')


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
		self.max_hp = 100
		self.hp = 100
		self.invincibility_frame = 0
		self.max_invincibility_frame = 30

	def move(self, direction):
		key_dict=pygame.key.get_pressed()
		if direction == DIRECTION_LEFT:
			if key_dict[pygame.K_LSHIFT]:
				self.vx = - 2*self.move_speed
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

	def get_center_x(self):
		return self.x + self.width // 2

	def get_center_y(self):
		return self.y + self.height // 2


class World():
	def __init__(self):
		self.clock = pygame.time.Clock()
		self.player = Player(PLAYER_INIT_X, PLAYER_INIT_Y, 0, 0, 0, 0, movement_sprites=protagonist_walk_sprites)
		self.game_running = True
		self.camera_x = self.player.x - GAME_FRAME_WIDTH / 2
		self.camera_y = self.player.y - GAME_FRAME_HEIGHT / 2
		self.map = []
		self.highlight_selected_block = True
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
		self.entities = []
		self.monster_count = 0
		self.chosen_block = None
		self.player_died = False
	# Updates the chosen_block attribute
	def update_chosen_block(self):
		if math.sqrt((pygame.mouse.get_pos()[0] + self.camera_x - self.player.get_center_x()) ** 2 \
					 + (pygame.mouse.get_pos()[1] + self.camera_y - self.player.get_center_y()) ** 2) > 120:
			self.chosen_block = None
			return
		chosen_block_position_x = max(0, min(299, (pygame.mouse.get_pos()[0] + self.camera_x) // 20))
		chosen_block_position_y = max(0, min(299, (pygame.mouse.get_pos()[1] + self.camera_y) // 20))
		self.chosen_block = self.map[int(chosen_block_position_y)][int(chosen_block_position_x)]
		if self.chosen_block.block_type == 0:
			self.chosen_block = None
	def spawn_monster(self):
		if random.random() < 0.1 and self.monster_count <= 10:
			spawn_area = pygame.rect.Rect(random.randint(-800, -500) + self.player.x if random.random() < 0.5 \
			else random.randint(500, 800) + self.player.x , \
			self.player.y + random.randint(150, 210), 100, 100)
			able_to_spawn = True
			for i in range(max(0, spawn_area.y // 20), min(300, spawn_area.y // 20 + 5)):
				for j in range(max(0, spawn_area.x // 20), min(300,spawn_area.x // 20 + 5)):
					if self.map[i][j].hitbox.colliderect(spawn_area) and not self.map[i][j].can_pass_through:
						able_to_spawn = False
						break
				if not able_to_spawn:
					break
			if able_to_spawn:
				skeleton = Skeleton(spawn_area.x, spawn_area.y, 0,
									0, 0, 0, skeleton_sprites, self.player)
				self.entities.append(skeleton)
				self.monster_count += 1
				print("Enemy spawned! Current enemies: ", self.monster_count)

	def despawn_monster(self):
		for entity in self.entities:
			if math.sqrt((entity.x - self.player.x) ** 2 + (entity.y - self.player.y) ** 2) > 2000:
				self.entities.remove(entity)
				self.monster_count -= 1

	def iterate_entities(self):
		for entity in self.entities:
			entity.iterate()

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
		for row in self.current_chunk:
			for block in row:
				if future_hitbox_x.colliderect(block.hitbox) and not block.can_pass_through:
					will_collide_x = True
				if future_hitbox_y.colliderect(block.hitbox) and not block.can_pass_through:
					will_collide_y = True
		self.player.can_jump = will_collide_y
		if not will_collide_x:
			self.player.x += self.player.vx
		else:
			self.player.vx = 0
		if not will_collide_y:
			self.player.y += self.player.vy
		else:
			self.player.vy = 0
		self.player.hitbox = pygame.rect.Rect((self.player.x, self.player.y), (self.player.width, self.player.height))
		for i in range(0, len(self.entities)):
			entity = self.entities[i]
			if entity.vy < 5:
				entity.ay = 0.5
			else:
				entity.ay = 0
			entity.vx += entity.ax
			entity.vy += entity.ay
			future_hitbox_x = pygame.rect.Rect((entity.x + entity.vx, entity.y),
											   (entity.width, entity.height))
			future_hitbox_y = pygame.rect.Rect((entity.x, entity.y + entity.vy),
											   (entity.width, entity.height))
			will_collide_x = False
			will_collide_y = False
			for row in self.current_chunk:
				for block in row:
					if future_hitbox_x.colliderect(block.hitbox) and not block.can_pass_through:
						will_collide_x = True
					if future_hitbox_y.colliderect(block.hitbox) and not block.can_pass_through:
						will_collide_y = True
			entity.can_jump = will_collide_y
			if not will_collide_x:
				entity.x += entity.vx
			if not will_collide_y:
				entity.y += entity.vy
			entity.hitbox = pygame.rect.Rect((entity.x, entity.y),
											(entity.width, entity.height))

	def update_current_chunk(self):
		self.current_chunk = []
		for r in range(max(0, int(self.camera_y // 20 - 40)), min(299, int(self.camera_y // 20 + 40))):
			current_row = []
			for c in range(max(0, int(self.camera_x // 20 - 50)), min(1999, int(self.camera_x // 20 + 50))):
				current_row.append(self.map[r][c])
			self.current_chunk.append(current_row)

	def render_frame(self):
		self.camera_x = self.player.x + self.player.width // 2 - GAME_FRAME_WIDTH // 2
		self.camera_y = self.player.y + self.player.height // 2 - GAME_FRAME_HEIGHT // 2
		screen.blit(background,(0, 0))

		for row in self.current_chunk:
			# If block is in camera range
			for block in row:
				if self.camera_x - block.width <= block.x <= self.camera_x + GAME_FRAME_WIDTH \
					and self.camera_y - block.height <= block.y <= self.camera_y + GAME_FRAME_HEIGHT:
					screen.blit(block.sprite, (block.x - self.camera_x, block.y - self.camera_y, block.width, block.height))
		# If the position chosen is close enough to the center of player, show highlight
		if self.chosen_block is not None and self.highlight_selected_block:
			# Highlight selected block at the proper position
				screen.blit(selected_block, (self.chosen_block.x - self.camera_x , self.chosen_block.y - self.camera_y, 20, 20))
		for entity in self.entities:
			# If entity is in camera range
			if self.camera_x - entity.width <= entity.x <= self.camera_x + GAME_FRAME_WIDTH \
				and self.camera_y - entity.height <= entity.y <= self.camera_y + GAME_FRAME_HEIGHT:
				screen.blit(entity.sprite, (entity.x - self.camera_x, entity.y - self.camera_y, entity.width, entity.height))
		if self.player.invincibility_frame % 2 == 0:
			screen.blit(self.player.sprite, (GAME_FRAME_WIDTH // 2 - self.player.width // 2, GAME_FRAME_HEIGHT // 2 - self.player.height // 2))
		pygame.draw.rect(screen, (255, 0, 0), pygame.rect.Rect(GAME_FRAME_WIDTH - 200, 0, (self.player.hp / self.player.max_hp) * 200, 15))
		if self.chosen_block is not None:
			pygame.draw.rect(screen, (255, 255, 0), \
			pygame.rect.Rect(self.player.get_center_x() - self.camera_x - 50, self.player.y - self.camera_y - 25, 100 - (self.chosen_block.hp / self.chosen_block.max_hp) * 100, 15))
		pygame.display.flip()

	def destroy_blocks(self):
		# Determine whether the player's mouse is in reach of the player
		# If selected block is too far, the block will not be destroyed
		if self.chosen_block is None:
			return
		if self.chosen_block.hp > 0:
			if self.chosen_block.block_type == 1:
				self.chosen_block.hp -= 50
			elif self.chosen_block.block_type == 2:
				self.chosen_block.hp -= 100
			elif self.chosen_block.block_type == 3:
				self.chosen_block.hp -= 35
			elif self.chosen_block.block_type == 4:
				self.chosen_block.hp -= 35
			elif self.chosen_block.block_type == 5:
				self.chosen_block.hp -= 100
			elif self.chosen_block.block_type == 6:
				self.chosen_block.hp -= 25
			elif self.chosen_block.block_type == 7:
				self.chosen_block.hp -= 15
			elif self.chosen_block.block_type == 8:
				self.chosen_block.hp -= 15
			elif self.chosen_block.block_type == 9:
				self.chosen_block.hp -= 10
			elif self.chosen_block.block_type == 10:
				self.chosen_block.hp -= 5
			elif self.chosen_block.block_type == 11:
				self.chosen_block.hp -= 35
		if self.chosen_block.hp <= 0:
			self.chosen_block.block_type = 0
			self.chosen_block.sprite = block_sprites[0]
			self.chosen_block.can_pass_through = True

	def main_loop(self):
		while self.game_running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.game_running = False
			if not self.player_died:
				if self.player.hp <= 0:
					self.player_died = True
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
				if self.player.invincibility_frame > 0:
					self.player.invincibility_frame -= 1
				self.update_chosen_block()
				self.spawn_monster()
				self.despawn_monster()
				self.iterate_entities()
				self.physical_engine()
				if pygame.mouse.get_pressed() == (1, 0, 0) or pygame.mouse.get_pressed() == (1, 0, 1) or \
					pygame.mouse.get_pressed() == (1, 1, 0) or pygame.mouse.get_pressed() == (1, 1, 1):
					self.destroy_blocks()
				self.update_current_chunk()
				self.render_frame()
				self.clock.tick(FRAMES_PER_SECOND)


world = World()
world.main_loop()

