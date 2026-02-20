"""
Settings Menu - Volume, Graphics, Controls
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
import json
import os
import math


class Settings:
    """Game settings storage"""
    
    SETTINGS_FILE = "settings.json"
    
    DEFAULT = {
        'music_volume': 0.5,
        'sfx_volume': 0.7,
        'show_fps': True,
        'show_tutorial': True,
        'particles_enabled': True,
        'screen_shake': True,
        'difficulty': 'normal'  # easy, normal, hard
    }
    
    def __init__(self):
        self.data = self.DEFAULT.copy()
        self.load()
    
    def load(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save(self):
        """Save settings to file"""
        try:
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key):
        return self.data.get(key, self.DEFAULT.get(key))
    
    def set(self, key, value):
        self.data[key] = value
        self.save()


class SettingsMenu:
    """Settings menu UI"""
    
    def __init__(self, window):
        self.window = window
        self.settings = Settings()
        self.active = False
        self.selected_index = 0
        
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 64)
        self.font_option = pygame.font.Font(None, 40)
        self.font_value = pygame.font.Font(None, 36)
        self.font_hint = pygame.font.Font(None, 28)
        
        # Menu options
        self.options = [
            {'key': 'music_volume', 'name': 'Music Volume', 'type': 'slider', 'min': 0, 'max': 1, 'step': 0.1},
            {'key': 'sfx_volume', 'name': 'SFX Volume', 'type': 'slider', 'min': 0, 'max': 1, 'step': 0.1},
            {'key': 'show_fps', 'name': 'Show FPS', 'type': 'toggle'},
            {'key': 'particles_enabled', 'name': 'Particles', 'type': 'toggle'},
            {'key': 'screen_shake', 'name': 'Screen Shake', 'type': 'toggle'},
            {'key': 'show_tutorial', 'name': 'Show Tutorial', 'type': 'toggle'},
            {'key': 'difficulty', 'name': 'Difficulty', 'type': 'choice', 'choices': ['easy', 'normal', 'hard']},
            {'key': 'back', 'name': '< Back', 'type': 'action'}
        ]
    
    def open(self):
        self.active = True
        self.selected_index = 0
    
    def close(self):
        self.active = False
        self.settings.save()
    
    def handle_input(self, events):
        """Handle menu input"""
        if not self.active:
            return None
        
        for event_type, event_data in events:
            if event_type == 'keydown':
                key = event_data
                
                # Navigation
                if key in [K_w, K_UP]:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif key in [K_s, K_DOWN]:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                
                # Selection/Change
                option = self.options[self.selected_index]
                
                if key in [K_a, K_LEFT]:
                    self._change_option(option, -1)
                elif key in [K_d, K_RIGHT]:
                    self._change_option(option, 1)
                elif key in [K_RETURN, K_SPACE]:
                    if option['type'] == 'toggle':
                        current = self.settings.get(option['key'])
                        self.settings.set(option['key'], not current)
                    elif option['type'] == 'action':
                        if option['key'] == 'back':
                            self.close()
                            return 'back'
                
                if key == K_ESCAPE:
                    self.close()
                    return 'back'
        
        return None
    
    def _change_option(self, option, direction):
        """Change option value"""
        if option['type'] == 'slider':
            current = self.settings.get(option['key'])
            new_value = current + direction * option['step']
            new_value = max(option['min'], min(option['max'], new_value))
            self.settings.set(option['key'], round(new_value, 2))
        
        elif option['type'] == 'toggle':
            current = self.settings.get(option['key'])
            self.settings.set(option['key'], not current)
        
        elif option['type'] == 'choice':
            choices = option['choices']
            current = self.settings.get(option['key'])
            try:
                idx = choices.index(current)
            except ValueError:
                idx = 0
            new_idx = (idx + direction) % len(choices)
            self.settings.set(option['key'], choices[new_idx])
    
    def render_text(self, text, font, color, position, center=False):
        """Render text"""
        surface = font.render(text, True, color)
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
    
    def draw(self, time):
        """Draw settings menu"""
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
        glColor4f(0.1, 0.1, 0.15, 0.95)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.window.width, 0)
        glVertex2f(self.window.width, self.window.height)
        glVertex2f(0, self.window.height)
        glEnd()
        
        cx = self.window.width // 2
        
        # Title
        self.render_text("SETTINGS", self.font_title,
                        (100, 180, 255), (cx, self.window.height - 80), center=True)
        
        # Options
        y = self.window.height - 160
        
        for i, option in enumerate(self.options):
            is_selected = i == self.selected_index
            
            # Highlight
            if is_selected:
                pulse = 0.6 + 0.4 * math.sin(time * 5)
                glColor4f(0.2 * pulse, 0.3 * pulse, 0.5 * pulse, 0.5)
                glBegin(GL_QUADS)
                glVertex2f(cx - 250, y - 5)
                glVertex2f(cx + 250, y - 5)
                glVertex2f(cx + 250, y + 35)
                glVertex2f(cx - 250, y + 35)
                glEnd()
            
            # Option name
            name_color = (255, 255, 255) if is_selected else (180, 180, 180)
            self.render_text(option['name'], self.font_option,
                           name_color, (cx - 200, y))
            
            # Option value
            if option['type'] == 'slider':
                value = self.settings.get(option['key'])
                # Draw slider bar
                bar_x = cx + 50
                bar_y = y + 10
                bar_width = 150
                bar_height = 15
                
                # Background
                glColor4f(0.3, 0.3, 0.3, 1.0)
                glBegin(GL_QUADS)
                glVertex2f(bar_x, bar_y)
                glVertex2f(bar_x + bar_width, bar_y)
                glVertex2f(bar_x + bar_width, bar_y + bar_height)
                glVertex2f(bar_x, bar_y + bar_height)
                glEnd()
                
                # Fill
                fill_width = bar_width * value
                glColor4f(0.3, 0.6, 1.0, 1.0)
                glBegin(GL_QUADS)
                glVertex2f(bar_x, bar_y)
                glVertex2f(bar_x + fill_width, bar_y)
                glVertex2f(bar_x + fill_width, bar_y + bar_height)
                glVertex2f(bar_x, bar_y + bar_height)
                glEnd()
                
                # Value text
                self.render_text(f"{int(value * 100)}%", self.font_value,
                               (200, 200, 200), (bar_x + bar_width + 15, y + 5))
            
            elif option['type'] == 'toggle':
                value = self.settings.get(option['key'])
                text = "ON" if value else "OFF"
                color = (100, 255, 100) if value else (255, 100, 100)
                self.render_text(f"< {text} >", self.font_value, color, (cx + 100, y + 5))
            
            elif option['type'] == 'choice':
                value = self.settings.get(option['key'])
                self.render_text(f"< {value.upper()} >", self.font_value,
                               (200, 200, 100), (cx + 80, y + 5))
            
            y -= 50
        
        # Hints
        self.render_text("W/S: Navigate | A/D: Change | Enter: Select | ESC: Back", 
                        self.font_hint, (120, 120, 120), (cx, 30), center=True)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
