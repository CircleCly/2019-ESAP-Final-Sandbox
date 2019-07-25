import pygame

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

