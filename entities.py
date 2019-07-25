import pygame
import math

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

class Skeleton(Entity):
    def __init__(self, x, y, vx, vy, ax, ay, sprites, target):
        Entity.__init__(self, x, y, vx, vy, ax, ay, 56, 94, sprites[0])
        self.target = target
        self.move_speed = 3
        self.jump_speed = 17
        self.can_jump = True
        self.movement_sprites = sprites
        self.movement_animation_index = 0
        self.attack_damage = 10
        self.attack_knockback_x = 0
        self.attack_knockback_y = 0

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
            if self.target.hitbox.colliderect(self.hitbox) and self.target.invincibility_frame == 0:
                self.target.hp -= self.attack_damage
                self.target.invincibility_frame = self.target.max_invincibility_frame
                self.target.vx = -self.attack_knockback_x
                self.target.vy = -self.attack_knockback_y
        elif 0 <= self.target.x - self.x < 40 and abs(self.y - self.target.y) < 40:
            self.movement_animation_index = 17
            self.sprite = self.movement_sprites[5]

    def iterate(self):
        self.approach_target()
        self.attack_target()
