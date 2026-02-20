"""
Player Character System - Enhanced with Advanced Features
Includes Hoverboard, Jetpack, Super Sneakers, and Trail Effects
"""

import numpy as np
from OpenGL.GL import *
from enum import Enum

import config
# from engine.mesh import create_cube 
from game.models import Models


class PlayerState(Enum):
    RUNNING = "running"
    JUMPING = "jumping"
    SLIDING = "sliding"
    SWITCHING = "switching"
    DEAD = "dead"
    HOVERBOARD = "hoverboard"
    JETPACK = "jetpack"


class Player:
    """Player character with advanced movement and power-ups"""
    
    def __init__(self):
        # Position
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        
        # Lane system
        self.current_lane = 1
        self.target_lane = 1
        self.target_x = 0.0
        
        # State
        self.state = PlayerState.RUNNING
        self.is_grounded = True
        self.is_invincible = False
        self.invincible_timer = 0.0
        
        # Dimensions
        self.width = config.PLAYER_WIDTH
        self.height = config.PLAYER_HEIGHT
        self.depth = config.PLAYER_DEPTH
        
        # Animation
        self.slide_timer = 0.0
        self.bob_offset = 0.0
        self.lean_angle = 0.0
        self.run_cycle = 0.0
        
        # Speed
        self.forward_speed = config.PLAYER_SPEED
        self.base_jump_force = config.JUMP_FORCE
        
        # 3D Model
        self.color = config.COLORS['player']
        self.model = Models.create_player(self.color)
        
        # Power-ups
        self.has_magnet = False
        self.has_shield = False
        self.score_multiplier = 1
        
        # NEW: Advanced Power-ups
        self.has_hoverboard = False
        self.hoverboard_timer = 0.0
        self.has_jetpack = False
        self.jetpack_timer = 0.0
        self.jetpack_fuel = 0.0
        self.has_super_sneakers = False
        self.super_sneakers_timer = 0.0
        
        # Trail effect positions
        self.trail_positions = []
        self.max_trail_length = 10
        
        # Near miss tracking
        self.near_miss_timer = 0.0
        self.near_miss_count = 0
    
    def update(self, delta_time):
        """Update player state"""
        if self.state == PlayerState.DEAD:
            return
        
        # Update run cycle for animation
        self.run_cycle += delta_time
        
        # Animate model
        speed_ratio = self.forward_speed / config.PLAYER_SPEED
        state_name = self.state.value
        Models.animate_player(self.model, self.run_cycle, speed_ratio, state_name)
        
        # Move forward
        self.position[2] += self.forward_speed * delta_time
        
        # Update trail
        self._update_trail()
        
        # Lane switching
        self._update_lane_switch(delta_time)
        
        # Power-up updates
        self._update_powerups(delta_time)
        
        # State-specific behavior
        if self.state == PlayerState.JETPACK:
            self._update_jetpack(delta_time)
        elif self.state == PlayerState.HOVERBOARD:
            self._update_hoverboard(delta_time)
        elif self.state == PlayerState.JUMPING:
            self._update_jumping(delta_time)
        elif self.state == PlayerState.SLIDING:
            self._update_sliding(delta_time)
        
        # Invincibility
        if self.is_invincible:
            self.invincible_timer -= delta_time
            if self.invincible_timer <= 0:
                self.is_invincible = False
        
        # Near miss cooldown
        if self.near_miss_timer > 0:
            self.near_miss_timer -= delta_time
        
        # Lean during lane switch
        lane_diff = self.target_x - self.position[0]
        self.lean_angle = lane_diff * 20
        self.model.root.rotation[2] = -self.lean_angle
    
    def _update_trail(self):
        """Update trail positions for effect"""
        pos_copy = self.position.copy()
        self.trail_positions.append(pos_copy)
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
    
    def _update_lane_switch(self, delta_time):
        """Smooth lane switching"""
        diff = self.target_x - self.position[0]
        if abs(diff) > 0.01:
            speed = config.LANE_SWITCH_SPEED
            if self.has_hoverboard:
                speed *= 1.5  # Faster on hoverboard
            
            move_amount = speed * delta_time
            if abs(diff) < move_amount:
                self.position[0] = self.target_x
            else:
                self.position[0] += move_amount * np.sign(diff)
    
    def _update_powerups(self, delta_time):
        """Update power-up timers"""
        # Hoverboard
        if self.has_hoverboard:
            self.hoverboard_timer -= delta_time
            if self.hoverboard_timer <= 0:
                self.has_hoverboard = False
                if self.state == PlayerState.HOVERBOARD:
                    self.state = PlayerState.RUNNING
        
        # Jetpack
        if self.has_jetpack:
            self.jetpack_timer -= delta_time
            if self.jetpack_timer <= 0:
                self.has_jetpack = False
                if self.state == PlayerState.JETPACK:
                    self.state = PlayerState.JUMPING  # Fall down
        
        # Super Sneakers
        if self.has_super_sneakers:
            self.super_sneakers_timer -= delta_time
            if self.super_sneakers_timer <= 0:
                self.has_super_sneakers = False
    
    def _update_jumping(self, delta_time):
        """Update jump physics"""
        self.velocity[1] += config.GRAVITY * delta_time
        self.position[1] += self.velocity[1] * delta_time
        
        if self.position[1] <= 0:
            self.position[1] = 0
            self.velocity[1] = 0
            self.is_grounded = True
            
            if self.has_hoverboard:
                self.state = PlayerState.HOVERBOARD
            else:
                self.state = PlayerState.RUNNING
    
    def _update_sliding(self, delta_time):
        """Update slide state"""
        self.slide_timer -= delta_time
        if self.slide_timer <= 0:
            self.height = config.PLAYER_HEIGHT
            if self.has_hoverboard:
                self.state = PlayerState.HOVERBOARD
            else:
                self.state = PlayerState.RUNNING
    
    def _update_hoverboard(self, delta_time):
        """Update hoverboard state"""
        # Hover slightly above ground
        target_height = 0.3
        self.position[1] += (target_height - self.position[1]) * 5 * delta_time
    
    def _update_jetpack(self, delta_time):
        """Update jetpack flying"""
        target_height = 4.0
        self.velocity[1] = (target_height - self.position[1]) * 2
        self.position[1] += self.velocity[1] * delta_time
        self.position[1] = min(self.position[1], 5.0)
    
    def move_left(self):
        """Switch to left lane"""
        if self.state != PlayerState.DEAD and self.target_lane > 0:
            self.target_lane -= 1
            self.target_x = config.LANES[self.target_lane]
            return True
        return False
    
    def move_right(self):
        """Switch to right lane"""
        if self.state != PlayerState.DEAD and self.target_lane < 2:
            self.target_lane += 1
            self.target_x = config.LANES[self.target_lane]
            return True
        return False
    
    def jump(self):
        """Make player jump"""
        if self.state == PlayerState.DEAD:
            return False
        
        if self.state == PlayerState.JETPACK:
            self.velocity[1] = 5.0
            return True
        
        if self.is_grounded or self.state == PlayerState.HOVERBOARD:
            prev_state = self.state
            self.state = PlayerState.JUMPING
            
            jump_force = self.base_jump_force
            if self.has_super_sneakers:
                jump_force *= 1.8
            
            self.velocity[1] = jump_force
            self.is_grounded = False
            
            if prev_state == PlayerState.HOVERBOARD:
                self.position[1] += 0.3
            
            return True
        return False

    def slide(self):
        """Make player slide"""
        if self.state == PlayerState.DEAD:
            return False
        
        if self.state == PlayerState.JETPACK:
            self.velocity[1] = -10.0
            return True
        
        if self.is_grounded or self.state == PlayerState.HOVERBOARD:
            self.state = PlayerState.SLIDING
            self.slide_timer = config.SLIDE_DURATION
            self.height = config.SLIDE_HEIGHT
            return True
        
        if self.state == PlayerState.JUMPING:
            self.velocity[1] = -15.0
            return True
        
        return False
    
    def get_bounds(self):
        """Get player bounding box"""
        half_w = self.width / 2
        
        # Adjust height based on state
        height = self.height
        if self.state == PlayerState.SLIDING:
            height = config.SLIDE_HEIGHT
            
        return {
            'min': np.array([self.position[0] - half_w, self.position[1], self.position[2] - self.depth / 2]),
            'max': np.array([self.position[0] + half_w, self.position[1] + height, self.position[2] + self.depth / 2])
        }
    
    def get_model_matrix(self):
        """Get transformation matrix for player"""
        matrix = np.identity(4, dtype=np.float32)
        matrix[0:3, 3] = self.position
        return matrix
    
    def draw(self, renderer):
        """Draw player"""
        # Get transformation matrix
        matrix = self.get_model_matrix()
        
        # Draw Shadow
        shadow_y = 0 if self.state != PlayerState.JETPACK else 0 
        renderer.draw_shadow([self.position[0], shadow_y, self.position[2]], radius=0.6, opacity=0.5)
        
        # Animate model
        Models.animate_player(
            self.model, 
            renderer.time, 
            self.forward_speed / config.PLAYER_SPEED,
            "jumping" if self.state == PlayerState.JUMPING else
            "sliding" if self.state == PlayerState.SLIDING else
            "hoverboard" if self.state == PlayerState.HOVERBOARD else
            "jetpack" if self.state == PlayerState.JETPACK else
            "running"
        )
        
        # Draw model
        self.model.draw_explicit(renderer, matrix)
        
        # Draw trail
        if self.trail_positions:
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glLineWidth(2.0)
            glBegin(GL_LINE_STRIP)
            color = (1.0, 1.0, 0.0, 0.5) if self.has_super_sneakers else (0.5, 0.8, 1.0, 0.5)
            glColor4f(*color)
            for pos in self.trail_positions:
                glVertex3f(pos[0], pos[1] + 0.5, pos[2])
            glEnd()
            glLineWidth(1.0)
            glEnable(GL_LIGHTING)
    
    def get_color(self):
        if self.state == PlayerState.JETPACK:
            return (1.0, 0.3, 0.1, 1.0)
        elif self.state == PlayerState.HOVERBOARD:
            return (1.0, 0.6, 0.0, 1.0)
        elif self.has_super_sneakers:
            return (0.0, 1.0, 0.5, 1.0)
        elif self.has_shield:
            return (0.2, 0.8, 1.0, 0.9)
        else:
            return self.color
    
    def get_trail_positions(self):
        return self.trail_positions
    
    def reset(self):
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.current_lane = 1
        self.target_lane = 1
        self.target_x = 0.0
        self.state = PlayerState.RUNNING
        self.is_grounded = True
        self.is_invincible = False
        self.height = config.PLAYER_HEIGHT
        self.forward_speed = config.PLAYER_SPEED
        
        self.has_magnet = False
        self.has_shield = False
        self.has_hoverboard = False
        self.has_jetpack = False
        self.has_super_sneakers = False
        self.hoverboard_timer = 0.0
        self.jetpack_timer = 0.0
        self.super_sneakers_timer = 0.0
        self.score_multiplier = 1
        
        self.trail_positions.clear()
        self.near_miss_count = 0
        self.near_miss_timer = 0.0
    
    def register_near_miss(self):
        """Register a near miss and return True if cooldown allows"""
        if self.near_miss_timer <= 0:
            self.near_miss_count += 1
            self.near_miss_timer = 0.5  # Cooldown
            return True
        return False
    
    def die(self):
        """Handle player death"""
        if self.is_invincible:
            return False
        if self.has_shield:
            self.has_shield = False
            self.is_invincible = True
            self.invincible_timer = 2.0
            return False
        if self.has_hoverboard:
            self.has_hoverboard = False
            self.hoverboard_timer = 0
            self.is_invincible = True
            self.invincible_timer = 2.0
            self.state = PlayerState.RUNNING
            return False
        
        self.state = PlayerState.DEAD
        return True
