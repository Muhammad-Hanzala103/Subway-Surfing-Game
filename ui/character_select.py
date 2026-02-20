"""
Character Selection Menu
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
import math
import numpy as np

from game.character import Character, CharacterType, CharacterManager


class CharacterSelectMenu:
    """Character selection UI"""
    
    def __init__(self, window, character_manager):
        self.window = window
        self.char_manager = character_manager
        self.active = False
        self.animation_time = 0.0
        
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 64)
        self.font_name = pygame.font.Font(None, 48)
        self.font_desc = pygame.font.Font(None, 32)
        self.font_stats = pygame.font.Font(None, 28)
        self.font_hint = pygame.font.Font(None, 24)
    
    def open(self):
        self.active = True
    
    def close(self):
        self.active = False
    
    def handle_input(self, events, available_coins=0):
        """Handle input, returns action or None"""
        if not self.active:
            return None
        
        for event_type, event_data in events:
            if event_type == 'keydown':
                key = event_data
                
                if key in [K_a, K_LEFT]:
                    self.char_manager.select_previous()
                
                elif key in [K_d, K_RIGHT]:
                    self.char_manager.select_next()
                
                elif key == K_RETURN:
                    selected = self.char_manager.get_selected()
                    
                    if selected.is_unlocked:
                        self.char_manager.confirm_selection()
                        self.close()
                        return 'selected'
                    else:
                        # Try to unlock
                        cost = self.char_manager.try_unlock(
                            Character.get_all_characters()[self.char_manager.selected_index],
                            available_coins
                        )
                        if cost > 0:
                            return ('unlock', cost)
                
                elif key == K_ESCAPE:
                    self.close()
                    return 'back'
        
        return None
    
    def update(self, delta_time):
        self.animation_time += delta_time
    
    def render_text(self, text, font, color, position, center=False):
        """Render text"""
        surface = font.render(str(text), True, color)
        text_data = pygame.image.tostring(surface, "RGBA", False)
        
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(),
                     surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        x, y = position
        w, h = surface.get_size()
        
        if center:
            x -= w // 2
        
        glEnable(GL_TEXTURE_2D)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        
        glDeleteTextures(1, [tex_id])
        glPopAttrib()
    
    def draw_character_preview(self, char, x, y, size, is_selected):
        """Draw character preview box"""
        # Box background
        if is_selected:
            pulse = 0.7 + 0.3 * math.sin(self.animation_time * 5)
            glColor4f(char.color[0] * 0.3 * pulse, 
                     char.color[1] * 0.3 * pulse,
                     char.color[2] * 0.3 * pulse, 0.8)
        else:
            glColor4f(0.15, 0.15, 0.2, 0.6)
        
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + size, y)
        glVertex2f(x + size, y + size)
        glVertex2f(x, y + size)
        glEnd()
        
        # Character color representation
        char_size = size * 0.5
        char_x = x + (size - char_size) / 2
        char_y = y + (size - char_size) / 2 + 10
        
        # Rotation animation for selected
        if is_selected:
            rotate_offset = math.sin(self.animation_time * 3) * 5
            char_x += rotate_offset
        
        glColor4f(*char.color)
        glBegin(GL_QUADS)
        glVertex2f(char_x, char_y)
        glVertex2f(char_x + char_size, char_y)
        glVertex2f(char_x + char_size, char_y + char_size)
        glVertex2f(char_x, char_y + char_size)
        glEnd()
        
        # Border
        if is_selected:
            glColor4f(1.0, 1.0, 1.0, 0.8)
            glLineWidth(3)
        else:
            glColor4f(0.5, 0.5, 0.5, 0.5)
            glLineWidth(1)
        
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + size, y)
        glVertex2f(x + size, y + size)
        glVertex2f(x, y + size)
        glEnd()
        
        # Lock icon if not unlocked
        if not char.is_unlocked:
            glColor4f(0.0, 0.0, 0.0, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(x, y)
            glVertex2f(x + size, y)
            glVertex2f(x + size, y + size)
            glVertex2f(x, y + size)
            glEnd()
            
            self.render_text("🔒", self.font_name, (255, 200, 50),
                           (x + size/2, y + size/2), center=True)
    
    def draw(self, available_coins=0):
        """Draw character selection screen"""
        if not self.active:
            return
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.window.width, 0, self.window.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Background
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.05, 0.05, 0.1, 0.95)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.window.width, 0)
        glVertex2f(self.window.width, self.window.height)
        glVertex2f(0, self.window.height)
        glEnd()
        
        cx = self.window.width // 2
        
        # Title
        self.render_text("SELECT CHARACTER", self.font_title,
                        (100, 180, 255), (cx, self.window.height - 70), center=True)
        
        # Coins display
        self.render_text(f"Coins: {available_coins}", self.font_stats,
                        (255, 215, 0), (self.window.width - 150, self.window.height - 40))
        
        # Character grid
        chars = self.char_manager.get_character_list()
        char_size = 120
        spacing = 20
        total_width = len(chars) * (char_size + spacing) - spacing
        start_x = (self.window.width - total_width) // 2
        
        for i, char_info in enumerate(chars):
            char = Character(char_info['type'])
            x = start_x + i * (char_size + spacing)
            y = self.window.height // 2 + 20
            
            is_selected = i == self.char_manager.selected_index
            self.draw_character_preview(char, x, y, char_size, is_selected)
            
            # Name below
            name_color = (255, 255, 255) if is_selected else (150, 150, 150)
            self.render_text(char.name, self.font_stats, name_color,
                           (x + char_size/2, y - 25), center=True)
        
        # Selected character info
        selected = self.char_manager.get_selected()
        
        info_y = 200
        
        # Name
        self.render_text(selected.name, self.font_name,
                        (255, 255, 255), (cx, info_y + 60), center=True)
        
        # Description
        self.render_text(selected.description, self.font_desc,
                        (180, 180, 180), (cx, info_y + 20), center=True)
        
        # Stats
        stats_text = []
        if selected.speed_bonus > 0:
            stats_text.append(f"Speed +{int(selected.speed_bonus * 100)}%")
        if selected.jump_bonus > 0:
            stats_text.append(f"Jump +{int(selected.jump_bonus * 100)}%")
        if selected.magnet_bonus > 0:
            stats_text.append(f"Magnet +{int(selected.magnet_bonus * 100)}%")
        
        if stats_text:
            self.render_text("  |  ".join(stats_text), self.font_stats,
                           (100, 255, 150), (cx, info_y - 15), center=True)
        
        # Action hint
        if selected.is_unlocked:
            self.render_text("Press ENTER to select", self.font_hint,
                           (100, 200, 100), (cx, 80), center=True)
        else:
            self.render_text(f"Press ENTER to unlock ({selected.cost} coins)", self.font_hint,
                           (255, 200, 100), (cx, 80), center=True)
        
        # Navigation hints
        self.render_text("A/D: Navigate | ENTER: Select | ESC: Back", self.font_hint,
                        (120, 120, 120), (cx, 40), center=True)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
