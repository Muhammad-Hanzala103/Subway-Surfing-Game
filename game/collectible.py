"""
Collectible System - Coins, Power-ups, Mystery Boxes
Enhanced with Hoverboard, Jetpack, Super Sneakers
"""

import numpy as np
import random
import math
from enum import Enum
import config
from engine.mesh import create_cylinder, create_cube, create_sphere


class PowerUpType(Enum):
    MAGNET = "magnet"
    SHIELD = "shield"
    SCORE_BOOST = "score_boost"
    HOVERBOARD = "hoverboard"
    JETPACK = "jetpack"
    SUPER_SNEAKERS = "super_sneakers"


class Coin:
    """Collectible coin with glow effect"""
    
    def __init__(self, x, y, z):
        self.position = np.array([x, y, z], dtype=np.float32)
        self.collected = False
        self.radius = config.COIN_RADIUS
        self.rotation = random.random() * 360
        self.glow_phase = random.random() * math.pi * 2
        self.mesh = create_cylinder(self.radius, 0.1, 12)
        self.color = config.COLORS['coin']
    
    def update(self, delta_time):
        self.rotation += config.COIN_ROTATION_SPEED * delta_time
        self.glow_phase += delta_time * 3
        # Floating animation
        self.position[1] = 1.0 + math.sin(self.rotation * 0.05) * 0.15
    
    def get_model_matrix(self):
        matrix = np.identity(4, dtype=np.float32)
        rad = math.radians(self.rotation)
        c, s = math.cos(rad), math.sin(rad)
        matrix[0, 0] = c
        matrix[0, 2] = s
        matrix[2, 0] = -s
        matrix[2, 2] = c
        matrix[0, 3] = self.position[0]
        matrix[1, 3] = self.position[1]
        matrix[2, 3] = self.position[2]
        return matrix
    
    def get_glow_color(self):
        """Get color with glow effect"""
        glow = 0.7 + 0.3 * math.sin(self.glow_phase)
        return (self.color[0] * glow, self.color[1] * glow, 
                self.color[2] * glow, self.color[3])
    
    def is_behind(self, z):
        return self.position[2] < z - 5


class PowerUp:
    """Power-up item with unique visuals per type"""
    
    # Power-up configuration
    POWERUP_CONFIG = {
        PowerUpType.MAGNET: {
            'color': (0.8, 0.2, 0.8, 1.0),  # Purple
            'size': 0.8,
            'shape': 'cube'
        },
        PowerUpType.SHIELD: {
            'color': (0.2, 0.8, 0.8, 1.0),  # Cyan
            'size': 0.9,
            'shape': 'sphere'
        },
        PowerUpType.SCORE_BOOST: {
            'color': (0.2, 0.8, 0.2, 1.0),  # Green
            'size': 0.8,
            'shape': 'cube'
        },
        PowerUpType.HOVERBOARD: {
            'color': (1.0, 0.5, 0.0, 1.0),  # Orange
            'size': 1.0,
            'shape': 'cube'  # Flat board
        },
        PowerUpType.JETPACK: {
            'color': (1.0, 0.2, 0.2, 1.0),  # Red
            'size': 0.9,
            'shape': 'cylinder'
        },
        PowerUpType.SUPER_SNEAKERS: {
            'color': (0.0, 1.0, 0.5, 1.0),  # Bright green
            'size': 0.7,
            'shape': 'cube'
        }
    }
    
    def __init__(self, power_type, lane, z):
        self.type = power_type
        self.position = np.array([config.LANES[lane], 1.5, z], dtype=np.float32)
        self.collected = False
        self.rotation = random.random() * 360
        self.pulse_phase = random.random() * math.pi * 2
        
        cfg = self.POWERUP_CONFIG[power_type]
        self.color = cfg['color']
        self.size = cfg['size']
        
        # Create appropriate mesh
        if cfg['shape'] == 'sphere':
            self.mesh = create_sphere(self.size / 2, 12, 8)
        elif cfg['shape'] == 'cylinder':
            self.mesh = create_cylinder(self.size / 3, self.size, 8)
        else:
            self.mesh = create_cube(self.size)
    
    def update(self, delta_time):
        self.rotation += 120 * delta_time
        self.pulse_phase += delta_time * 4
        # Floating animation
        self.position[1] = 1.5 + math.sin(self.pulse_phase) * 0.25
    
    def get_model_matrix(self):
        matrix = np.identity(4, dtype=np.float32)
        rad = math.radians(self.rotation)
        c, s = math.cos(rad), math.sin(rad)
        matrix[0, 0] = c
        matrix[0, 2] = s
        matrix[2, 0] = -s
        matrix[2, 2] = c
        matrix[0, 3] = self.position[0]
        matrix[1, 3] = self.position[1]
        matrix[2, 3] = self.position[2]
        return matrix
    
    def get_pulse_color(self):
        """Get color with pulse effect"""
        pulse = 0.7 + 0.3 * math.sin(self.pulse_phase)
        return (min(1.0, self.color[0] * pulse * 1.3),
                min(1.0, self.color[1] * pulse * 1.3),
                min(1.0, self.color[2] * pulse * 1.3),
                self.color[3])
    
    def is_behind(self, z):
        return self.position[2] < z - 5


class MysteryBox:
    """Mystery box that gives random rewards"""
    
    def __init__(self, lane, z):
        self.position = np.array([config.LANES[lane], 1.5, z], dtype=np.float32)
        self.collected = False
        self.rotation = 0
        self.mesh = create_cube(1.0)
        self.color = (0.8, 0.6, 0.2, 1.0)  # Golden brown
        self.glow_phase = 0
    
    def update(self, delta_time):
        self.rotation += 60 * delta_time
        self.glow_phase += delta_time * 5
        self.position[1] = 1.5 + math.sin(self.glow_phase) * 0.2
    
    def get_model_matrix(self):
        matrix = np.identity(4, dtype=np.float32)
        rad = math.radians(self.rotation)
        c, s = math.cos(rad), math.sin(rad)
        matrix[0, 0] = c
        matrix[0, 2] = s
        matrix[2, 0] = -s
        matrix[2, 2] = c
        matrix[0, 3] = self.position[0]
        matrix[1, 3] = self.position[1]
        matrix[2, 3] = self.position[2]
        return matrix
    
    def get_reward(self):
        """Get random reward from mystery box"""
        rewards = [
            ('coins', random.randint(10, 50)),
            ('powerup', random.choice(list(PowerUpType))),
            ('score', random.randint(100, 500)),
        ]
        return random.choice(rewards)
    
    def is_behind(self, z):
        return self.position[2] < z - 5


class CollectibleManager:
    """Manages coins, power-ups, and mystery boxes"""
    
    def __init__(self):
        self.coins = []
        self.powerups = []
        self.mystery_boxes = []
        self.last_spawn_z = 0.0
        self.spawn_distance = 80.0
        self.combo_count = 0
        self.combo_timer = 0.0
    
    def update(self, player_z, delta_time):
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= delta_time
            if self.combo_timer <= 0:
                self.combo_count = 0
        
        # Update existing items
        for coin in self.coins:
            coin.update(delta_time)
        for powerup in self.powerups:
            powerup.update(delta_time)
        for box in self.mystery_boxes:
            box.update(delta_time)
        
        # Remove passed/collected items
        self.coins = [c for c in self.coins if not c.is_behind(player_z) and not c.collected]
        self.powerups = [p for p in self.powerups if not p.is_behind(player_z) and not p.collected]
        self.mystery_boxes = [b for b in self.mystery_boxes if not b.is_behind(player_z) and not b.collected]
        
        # Spawn new items
        while self.last_spawn_z < player_z + self.spawn_distance:
            self.last_spawn_z += 5.0
            self._spawn_coins(self.last_spawn_z)
            
            # Power-up spawn
            if random.random() < 0.12:  # 12% chance
                self._spawn_powerup(self.last_spawn_z + 2)
            
            # Mystery box spawn
            if random.random() < 0.03:  # 3% chance
                self._spawn_mystery_box(self.last_spawn_z + 2)
    
    def _spawn_coins(self, z):
        if random.random() < config.COIN_SPAWN_CHANCE:
            lane = random.randint(0, 2)
            x = config.LANES[lane]
            
            # Random coin patterns
            pattern = random.choice(['line', 'arc', 'zigzag'])
            
            if pattern == 'line':
                for i in range(config.COINS_PER_GROUP):
                    coin_z = z + i * config.COIN_SPACING
                    self.coins.append(Coin(x, 1.0, coin_z))
            
            elif pattern == 'arc':
                for i in range(config.COINS_PER_GROUP):
                    coin_z = z + i * config.COIN_SPACING
                    height = 1.0 + math.sin(i / config.COINS_PER_GROUP * math.pi) * 1.5
                    self.coins.append(Coin(x, height, coin_z))
            
            elif pattern == 'zigzag':
                for i in range(config.COINS_PER_GROUP):
                    coin_z = z + i * config.COIN_SPACING
                    lane_offset = (i % 2) * config.LANE_WIDTH * (1 if lane < 2 else -1)
                    self.coins.append(Coin(x + lane_offset * 0.5, 1.0, coin_z))
    
    def _spawn_powerup(self, z):
        # Weighted random selection
        weights = {
            PowerUpType.MAGNET: 20,
            PowerUpType.SHIELD: 15,
            PowerUpType.SCORE_BOOST: 25,
            PowerUpType.HOVERBOARD: 15,
            PowerUpType.JETPACK: 10,
            PowerUpType.SUPER_SNEAKERS: 15,
        }
        
        total = sum(weights.values())
        r = random.randint(1, total)
        cumulative = 0
        
        for power_type, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                lane = random.randint(0, 2)
                self.powerups.append(PowerUp(power_type, lane, z))
                break
    
    def _spawn_mystery_box(self, z):
        lane = random.randint(0, 2)
        self.mystery_boxes.append(MysteryBox(lane, z))
    
    def collect_coin(self):
        """Called when coin is collected - updates combo"""
        self.combo_count += 1
        self.combo_timer = 2.0  # 2 second combo window
        return self.combo_count
    
    def get_combo_multiplier(self):
        """Get score multiplier based on combo"""
        if self.combo_count < 5:
            return 1.0
        elif self.combo_count < 10:
            return 1.5
        elif self.combo_count < 20:
            return 2.0
        else:
            return 3.0
    
    def draw(self, renderer):
        # Draw coins with glow
        for coin in self.coins:
            if not coin.collected:
                renderer.draw_mesh(coin.mesh, coin.get_model_matrix(), coin.get_glow_color())
        
        # Draw power-ups with pulse
        for powerup in self.powerups:
            if not powerup.collected:
                renderer.draw_mesh(powerup.mesh, powerup.get_model_matrix(), powerup.get_pulse_color())
        
        # Draw mystery boxes
        for box in self.mystery_boxes:
            if not box.collected:
                # Draw with golden glow
                glow = 0.8 + 0.2 * math.sin(box.glow_phase)
                color = (box.color[0] * glow, box.color[1] * glow, box.color[2] * glow, 1.0)
                renderer.draw_mesh(box.mesh, box.get_model_matrix(), color)
    
    def get_coins(self):
        return [c for c in self.coins if not c.collected]
    
    def get_powerups(self):
        return [p for p in self.powerups if not p.collected]
    
    def get_mystery_boxes(self):
        return [b for b in self.mystery_boxes if not b.collected]
    
    def reset(self):
        self.coins.clear()
        self.powerups.clear()
        self.mystery_boxes.clear()
        self.last_spawn_z = 20.0
        self.combo_count = 0
        self.combo_timer = 0.0
