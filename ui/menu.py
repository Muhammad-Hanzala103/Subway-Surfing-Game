"""
Menu System - Enhanced with better visuals
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
import math


class MenuSystem:
    """Enhanced game menus"""
    
    def __init__(self, window):
        self.window = window
        self.animation_time = 0.0
        
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        self.text_cache = {}  # { (text, color_tuple): (tex_id, w, h) }
        
        self.shop_menu = None # initialized by game manager to avoid circular import issues or set later
    
    def set_game_manager(self, game_manager):
        from .shop import ShopMenu
        self.shop_menu = ShopMenu(self, game_manager)
    
    def update(self, delta_time):
        self.animation_time += delta_time
    
    def _get_cached_text(self, text, font, color):
        """Get or create cached text texture"""
        # color can be variable due to pulsing, caching only exact matches
        cache_key = (text, tuple(color))
        
        if cache_key in self.text_cache:
            return self.text_cache[cache_key]
            
        surface = font.render(text, True, color)
        text_data = pygame.image.tostring(surface, "RGBA", False)
        w, h = surface.get_size()
        
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        self.text_cache[cache_key] = (tex_id, w, h)
        return tex_id, w, h

    def render_text(self, text, font, color, position, center=False):
        """Render text to screen using cache"""
        tex_id, w, h = self._get_cached_text(text, font, color)
        
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        x, y = position
        if center:
            x -= w // 2
        
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glEnable(GL_TEXTURE_2D)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        
        glPopAttrib()
        
        return (w, h)
    
    def setup_2d(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.window.width, 0, self.window.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
    
    def restore_3d(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def draw_gradient_background(self, color_top, color_bottom):
        """Draw animated gradient background"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glBegin(GL_QUADS)
        glColor4f(*color_bottom)
        glVertex2f(0, 0)
        glVertex2f(self.window.width, 0)
        glColor4f(*color_top)
        glVertex2f(self.window.width, self.window.height)
        glVertex2f(0, self.window.height)
        glEnd()
    
    def draw_main_menu(self):
        """Draw animated main menu"""
        self.setup_2d()
        
        # Animated gradient background
        pulse = 0.5 + 0.1 * math.sin(self.animation_time * 2)
        self.draw_gradient_background(
            (0.1, 0.05, 0.2 + pulse * 0.1, 0.95),
            (0.05, 0.1, 0.15, 0.95)
        )
        
        cx = self.window.width // 2
        
        # Animated title
        title_offset = math.sin(self.animation_time * 3) * 5
        self.render_text("RAIL RUNNERS", self.font_title,
                        (51, 153, 255), (cx, self.window.height - 100 + title_offset), center=True)
        
        # Subtitle with glow effect
        glow = int(200 + 55 * math.sin(self.animation_time * 4))
        self.render_text("URBAN ESCAPE", self.font_medium,
                        (255, glow, 51), (cx, self.window.height - 160), center=True)
        
        # Feature list (Centered)
        features = [
            "🎮 Endless Runner Action",
            "🚂 Dynamic World & Fog",
            "💎 Coins & Power-ups",
            "🛹 Upgradable Gear",
            "🏆 High Score System"
        ]
        
        # Draw features going DOWN from middle
        y = self.window.height - 200
        for feature in features:
            self.render_text(feature, self.font_small,
                           (200, 200, 220), (cx, y), center=True)
            y -= 40
            
        # Pulsing start button
        pulse_scale = 1.0 + 0.05 * math.sin(self.animation_time * 5)
        alpha = int(200 + 55 * math.sin(self.animation_time * 3))
        self.render_text("Press ENTER to Start", self.font_large,
                        (255, 255, alpha), (cx, 160), center=True)

        # Shop Hint (Separate from Start text)
        shop_glow = int(200 + 55 * math.sin(self.animation_time * 8))
        self.render_text("[S] OPEN SHOP", self.font_medium,
                        (51, 255, 51), (cx, 120), center=True)
        
        # Controls
        self.render_text("Controls:", self.font_small,
                        (150, 150, 150), (cx, 70), center=True)
        self.render_text("A/D - Move | W/Space - Jump | S - Slide | ESC - Pause", self.font_small,
                        (120, 120, 120), (cx, 40), center=True)
        
        self.restore_3d()
    
    def draw_shop(self):
        """Draw shop menu"""
        if self.shop_menu:
            self.shop_menu.draw()

    def draw_pause_menu(self):
        
        # Dark overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.75)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.window.width, 0)
        glVertex2f(self.window.width, self.window.height)
        glVertex2f(0, self.window.height)
        glEnd()
        
        cx = self.window.width // 2
        cy = self.window.height // 2
        
        # Pulsing pause text
        pulse = int(200 + 55 * math.sin(self.animation_time * 4))
        self.render_text("PAUSED", self.font_title,
                        (255, 255, pulse), (cx, cy + 60), center=True)
        
        self.render_text("Press ESC to Resume", self.font_medium,
                        (180, 180, 180), (cx, cy - 20), center=True)
        
        self.restore_3d()
    
    def draw_game_over(self, game_manager):
        """Draw enhanced game over screen"""
        self.setup_2d()
        
        # Dark red overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.15, 0.0, 0.0, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.window.width, 0)
        glVertex2f(self.window.width, self.window.height)
        glVertex2f(0, self.window.height)
        glEnd()
        
        cx = self.window.width // 2
        stats = game_manager.score.get_stats()
        
        # Title with shake effect
        shake = 3 * math.sin(self.animation_time * 20) if self.animation_time < 0.5 else 0
        self.render_text("GAME OVER", self.font_title,
                        (255, 60, 60), (cx + shake, self.window.height - 120), center=True)
        
        # New high score?
        if stats['score'] == stats['high_score'] and stats['score'] > 0:
            glow = int(200 + 55 * math.sin(self.animation_time * 6))
            self.render_text("NEW HIGH SCORE!", self.font_medium,
                           (255, glow, 50), (cx, self.window.height - 180), center=True)
        
        # Stats panel
        y = self.window.height // 2 + 100
        
        self.render_text(f"Score: {stats['score']:,}", self.font_large,
                        (255, 255, 255), (cx, y), center=True)
        y -= 50
        
        self.render_text(f"High Score: {stats['high_score']:,}", self.font_medium,
                        (255, 215, 0), (cx, y), center=True)
        y -= 40
        
        self.render_text(f"Distance: {stats['distance']}m", self.font_small,
                        (200, 200, 200), (cx, y), center=True)
        y -= 30
        
        self.render_text(f"Coins: {stats['coins']}", self.font_small,
                        (255, 215, 0), (cx, y), center=True)
        y -= 30
        
        if stats['near_misses'] > 0:
            self.render_text(f"Near Misses: {stats['near_misses']}", self.font_small,
                           (100, 255, 150), (cx, y), center=True)
            y -= 30
        
        if stats['powerups'] > 0:
            self.render_text(f"Power-ups: {stats['powerups']}", self.font_small,
                           (150, 150, 255), (cx, y), center=True)
        
        # Revive option
        if game_manager.can_revive and game_manager.score.coins >= game_manager.revive_cost:
            pulse = int(200 + 55 * math.sin(self.animation_time * 5))
            self.render_text(f"Press R to Revive ({game_manager.revive_cost} coins)", self.font_medium,
                           (100, 255, pulse), (cx, 130), center=True)
        
        # Restart prompt
        self.render_text("Press ENTER to Restart", self.font_medium,
                        (100, 255, 100), (cx, 80), center=True)
        
        self.render_text("Press ESC for Menu", self.font_small,
                        (150, 150, 150), (cx, 45), center=True)
        
        self.restore_3d()
