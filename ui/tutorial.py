"""
Tutorial System - First-time player guidance
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
import math


class TutorialStep:
    """Single tutorial step"""
    
    def __init__(self, title, description, key_hint, highlight_area=None):
        self.title = title
        self.description = description
        self.key_hint = key_hint
        self.highlight_area = highlight_area  # (x, y, width, height) for highlight


class TutorialSystem:
    """Manages tutorial flow for first-time players"""
    
    def __init__(self, window):
        self.window = window
        self.active = False
        self.current_step = 0
        self.completed = False
        self.step_timer = 0.0
        
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 56)
        self.font_text = pygame.font.Font(None, 36)
        self.font_hint = pygame.font.Font(None, 28)
        
        # Tutorial steps
        self.steps = [
            TutorialStep(
                "Welcome to Subway Surfer!",
                "You are being chased! Run as far as you can.",
                "Press SPACE to continue"
            ),
            TutorialStep(
                "Lane Switching",
                "Press A or LEFT ARROW to move left.\nPress D or RIGHT ARROW to move right.",
                "Try pressing A or D"
            ),
            TutorialStep(
                "Jumping",
                "Press W, UP ARROW, or SPACE to jump.\nJump over low barriers!",
                "Try pressing W or SPACE"
            ),
            TutorialStep(
                "Sliding",
                "Press S or DOWN ARROW to slide.\nSlide under high obstacles!",
                "Try pressing S"
            ),
            TutorialStep(
                "Collect Coins",
                "Collect coins to increase your score.\nCoins can be used to unlock characters!",
                "Press SPACE to continue"
            ),
            TutorialStep(
                "Power-ups",
                "Collect power-ups for special abilities:\n🛹 Hoverboard  🚀 Jetpack  👟 Super Jump\n🧲 Magnet  🛡️ Shield  ⭐ 2x Score",
                "Press SPACE to continue"
            ),
            TutorialStep(
                "You're Ready!",
                "Dodge trains, collect coins, beat your high score!\nGood luck!",
                "Press ENTER to start playing!"
            )
        ]
    
    def start(self):
        """Start the tutorial"""
        self.active = True
        self.current_step = 0
        self.completed = False
    
    def skip(self):
        """Skip the tutorial"""
        self.active = False
        self.completed = True
    
    def next_step(self):
        """Move to next step"""
        self.current_step += 1
        if self.current_step >= len(self.steps):
            self.active = False
            self.completed = True
            return True
        return False
    
    def handle_input(self, events):
        """Handle tutorial input"""
        if not self.active:
            return False
        
        for event_type, event_data in events:
            if event_type == 'keydown':
                key = event_data
                
                step = self.steps[self.current_step]
                
                # Step 1: Lane switching
                if self.current_step == 1:
                    if key in [K_a, K_LEFT, K_d, K_RIGHT]:
                        return self.next_step()
                
                # Step 2: Jumping
                elif self.current_step == 2:
                    if key in [K_w, K_UP, K_SPACE]:
                        return self.next_step()
                
                # Step 3: Sliding
                elif self.current_step == 3:
                    if key in [K_s, K_DOWN]:
                        return self.next_step()
                
                # Last step: Start game
                elif self.current_step == len(self.steps) - 1:
                    if key == K_RETURN:
                        self.active = False
                        self.completed = True
                        return True
                
                # Other steps: Space to continue
                else:
                    if key == K_SPACE:
                        return self.next_step()
                
                # ESC to skip
                if key == K_ESCAPE:
                    self.skip()
                    return True
        
        return False
    
    def render_text(self, text, font, color, position, center=False):
        """Render text"""
        lines = text.split('\n')
        y = position[1]
        
        for line in lines:
            surface = font.render(line, True, color)
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
            
            x = position[0]
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
            
            y -= h + 5
    
    def draw(self, time):
        """Draw tutorial overlay"""
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
        
        # Dark overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.window.width, 0)
        glVertex2f(self.window.width, self.window.height)
        glVertex2f(0, self.window.height)
        glEnd()
        
        # Tutorial box
        box_width = 600
        box_height = 300
        box_x = (self.window.width - box_width) // 2
        box_y = (self.window.height - box_height) // 2
        
        # Box background
        glColor4f(0.15, 0.15, 0.25, 0.95)
        glBegin(GL_QUADS)
        glVertex2f(box_x, box_y)
        glVertex2f(box_x + box_width, box_y)
        glVertex2f(box_x + box_width, box_y + box_height)
        glVertex2f(box_x, box_y + box_height)
        glEnd()
        
        # Box border
        pulse = 0.7 + 0.3 * math.sin(time * 4)
        glColor4f(0.3 * pulse, 0.6 * pulse, 1.0 * pulse, 1.0)
        glLineWidth(3)
        glBegin(GL_LINE_LOOP)
        glVertex2f(box_x, box_y)
        glVertex2f(box_x + box_width, box_y)
        glVertex2f(box_x + box_width, box_y + box_height)
        glVertex2f(box_x, box_y + box_height)
        glEnd()
        
        # Progress indicator
        step_count = len(self.steps)
        indicator_width = box_width - 40
        step_width = indicator_width // step_count
        
        for i in range(step_count):
            px = box_x + 20 + i * step_width
            py = box_y + box_height - 25
            
            if i < self.current_step:
                glColor4f(0.2, 0.8, 0.4, 1.0)  # Completed
            elif i == self.current_step:
                glColor4f(0.3, 0.6, 1.0, 1.0)  # Current
            else:
                glColor4f(0.3, 0.3, 0.3, 1.0)  # Future
            
            glBegin(GL_QUADS)
            glVertex2f(px, py)
            glVertex2f(px + step_width - 5, py)
            glVertex2f(px + step_width - 5, py + 10)
            glVertex2f(px, py + 10)
            glEnd()
        
        # Get current step
        step = self.steps[self.current_step]
        cx = self.window.width // 2
        
        # Title
        self.render_text(step.title, self.font_title, 
                        (100, 180, 255), (cx, box_y + box_height - 70), center=True)
        
        # Description
        self.render_text(step.description, self.font_text,
                        (220, 220, 220), (cx, box_y + box_height - 140), center=True)
        
        # Hint (pulsing)
        alpha = int(150 + 105 * math.sin(time * 5))
        self.render_text(step.key_hint, self.font_hint,
                        (alpha, alpha, 50), (cx, box_y + 40), center=True)
        
        # Skip hint
        self.render_text("Press ESC to skip tutorial", self.font_hint,
                        (100, 100, 100), (cx, box_y + 15), center=True)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
