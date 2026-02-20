"""
Shop System UI
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
import math
import config

class ShopMenu:
    """Shop menu for buying upgrades"""
    
    def __init__(self, menu_system, game_manager):
        self.menu_system = menu_system
        self.game_manager = game_manager
        self.window = menu_system.window
        
        self.selected_item = 0
        self.items = ["Jetpack", "Magnet", "Sneakers", "Multiplier", "Back"]
        
        # Upgrade Costs
        self.base_costs = {
            "Jetpack": 500,
            "Magnet": 500,
            "Sneakers": 500,
            "Multiplier": 2000
        }
    
    def handle_key(self, key):
        if key == K_UP:
            self.selected_item = (self.selected_item - 1) % len(self.items)
            self.menu_system.animation_time = 0
            return None
        if key == K_DOWN:
            self.selected_item = (self.selected_item + 1) % len(self.items)
            self.menu_system.animation_time = 0
            return None
        if key in (K_RETURN, K_SPACE):
            return self.activate_item()
        if key == K_ESCAPE:
            return "back"
        return None

    def activate_item(self):
        item = self.items[self.selected_item]
        
        if item == "Back":
            return "back"
            
        # Get current level
        upgrades = self.game_manager.score.get_upgrades()
        level_key = item.lower() + "_level"
        current_level = upgrades.get(level_key, 1)
        
        if current_level >= 6:
            return "maxed"
            
        # Calculate Cost
        cost = self.base_costs[item] * current_level
        
        # Check money
        if self.game_manager.score.total_coins >= cost:
            # Buy
            self.game_manager.score.total_coins -= cost
            self.game_manager.score.upgrade_powerup(level_key)
            return "purchased"
        return "insufficient_funds"
    
    def draw(self):
        # Background
        self.menu_system.draw_gradient_background((0.1, 0.2, 0.3, 1.0), (0.05, 0.1, 0.15, 1.0))
        
        cx = self.window.width // 2
        cy = self.window.height // 2 + 150
        
        # Title
        self.menu_system.render_text("SHOP", self.menu_system.font_title, (1.0, 0.8, 0.0, 1.0), (cx, self.window.height - 100), center=True)
        
        # Coins Display
        coins = self.game_manager.score.total_coins
        self.menu_system.render_text(f"Coins: {coins}", self.menu_system.font_large, (1.0, 1.0, 0.0, 1.0), (self.window.width - 200, self.window.height - 60), center=True)
        
        # Items
        upgrades = self.game_manager.score.get_upgrades()
        
        for i, item in enumerate(self.items):
            y = cy - (i * 80)
            
            # Color
            if i == self.selected_item:
                scale = 1.0 + 0.1 * abs(math.sin(self.menu_system.animation_time * 5))
                color = (1.0, 1.0, 1.0, 1.0)
            else:
                scale = 1.0
                color = (0.6, 0.6, 0.6, 1.0)
            
            # Draw Item Name
            if item == "Back":
                self.menu_system.render_text(item, self.menu_system.font_medium, color, (cx, y), center=True)
            else:
                level_key = item.lower() + "_level"
                level = upgrades.get(level_key, 1)
                cost = self.base_costs[item] * level
                
                # Name + Level
                text = f"{item} (Lvl {level})"
                if level >= 6: 
                    text += " - MAX"
                    cost_text = ""
                else:
                    cost_text = f"{cost} C"
                
                self.menu_system.render_text(text, self.menu_system.font_medium, color, (cx - 100, y), center=True)
                
                # Cost
                if cost_text:
                    can_afford = coins >= cost
                    cost_col = (1.0, 1.0, 0.0, 1.0) if can_afford else (1.0, 0.2, 0.2, 1.0)
                    self.menu_system.render_text(cost_text, self.menu_system.font_medium, cost_col, (cx + 200, y), center=True)
                    
                # Progress Bar
                bar_x = cx - 150
                bar_y = y - 30
                bar_w = 300
                bar_h = 10
                
                self.draw_progress_bar(bar_x, bar_y, bar_w, bar_h, level / 6.0)

    def draw_progress_bar(self, x, y, width, height, progress):
        """Draw GL progress bar"""
        glDisable(GL_TEXTURE_2D)
        
        # Background
        glColor4f(0.3, 0.3, 0.3, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Fill
        if progress > 0:
            fill_w = width * progress
            glColor4f(0.0, 1.0, 0.0, 1.0)
            glBegin(GL_QUADS)
            glVertex2f(x, y)
            glVertex2f(x + fill_w, y)
            glVertex2f(x + fill_w, y + height)
            glVertex2f(x, y + height)
            glEnd()
            
        glEnable(GL_TEXTURE_2D)
