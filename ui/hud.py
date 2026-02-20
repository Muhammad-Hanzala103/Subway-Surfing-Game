"""
HUD - Enhanced In-game heads-up display
Shows all power-ups, combo, and advanced stats
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
import config


class HUD:
    """Enhanced in-game heads-up display"""
    
    def __init__(self, window):
        self.window = window
        
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        self.font_combo = pygame.font.Font(None, 80)
        
        self.text_cache = {}  # { (text, color_tuple): (tex_id, w, h) }
        
    def _get_cached_text(self, text, font, color):
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
        
        return w, h
    
    def draw_bar(self, x, y, width, height, fill_percent, color, bg_color=(0.2, 0.2, 0.2, 0.8)):
        """Draw a progress bar"""
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Background
        glColor4f(*bg_color)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Fill
        fill_width = width * fill_percent
        glColor4f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + fill_width, y)
        glVertex2f(x + fill_width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Border
        glColor4f(1, 1, 1, 0.5)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        glPopAttrib()
    
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
    
    def draw(self, game_manager):
        """Draw the complete HUD"""
        self.setup_2d()
        
        score = game_manager.score.get_score()
        coins = game_manager.score.get_coins()
        distance = game_manager.score.get_distance()
        combo = game_manager.collectibles.combo_count
        active_powerups = game_manager.get_active_powerups()
        
        # Score (top right)
        self.render_text(f"{score:,}", self.font_large, 
                        (255, 255, 255), (self.window.width - 200, self.window.height - 55))
        self.render_text("SCORE", self.font_small,
                        (180, 180, 180), (self.window.width - 200, self.window.height - 25))
        
        # Coins (below score)
        self.render_text(f"{coins}", self.font_medium,
                        (255, 215, 0), (self.window.width - 120, self.window.height - 95))
        
        # Distance (top left)
        self.render_text(f"{distance}m", self.font_medium,
                        (200, 200, 200), (20, self.window.height - 50))
        
        # Combo display (center-ish)
        if combo >= 3:
            combo_color = (255, 200, 50) if combo < 10 else (255, 100, 50) if combo < 20 else (255, 50, 255)
            self.render_text(f"x{combo}", self.font_combo,
                           combo_color, (self.window.width // 2, self.window.height - 100), center=True)
            mult = game_manager.collectibles.get_combo_multiplier()
            if mult > 1:
                self.render_text(f"{mult:.1f}X MULTIPLIER", self.font_small,
                               combo_color, (self.window.width // 2, self.window.height - 140), center=True)
        
        # Power-up indicators (left side)
        y_offset = self.window.height - 120
        for name, timer in active_powerups:
            # Background bar
            max_time = config.POWERUP_DURATION
            fill = min(1.0, timer / max_time)
            
            # Color based on powerup
            if 'MAGNET' in name:
                bar_color = (0.8, 0.2, 0.8, 0.9)
            elif 'SHIELD' in name:
                bar_color = (0.2, 0.8, 0.8, 0.9)
            elif 'SCORE' in name:
                bar_color = (0.2, 0.8, 0.2, 0.9)
            elif 'HOVERBOARD' in name:
                bar_color = (1.0, 0.5, 0.0, 0.9)
            elif 'JETPACK' in name:
                bar_color = (1.0, 0.2, 0.2, 0.9)
            elif 'SUPER' in name:
                bar_color = (0.0, 1.0, 0.5, 0.9)
            else:
                bar_color = (0.5, 0.5, 0.5, 0.9)
            
            self.draw_bar(20, y_offset, 150, 25, fill, bar_color)
            self.render_text(name, self.font_small, (255, 255, 255), (25, y_offset + 3))
            
            y_offset -= 35
        
        # Near miss notification (would flash)
        if game_manager.player.near_miss_timer > 0:
            self.render_text("NEAR MISS!", self.font_medium,
                           (100, 255, 150), (self.window.width // 2, self.window.height // 2 + 50), center=True)
        
        self.restore_3d()
    
    def draw_fps(self, fps):
        """Draw FPS counter"""
        self.setup_2d()
        self.render_text(f"FPS: {int(fps)}", self.font_small,
                        (100, 100, 100), (20, 20))
        self.restore_3d()
    
    def draw_slow_motion_indicator(self):
        """Draw slow motion effect indicator"""
        self.setup_2d()
        
        # Vignette-like effect text
        self.render_text("SLOW MOTION", self.font_medium,
                        (100, 150, 255), (self.window.width // 2, 50), center=True)
        
        self.restore_3d()
