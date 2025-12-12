import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, MIN_ZOOM, MAX_ZOOM, ZOOM_FACTOR

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.smooth_zoom = 1.0
    
    def apply(self, pos):
        """Apply camera transformation to position"""
        x, y = pos
        x = (x - self.x) * self.zoom
        y = (y - self.y) * self.zoom
        return x, y
    
    def apply_rect(self, rect):
        """Apply camera transformation to rectangle"""
        x, y = self.apply((rect.x, rect.y))
        w = rect.width * self.zoom
        h = rect.height * self.zoom
        return pygame.Rect(x, y, w, h)
    
    def update(self, target_x=None, target_y=None):
        """Update camera position and zoom"""
        # Smooth zoom interpolation
        if abs(self.target_zoom - self.smooth_zoom) > 0.01:
            self.smooth_zoom += (self.target_zoom - self.smooth_zoom) * 0.1
            self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.smooth_zoom))
    
    def move(self, dx, dy):
        """Move camera"""
        self.x += dx / self.zoom
        self.y += dy / self.zoom
    
    def set_position(self, x, y):
        """Set camera position"""
        self.x = x
        self.y = y
    
    def set_zoom(self, zoom_level):
        """Set zoom level"""
        self.target_zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom_level))
    
    def zoom_in(self):
        """Zoom in"""
        self.target_zoom = min(MAX_ZOOM, self.target_zoom * ZOOM_FACTOR)
    
    def zoom_out(self):
        """Zoom out"""
        self.target_zoom = max(MIN_ZOOM, self.target_zoom / ZOOM_FACTOR)