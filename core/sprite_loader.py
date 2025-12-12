import pygame
import os

class SpriteLoader:
    def __init__(self, sprite_dir='resources/sprites'):
        self.sprite_dir = sprite_dir
        self.sprites = {}
        self.load_sprites()
    
    def load_sprites(self):
        """Load all sprites from the sprite directory"""
        for filename in os.listdir(self.sprite_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(self.sprite_dir, filename)
                try:
                    sprite = pygame.image.load(path).convert_alpha()
                    self.sprites[filename] = sprite
                except pygame.error:
                    print(f"Could not load sprite: {path}")
    
    def get_sprite(self, filename):
        """Get sprite by filename"""
        return self.sprites.get(filename)
    
    def get_scaled_sprite(self, filename, size):
        """Get scaled sprite"""
        sprite = self.get_sprite(filename)
        if sprite:
            return pygame.transform.scale(sprite, size)
        return None