import pygame
import random
import math

#Game Constant
DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3
NO_DIRECTION_X = 4
PLAYER_INIT_X = 20000
PLAYER_INIT_Y = 2700
FRAMES_PER_SECOND = 60
GAME_FRAME_WIDTH = 800
GAME_FRAME_HEIGHT = 600
# Initialize the game
screen = pygame.display.set_mode((GAME_FRAME_WIDTH,GAME_FRAME_HEIGHT))
pygame.display.set_caption('Sandbox!')
map_file = open("map.mp","r")

#Game Resources
pygame.init()
writing_font = pygame.font.SysFont("Comic Sans MS", 15)

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
wooden_sword_sprites = []
wooden_sword_sprites.append(pygame.image.load('wooden_sword_right.png'))
wooden_sword_sprites.append(pygame.image.load('wooden_sword_left.png'))
wooden_pickaxe_sprites = []
wooden_pickaxe_sprites.append(pygame.image.load('wooden_pickaxe_right.png'))
wooden_pickaxe_sprites.append(pygame.image.load('wooden_pickaxe_left.png'))
inventory_slot = pygame.image.load('inventory_slot.png')
highlighted_inventory_slot = pygame.image.load('highlighted_inventory_slot.png')
arrow_left = pygame.image.load('arrow_left.png')
arrow_right = pygame.image.load('arrow_right.png')
wooden_bow_sprites = []
wooden_bow_sprites.append(pygame.image.load('wooden_bow_left.png'))
wooden_bow_sprites.append(pygame.image.load('wooden_bow_right.png'))
dynamite_monster_sprites = []
dynamite_monster_sprites.append(pygame.image.load('dynamite_monster.png'))
explosion = pygame.image.load('explosion.png')
lava_monster_sprites = []
lava_monster_sprites.append(pygame.image.load('lava_monster.png'))
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
		self.affected_by_gravity = True
		self.hp = 1
		self.max_hp = 1

class Item():
	def __init__(self, sprite, name, width, height, owner):
		self.number = 1
		self.name = name
		self.sprite = sprite
		self.use_frames = 15
		self.width = width
		self.height = height
		self.owner = owner

class ItemEntity(Entity):
	def __init__(self, x, y, width, height, sprite, item):
		self.item = item
		Entity.__init__(self, x, y, 0, 0, 0, 0, width, height, sprite)
		
class BowItem(Item):
	def __init__(self, sprites, name, width, height, owner):
		Item.__init__(self, sprites[0], name, width, height, owner)
		self.number = 1
		self.damage = 3
		self.use_frames = 15
		self.sprites = sprites
		
	def attack(self, direction):
		bow_entity = BowEntity(self, self.owner, direction)
		bow_entity.affected_by_gravity = False
		world.entities.append(bow_entity)
		if direction == DIRECTION_RIGHT:
			arrow = Arrow(bow_entity.x + bow_entity.width, \
						  bow_entity.y + bow_entity.height // 2 - 9, 27, self.damage + self.owner.damage_bonus)
			arrow.affected_by_gravity = False
			world.entities.append(arrow)
		elif direction == DIRECTION_LEFT:
			arrow = Arrow(bow_entity.x, bow_entity.y + bow_entity.height // 2 - 9,\
						  -27 , self.damage + self.owner.damage_bonus)
			arrow.affected_by_gravity = False
			world.entities.append(arrow)

class BowEntity(ItemEntity):
	def __init__(self, bow, attacker, attack_direction):
		self.attacker = attacker
		if attack_direction == DIRECTION_LEFT:
			ItemEntity.__init__(self, attacker.x  - bow.width, attacker.y + 25, \
								bow.width, bow.height, bow.sprites[0], bow)
			self.direction = DIRECTION_LEFT
			self.lasting_time = bow.use_frames
		elif attack_direction == DIRECTION_RIGHT:
			ItemEntity.__init__(self, attacker.x + attacker.width, attacker.y + 25, \
								bow.width, bow.height, bow.sprites[1], bow)
			self.direction = DIRECTION_RIGHT
			self.lasting_time = bow.use_frames
		self.bow = bow
		self.attack_direction = attack_direction

	def iterate(self):
		if self.attack_direction == DIRECTION_LEFT:
			self.x , self.y = self.attacker.x  - self.bow.width, self.attacker.y + 25
		elif self.attack_direction == DIRECTION_RIGHT:
			self.x , self.y = self.attacker.x + self.attacker.width, self.attacker.y + 25
		if self.lasting_time > 0:
			self.lasting_time -= 1
		else:
			self.hp = 0

class Arrow(Entity):
	def __init__(self, x, y, speed, damage):
		self.lasting_time = 600
		Entity.__init__(self, x, y, speed, 0, 0, 0, 61, 18, arrow_right)
		if speed < 0:
			self.sprite = arrow_left
		else:
			self.sprite = arrow_right
		self.vx = speed
		self.damage = damage
	def iterate(self):

		for row in world.current_chunk:
			for block in row:
				if self.hitbox.colliderect(block.hitbox) and not block.can_pass_through:
					self.hp = 0
		for entity in world.entities:
			if isinstance(entity, Enemy) and self.hitbox.colliderect(entity.hitbox):
				entity.hp -= self.damage
				self.hp = 0
				if entity.hp < 0:
					entity.hp = 0
		if self.lasting_time > 0:
			self.lasting_time -= 1
		else:
			self.hp = 0

class SwordItem(Item):
	def __init__(self, sprites, name, width, height, owner, attack_times):
		Item.__init__(self, sprites[0], name, width, height, owner)
		self.number = 1
		self.damage = 6
		self.use_frames = 15
		self.sprites = sprites
		self.attack_times = attack_times

	def attack(self, attack_direction):
		sword_entity = SwordEntity(self, self.owner, attack_direction)
		sword_entity.affected_by_gravity = False
		world.entities.append(sword_entity)

class SwordEntity(ItemEntity):
	def __init__(self, sword, attacker, attack_direction):
		self.attacker = attacker
		if attack_direction == DIRECTION_LEFT:
			ItemEntity.__init__(self, attacker.x + 3 - sword.width, attacker.y + 45, \
							sword.width, sword.height, sword.sprites[1], sword)
			self.direction = DIRECTION_LEFT
			self.lasting_time = sword.use_frames
		elif attack_direction == DIRECTION_RIGHT:
			ItemEntity.__init__(self, attacker.x + attacker.width, attacker.y + 45, \
							sword.width, sword.height, sword.sprites[0], sword)
			self.direction = DIRECTION_RIGHT
			self.lasting_time = sword.use_frames
		self.sword = sword
		self.attack_times = sword.attack_times

	def iterate(self):
		if self.direction == DIRECTION_LEFT:
			self.x = self.attacker.x + 3 - self.width
			self.y = self.attacker.y + 45
		elif self.direction == DIRECTION_RIGHT:
			self.x = self.attacker.x + self.attacker.width
			self.y = self.attacker.y + 45
		hit_enemy = False
		for potential_enemy in world.entities:
			if isinstance(potential_enemy, Enemy) \
					and potential_enemy.hitbox.colliderect(self.hitbox)\
					and self.attack_times > 0:
				potential_enemy.hp -= self.sword.damage + self.attacker.damage_bonus
				if potential_enemy.hp < 0:
					potential_enemy.hp = 0
				hit_enemy = True
		if hit_enemy:
			self.attack_times -= 1
		if self.lasting_time > 0:
			self.lasting_time -= 1
		else:
			self.hp = 0

class PickaxeItem(Item):
	def __init__(self, sprites, name, width, height, owner):
		Item.__init__(self, sprites[0], name, width, height, owner)
		self.use_frames = 15
		self.sprites = sprites
		
	def use(self, use_direction):
		pickaxe_entity = PickaxeEntity(self, self.owner, use_direction)
		pickaxe_entity.affected_by_gravity = False
		world.entities.append(pickaxe_entity)
		
class PickaxeEntity(ItemEntity):
	def __init__(self, pickaxe, user, use_direction):
		self.user = user
		if use_direction == DIRECTION_LEFT:
			ItemEntity.__init__(self, user.x - pickaxe.width, user.y + 3, \
							 pickaxe.width, pickaxe.height, pickaxe.sprites[1], pickaxe)
			self.lasting_time = pickaxe.use_frames
		if use_direction == DIRECTION_RIGHT:
			ItemEntity.__init__(self, user.x + user.width, user.y + 3, \
							pickaxe.width, pickaxe.height, pickaxe.sprites[0], pickaxe)
			self.lasting_time = pickaxe.use_frames
		self.direction = use_direction
	def iterate(self):
		if self.direction == DIRECTION_LEFT:
			self.x , self.y = self.user.x - self.width, self.user.y + 3
		elif self.direction == DIRECTION_RIGHT:
			self.x , self.y = self.user.x + self.user.width, self.user.y + 3
		if self.lasting_time > 0:
			self.lasting_time -= 1
		else:
			self.hp = 0

class BlockItem(Item):
	def __init__(self, sprite, name, owner, block_type):
		Item.__init__(self, sprite, name, 20, 20, owner)
		self.block_type = block_type

	def place(self, map_grid_x, map_grid_y):
		placed_block = Block(map_grid_x * 20, map_grid_y * 20, self.sprite, self.block_type)
		world.map[map_grid_y][map_grid_x] = placed_block
		self.number -= 1

class Inventory():
	def __init__(self, owner):
		self.swords = []
		self.swords.append(SwordItem(wooden_sword_sprites, "Wooden Sword", 63, 19, owner, 1))
		self.current_sword = 0
		self.pickaxes = []
		self.pickaxes.append(PickaxeItem(wooden_pickaxe_sprites, "Wooden Pickaxe", 54, 54, owner))
		self.current_pickaxe = 0
		self.blocks = []
		stone_blocks = BlockItem(block_sprites[6], "Stone Block", owner, 6)
		stone_blocks.number = 100
		self.blocks.append(stone_blocks)
		self.current_block = 0
		self.bows = []
		self.current_bow = 0
		wooden_bow = BowItem(wooden_bow_sprites, "Wooden Bow", 12, 56, owner)
		self.bows.append(wooden_bow)
		self.current_item = 0
class Player(Entity):
	def __init__(self, x, y, vx, vy, ax, ay, movement_sprites):
		Entity.__init__(self, x, y, vx, vy, ax, ay, 56, 94, movement_sprites[0])
		self.movement_sprites = movement_sprites
		self.movement_animation_index = 0
		self.move_speed = 5
		self.jump_speed = 11
		self.can_jump = True
		self.width = 56
		self.height = 94
		self.max_hp = 100
		self.hp = 100
		self.use_item_time = 0
		self.invincibility_frame = 0
		self.max_invincibility_frame = 30
		self.inventory = Inventory(self)
		self.score = 0
		self.healing_delay = 0
		self.max_healing_delay = 300
		self.healing_speed = 60
		self.healing_timer = 1
		self.damage_bonus = 0

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

	def strike_with_sword(self, direction):
		if self.use_item_time <= 0 and self.can_use_again:
			sword = self.inventory.swords[self.inventory.current_sword]
			sword.attack(direction)
			self.use_item_time = sword.use_frames
			self.can_use_again = False

	def dig_with_pickaxe(self, direction):
		if self.use_item_time <= 0 and self.can_use_again:
			pickaxe = self.inventory.pickaxes[self.inventory.current_pickaxe]
			pickaxe.use(direction)
			self.use_item_time = pickaxe.use_frames
			self.can_use_again = True
	def shoot_with_bow(self, direction):
		if self.use_item_time <= 0 and self.can_use_again:
			bow = self.inventory.bows[self.inventory.current_pickaxe]
			bow.attack(direction)
			self.use_item_time = bow.use_frames
			self.can_use_again = True
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
		self.chosen_block = Block(0, 0, None, 0)
		self.has_chosen_block = True
		self.player_died = False

	def get_clicked_distance_to_player(self):
		return math.sqrt((pygame.mouse.get_pos()[0] + self.camera_x - self.player.get_center_x()) ** 2 \
					 + (pygame.mouse.get_pos()[1] + self.camera_y - self.player.get_center_y()) ** 2)
	# Updates the chosen_block attribute
	def update_chosen_block(self):
		if self.get_clicked_distance_to_player()> 120:
			self.has_chosen_block = False
			return
		chosen_block_position_x = max(0, min(1999, (pygame.mouse.get_pos()[0] + self.camera_x) // 20))
		chosen_block_position_y = max(0, min(299, (pygame.mouse.get_pos()[1] + self.camera_y) // 20))
		self.chosen_block = self.map[int(chosen_block_position_y)][int(chosen_block_position_x)]
		self.has_chosen_block = True

	def spawn_monster(self):
		if random.random() < (0.0025 * (1 / 2) ** self.monster_count) and self.monster_count <= 10:
			spawn_area = pygame.rect.Rect(random.randint(-600, -300) + self.player.x if random.random() < 0.5 \
			else random.randint(300, 600) + self.player.x , \
			self.player.y - random.randint(150, 210), 100, 100)
			able_to_spawn = True
			for i in range(max(0, spawn_area.y // 20), min(299, spawn_area.y // 20 + 6)):
				for j in range(max(0, spawn_area.x // 20), min(1999,spawn_area.x // 20 + 6)):
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
		if random.random() < 0.0005 * (1 / 2) ** self.monster_count and self.monster_count <= 10:
			spawn_area = pygame.rect.Rect(random.randint(-600, -300) + self.player.x if random.random() < 0.5 \
											  else random.randint(300, 600) + self.player.x, \
										  self.player.y - random.randint(150, 210), 100, 100)
			able_to_spawn = True
			for i in range(max(0, spawn_area.y // 20), min(299, spawn_area.y // 20 + 6)):
				for j in range(max(0, spawn_area.x // 20), min(1999, spawn_area.x // 20 + 6)):
					if self.map[i][j].hitbox.colliderect(spawn_area) and not self.map[i][j].can_pass_through:
						able_to_spawn = False
						break
				if not able_to_spawn:
					break
			if able_to_spawn:
				dynamite_monster = DynamiteMonster(spawn_area.x, spawn_area.y, \
												   0, 0, 0, 0, dynamite_monster_sprites, self.player)
				self.entities.append(dynamite_monster)
				self.monster_count += 1
		if random.random() < 0.0005 * (1 / 2) ** self.monster_count and self.monster_count <= 10:
			spawn_area = pygame.rect.Rect(random.randint(-600, -300) + self.player.x if random.random() < 0.5 \
										else random.randint(300, 600) + self.player.x, \
										self.player.y - random.randint(150, 210), 100, 100)
			able_to_spawn = True
			for i in range(max(0, spawn_area.y // 20), min(299, spawn_area.y // 20 + 6)):
				for j in range(max(0, spawn_area.x // 20), min(1999, spawn_area.x // 20 + 6)):
					if self.map[i][j].hitbox.colliderect(spawn_area) and not self.map[i][j].can_pass_through:
						able_to_spawn = False
						break
				if not able_to_spawn:
					break
			if able_to_spawn:
				lava_monster = LavaMonster(spawn_area.x, spawn_area.y, \
												   0, 0, 0, 0, lava_monster_sprites, self.player)
				self.entities.append(lava_monster)
				self.monster_count += 1

	def despawn_monster(self):
		for entity in self.entities:
			if math.sqrt((entity.x - self.player.x) ** 2 + (entity.y - self.player.y) ** 2) > 2000:
				self.entities.remove(entity)
				self.monster_count -= 1

	def iterate_entities(self):
		for entity in self.entities:
			entity.iterate()
			if entity.hp <= 0:
				self.entities.remove(entity)
				if isinstance(entity, Enemy):
					self.monster_count -= 1
					if isinstance(entity, Skeleton):
						self.player.score += 5
					if isinstance(entity, LavaMonster):
						self.player.score += 15
					if isinstance(entity, DynamiteMonster):
						self.player.score += 3


	def physical_engine(self):
		# Gravity
		if self.player.vy < 5:
			self.player.ay = 0.7
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
			if entity.affected_by_gravity:
				if entity.vy < 5 :
					entity.ay = 0.7
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
			if not isinstance(entity, Arrow):
				if not will_collide_x:
					entity.x += entity.vx
				if not will_collide_y:
					entity.y += entity.vy
			else:
				entity.x += entity.vx
				entity.y += entity.vy
			entity.hitbox = pygame.rect.Rect((entity.x, entity.y),
											(entity.width, entity.height))

	def update_current_chunk(self):
		self.current_chunk = []
		for r in range(max(0, int(self.camera_y // 20 - 50)), min(299, int(self.camera_y // 20 + 50))):
			current_row = []
			for c in range(max(0, int(self.camera_x // 20 - 70)), min(1999, int(self.camera_x // 20 + 70))):
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
		if self.has_chosen_block:
			# If the position chosen is close enough to the center of player, show highlight
			if self.chosen_block.block_type != 0 and self.highlight_selected_block \
				and self.player.inventory.current_item == 1:
				# Highlight selected block at the proper position
					screen.blit(selected_block, (self.chosen_block.x - self.camera_x , self.chosen_block.y - self.camera_y, 20, 20))
			if self.chosen_block.block_type == 0 and self.highlight_selected_block \
				and self.player.inventory.current_item == 2:
				screen.blit(selected_block,
							(self.chosen_block.x - self.camera_x, self.chosen_block.y - self.camera_y, 20, 20))
		for entity in self.entities:
			# If entity is in camera range
			if self.camera_x - entity.width <= entity.x <= self.camera_x + GAME_FRAME_WIDTH \
				and self.camera_y - entity.height <= entity.y <= self.camera_y + GAME_FRAME_HEIGHT:
				if isinstance(entity, ItemEntity) and entity.item.owner.hp <= 0:
					continue
				screen.blit(entity.sprite, (entity.x - self.camera_x, entity.y - self.camera_y, entity.width, entity.height))
				if isinstance(entity, Enemy):
					health_percentage = entity.hp / entity.max_hp
					pygame.draw.rect(screen, ((1 - health_percentage) * 255, health_percentage * 255, 60), pygame.rect.Rect(\
					entity.x - self.camera_x - 22, entity.y - self.camera_y - 35, 100 * health_percentage, 15 ))
					if isinstance(entity, DynamiteMonster) and entity.activated:
						screen.blit(writing_font.render(str(entity.explosion_timer // 60 + 1), True, [255, 0, 0]),
									(entity.x + 15 - self.camera_x, entity.y - 65 - self.camera_y, 50, 25))
		if self.player.invincibility_frame % 2 == 0:
			screen.blit(self.player.sprite, (GAME_FRAME_WIDTH // 2 - self.player.width // 2, GAME_FRAME_HEIGHT // 2 - self.player.height // 2))
		pygame.draw.rect(screen, (255, 0, 0), pygame.rect.Rect(GAME_FRAME_WIDTH - 200, 0, (self.player.hp / self.player.max_hp) * 200, 15))
		if self.chosen_block is not None and self.player.inventory.current_item == 1:
			pygame.draw.rect(screen, (255, 255, 0), \
			pygame.rect.Rect(self.player.get_center_x() - self.camera_x - 50, self.player.y - self.camera_y - 25, 100 - (self.chosen_block.hp / self.chosen_block.max_hp) * 100, 15))
		# Draws the inventory
		screen.blit(inventory_slot, (0, 0, 64, 64))
		screen.blit(inventory_slot, (70, 0, 64, 64))
		screen.blit(inventory_slot, (140, 0, 64, 64))
		screen.blit(inventory_slot, (210, 0, 64, 64))
		if self.player.inventory.current_item == 0:
			screen.blit(highlighted_inventory_slot, (0, 0, 64, 64))
		elif self.player.inventory.current_item == 1:
			screen.blit(highlighted_inventory_slot, (70, 0, 64, 64))
		elif self.player.inventory.current_item == 2:
			screen.blit(highlighted_inventory_slot, (140, 0, 64, 64))
		elif self.player.inventory.current_item == 3:
			screen.blit(highlighted_inventory_slot, (210, 0, 64, 64))
		sword = self.player.inventory.swords[self.player.inventory.current_sword]
		screen.blit(sword.sprite,(0 + 32 - sword.width // 2, 0 + 32 - sword.height // 2))
		pickaxe = self.player.inventory.pickaxes[self.player.inventory.current_pickaxe]
		screen.blit(pickaxe.sprite, (70 + 32 - pickaxe.width // 2, 0 + 32 - pickaxe.height // 2))
		block = self.player.inventory.blocks[self.player.inventory.current_block]
		screen.blit(block.sprite, (140 + 32 - block.width // 2, 0 + 32 - block.height // 2))
		screen.blit(writing_font.render(str(block.number), True, [255, 255, 255] ), (140 + 64 - 25, 64 - 18, 25, 25))
		bow = self.player.inventory.bows[self.player.inventory.current_bow]
		screen.blit(bow.sprite, (210 + 32 - bow.width // 2, 0 + 32 - bow.height // 2))
		screen.blit(writing_font.render("Your score: "+str(self.player.score), True, [255, 0, 0]), (GAME_FRAME_WIDTH // 2 - 40, 0, 75, 25))
		pygame.display.flip()

	def destroy_blocks(self):
		# Determine whether the player's mouse is in reach of the player
		# If selected block is too far, the block will not be destroyed
		if not self.has_chosen_block:
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
			if self.chosen_block.block_type == 6:
				self.player.inventory.blocks[self.player.inventory.current_block].number += 1
			if self.chosen_block.block_type == 7:
				self.player.damage_bonus += 1
			elif self.chosen_block.block_type == 8:
				self.player.damage_bonus += 2
			elif self.chosen_block.block_type == 9:
				self.player.damage_bonus += 3
			elif self.chosen_block.block_type == 10:
				self.player.damage_bonus += 4
			self.chosen_block.block_type = 0
			self.chosen_block.sprite = block_sprites[0]
			self.chosen_block.can_pass_through = True
			self.chosen_block.hp = self.chosen_block.max_hp

	def place_block(self):
		current_block = self.player.inventory.blocks[self.player.inventory.current_block]
		if self.chosen_block.block_type != 0 \
				or current_block.number <= 0\
				or self.chosen_block.hitbox.colliderect(self.player.hitbox)\
				or self.player.use_item_time > 0\
				or not self.has_chosen_block:
			return
		current_block.number -= 1
		self.chosen_block.block_type = current_block.block_type
		self.chosen_block.sprite = current_block.sprite
		self.chosen_block.can_pass_through = False
		self.player.use_item_time = 30

	def save_map(self):
		with open("map.mp","w") as map_file_write_stream:
			for row in self.map:
				for block in row:
					map_file_write_stream.write(str(block.block_type)+" ")
				map_file_write_stream.write("\n")

	def handle_user_input(self):
		key_dict = pygame.key.get_pressed()
		if key_dict[pygame.K_ESCAPE]:
			self.game_running = False
			self.save_map()
		if key_dict[pygame.K_SPACE]:
			self.player.move(DIRECTION_UP)
		if key_dict[pygame.K_d]:
			self.player.move(DIRECTION_RIGHT)
		if key_dict[pygame.K_a]:
			self.player.move(DIRECTION_LEFT)
		if not key_dict[pygame.K_d] and not key_dict[pygame.K_a]:
			self.player.move(NO_DIRECTION_X)
		if key_dict[pygame.K_1]:
			self.player.inventory.current_item = 0
		if key_dict[pygame.K_2]:
			self.player.inventory.current_item = 1
		if key_dict[pygame.K_3]:
			self.player.inventory.current_item = 2
		if key_dict[pygame.K_4]:
			self.player.inventory.current_item = 3
		if pygame.mouse.get_pressed()[0] == 1:
			if self.player.inventory.current_item == 0:
				if pygame.mouse.get_pos()[0] <= GAME_FRAME_WIDTH // 2:
					self.player.strike_with_sword(DIRECTION_LEFT)
				else:
					self.player.strike_with_sword(DIRECTION_RIGHT)
			elif self.player.inventory.current_item == 1:
				if pygame.mouse.get_pos()[0] <= GAME_FRAME_WIDTH // 2:
					self.player.dig_with_pickaxe(DIRECTION_LEFT)
				else:
					self.player.dig_with_pickaxe(DIRECTION_RIGHT)
				self.destroy_blocks()
			elif self.player.inventory.current_item == 2:
				self.place_block()
			elif self.player.inventory.current_item == 3:
				if pygame.mouse.get_pos()[0] <= GAME_FRAME_WIDTH // 2:
					self.player.shoot_with_bow(DIRECTION_LEFT)
				else:
					self.player.shoot_with_bow(DIRECTION_RIGHT)
		if pygame.mouse.get_pressed()[0] == 0:
			self.player.can_use_again = True

	def do_player_healing(self):
		if self.player.healing_delay > 0:
			self.player.healing_delay -= 1
		else:
			if self.player.healing_timer > 0:
				self.player.healing_timer -= 1
			else:
				if self.player.hp < self.player.max_hp:
					self.player.hp += 1
				self.player.healing_timer = self.player.healing_speed

	def message_display(self, text1, text2):
		pygame.init()
		font = pygame.font.SysFont("Courier New", 70)
		text1 = font.render(text1, True, (100,0,0))
		font1 = pygame.font.SysFont("Courier New", 25)
		text2 = font1.render(text2, True, (100,0,0))
		screen.fill((255, 255, 255))
		screen.blit(text1, (GAME_FRAME_WIDTH//2-140, 100))
		screen.blit(text2, (GAME_FRAME_WIDTH//2-300, 400))

	def main_loop(self):
		in_Game = False
		while self.game_running:
			if in_Game==True:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.game_running = False
						self.save_map()
				if not self.player_died:
					if self.player.hp <= 0:
						self.player_died = True
						in_Game = False
					self.update_chosen_block()
					self.handle_user_input()
					if self.player.invincibility_frame > 0:
						self.player.invincibility_frame -= 1
					if self.player.use_item_time > 0:
						self.player.use_item_time -= 1
					self.spawn_monster()
					self.despawn_monster()
					self.physical_engine()
					self.do_player_healing()
					self.iterate_entities()
					self.update_current_chunk()
					self.render_frame()
					self.clock.tick(FRAMES_PER_SECOND)
			if in_Game == False:
				self.message_display("Survive", "Press space to play.   Press ESC to quit.")
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						self.game_running = False
				key_dict = pygame.key.get_pressed()
				if key_dict[pygame.K_ESCAPE]:
					self.game_running = False
				if key_dict[pygame.K_SPACE]:
					in_Game = True
					self.player_died = False
					self.player.hp = self.player.max_hp
					self.player.score = 0
					self.player.x = PLAYER_INIT_X
					self.player.y = PLAYER_INIT_Y
					self.player.damage_bonus = 0
					self.entities.clear()
					self.monster_count=0
					self.score=0
				pygame.display.flip()


class Enemy(Entity):
	def __init__(self, x, y, vx, vy, ax, ay, width, height, sprites, target):
		self.target = target
		self.sprites = sprites
		Entity.__init__(self, x, y, vx, vy, ax, ay, width, height, sprites[0])


class DynamiteMonster(Enemy):
	def __init__(self, x, y, vx, vy, ax, ay, sprites, target):
		Enemy.__init__(self, x, y, vx, vy, ax, ay, 56, 94, sprites, target)
		self.target = target
		self.move_speed = 2
		self.jump_speed = 7
		self.can_jump = True
		self.max_hp = 22
		self.hp = 22
		self.explosion_timer = 180
		self.activated = False

	def approach_target(self):
		if math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2) > 900:
			self.vx = 0
			return
		if self.target.x > self.x:
			self.vx = self.move_speed
		elif self.target.x < self.x:
			self.vx = -self.move_speed
		if self.target.y < self.y:
			if self.can_jump:
				self.vy = -self.jump_speed
				self.can_jump = False

	def check_activate(self):
		if math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2) < 140:
			self.activated = True

	def explode(self):
		self.hp = 0
		world.entities.append(Explosion(self.x + self.width // 2 - 80, self.y + self.height // 2 - 80,
										160, 160, 5, explosion))

	def iterate(self):
		self.approach_target()
		self.check_activate()
		if self.activated and self.explosion_timer > 0:
			self.explosion_timer -= 1
		if self.activated and self.explosion_timer <= 0:
			self.explode()


class Explosion(Entity):
	def __init__(self, x, y, width, height, lasting_time, sprite):
		Entity.__init__(self, x, y, 0, 0, 0, 0, width, height, sprite)
		self.lasting_time = lasting_time

	def iterate(self):
		for row in world.current_chunk:
			for block in row:
				if block.hitbox.colliderect(self.hitbox):
					block.block_type = 0
					block.sprite = block_sprites[0]
					block.can_pass_through = True
					block.hp = block.max_hp
		if world.player.hitbox.colliderect(self.hitbox) and world.player.invincibility_frame <= 0:
			world.player.hp -= 20
			if world.player.hp < 0:
				world.player.hp = 0
		for entity in world.entities:
			if entity.hitbox.colliderect(self.hitbox) and not isinstance(entity, DynamiteMonster) and not isinstance(entity, Explosion):
				entity.hp -= 20
				if entity.hp < 0:
					entity.hp = 0
		if self.lasting_time > 0:
			self.lasting_time -= 1
		else:
			self.hp = 0

class LavaMonster(Enemy):
	def __init__(self, x, y, vx, vy, ax, ay, sprites, target):
		Enemy.__init__(self, x, y, vx, vy, ax, ay, 60, 60, sprites, target)
		self.target = target
		self.move_speed = 3
		self.jump_speed = 7
		self.can_jump = True
		self.movement_sprites = sprites
		self.movement_animation_index = 0
		self.attack_damage = 33
		self.attack_knockback_x = 0
		self.attack_knockback_y = 0
		self.max_hp = 40
		self.hp = 40

	def approach_target(self):
		if math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2) > 900:
			self.vx = 0
			return
		if self.target.x > self.x:
			self.vx = self.move_speed
		elif self.target.x < self.x:
			self.vx = -self.move_speed
		if self.target.y < self.y:
			if self.can_jump:
				self.vy = -self.jump_speed
				self.can_jump = False

	def attack_target(self):
		if self.target.hitbox.colliderect(self.hitbox) and self.target.invincibility_frame == 0:
			self.target.hp -= self.attack_damage
			self.target.invincibility_frame = self.target.max_invincibility_frame
			self.target.healing_delay = self.target.max_healing_delay
			self.target.healing_timer = self.target.healing_speed
			self.target.vx = -self.attack_knockback_x
			self.target.vy = -self.attack_knockback_y

	def iterate(self):
		self.approach_target()
		self.attack_target()

class Skeleton(Enemy):
	def __init__(self, x, y, vx, vy, ax, ay, sprites, target):
		Enemy.__init__(self, x, y, vx, vy, ax, ay, 56, 94, sprites, target)
		self.target = target
		self.move_speed = 5
		self.jump_speed = 8
		self.can_jump = True
		self.movement_sprites = sprites
		self.movement_animation_index = 0
		self.attack_damage = 10
		self.attack_knockback_x = 0
		self.attack_knockback_y = 0
		self.max_hp = 30
		self.hp = 30

	def approach_target(self):
		if math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2) > 900:
			self.vx = 0
			return
		if self.target.x > self.x:
			self.vx = self.move_speed
			self.movement_animation_index += 1
		elif self.target.x < self.x:
			self.vx = -self.move_speed
			self.movement_animation_index += 1
		if self.target.y < self.y:
			if self.can_jump:
				self.vy = -self.jump_speed
				self.can_jump = False
		if self.movement_animation_index > 15:
			self.movement_animation_index = 0
		self.sprite = self.movement_sprites[self.movement_animation_index // 4]

	def attack_target(self):
		if 0 <= self.x - self.target.x < 40 and abs(self.y - self.target.y) < 40:
			self.movement_animation_index = 16
			self.sprite = self.movement_sprites[4]
		elif 0 <= self.target.x - self.x < 40 and abs(self.y - self.target.y) < 40:
			self.movement_animation_index = 17
			self.sprite = self.movement_sprites[5]
		if self.target.hitbox.colliderect(self.hitbox) and self.target.invincibility_frame == 0:
			self.target.hp -= self.attack_damage
			self.target.invincibility_frame = self.target.max_invincibility_frame
			self.target.healing_delay = self.target.max_healing_delay
			self.target.healing_timer = self.target.healing_speed
			self.target.vx = -self.attack_knockback_x
			self.target.vy = -self.attack_knockback_y

	def iterate(self):
		self.approach_target()
		self.attack_target()

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite, block_type):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.sprite = sprite
        self.block_type = block_type
        self.hitbox = pygame.rect.Rect((x, y), (self.width, self.height))
        self.can_pass_through = False
        self.hp = 1000
        self.max_hp = 1000

world = World()
world.main_loop()

