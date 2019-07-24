from game import Entity
import pygame
class Skeleton(Entity):
    def __init__(self, x, y, vx, vy, ax, ay, sprites, target):
        Entity.__init__(self, x, y, vx, vy, ax, ay, 56, 94, sprites[0])
        self.target = target
        self.move_speed = 3
        self.jump_speed = 17
        self.can_jump = True
        self.movement_sprites = sprites
        self.movement_animation_index = 0

    def approach_target(self):
        if self.target.x > self.x:
            self.vx = self.move_speed
            self.movement_animation_index += 1
        elif self.target.x < self.x:
            self.vx = -self.move_speed
            self.movement_animation_index += 1
        if self.target.y < self.y:
            if self.can_jump:
                self.vy += -self.jump_speed
                self.can_jump = False
        if self.movement_animation_index > 15:
            self.movement_animation_index = 0
        self.sprite = self.movement_sprites[self.movement_animation_index // 4]

    def attack_player(self):
        if self.x - self.target.x < 50 and abs(self.y - self.target.y) < 40:
            self.movement_animation_index = 16
            self.sprite = self.movement_sprites[4]
        elif self.target.x - self.x < 50 and abs(self.y - self.target.y) < 40:
            self.movement_animation_index = 17
            self.sprite = self.movement_sprites[5]
