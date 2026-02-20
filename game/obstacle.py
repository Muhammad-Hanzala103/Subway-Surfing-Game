"""
Obstacle System - Enhanced with Moving Trains and 3D Models
"""

import numpy as np
import random
from enum import Enum
import config
from engine.mesh import create_cube
from game.models import Models


class ObstacleType(Enum):
    TRAIN = "train"
    BARRIER_LOW = "barrier_low"
    BARRIER_HIGH = "barrier_high"
    BARRIER_FULL = "barrier_full"
    MOVING_TRAIN = "moving_train"


from engine.texture import TextureGenerator


class Obstacle:
    """Single obstacle object with optional movement"""
    
    def __init__(self, obs_type, lane, z_position, moving=False, texture=None):
        self.type = obs_type
        self.lane = lane
        self.z_position = z_position
        self.active = True
        self.moving = moving
        self.move_speed = 0.0
        self.move_direction = 0  # -1 left, 1 right
        self.model = None
        self.mesh = None
        self.texture = texture
        
        # Set dimensions based on type
        if obs_type == ObstacleType.TRAIN or obs_type == ObstacleType.MOVING_TRAIN:
            self.width = config.TRAIN_WIDTH
            self.height = config.TRAIN_HEIGHT
            self.depth = config.TRAIN_LENGTH
            self.color = config.COLORS['train']
            self.model = Models.create_train()
            # Trains handle their own detailed model/texture internally (in future)
            # For now they use Vertex Colors defined in Models
            
            if obs_type == ObstacleType.MOVING_TRAIN:
                self.moving = True
                self.move_speed = random.uniform(3, 6)
                self.move_direction = random.choice([-1, 1])
        elif obs_type == ObstacleType.BARRIER_LOW:
            self.width = config.BARRIER_WIDTH
            self.height = config.BARRIER_LOW_HEIGHT
            self.depth = config.BARRIER_DEPTH
            self.color = (0.9, 0.9, 0.1, 1.0)
            self.mesh = create_cube(1.0)
        elif obs_type == ObstacleType.BARRIER_HIGH:
            self.width = config.BARRIER_WIDTH
            self.height = config.BARRIER_HIGH_HEIGHT
            self.depth = config.BARRIER_DEPTH
            self.color = (0.9, 0.5, 0.1, 1.0) 
            self.mesh = create_cube(1.0)
        else:  # BARRIER_FULL
            self.width = config.BARRIER_WIDTH
            self.height = config.BARRIER_FULL_HEIGHT
            self.depth = config.BARRIER_DEPTH
            self.color = (0.8, 0.2, 0.2, 1.0) 
            self.mesh = create_cube(1.0)
        
        # Position
        self.x = config.LANES[lane]
        self.y = self.height / 2
    
    def update(self, delta_time):
        """Update obstacle (for moving trains)"""
        if self.moving:
            self.x += self.move_direction * self.move_speed * delta_time
            
            # Bounce off edges
            max_x = config.LANES[2] + config.LANE_WIDTH * 0.5
            min_x = config.LANES[0] - config.LANE_WIDTH * 0.5
            
            if self.x > max_x:
                self.x = max_x
                self.move_direction = -1
            elif self.x < min_x:
                self.x = min_x
                self.move_direction = 1
    
    def get_bounds(self):
        half_w = self.width / 2
        half_d = self.depth / 2
        return {
            'min': np.array([self.x - half_w, 0, self.z_position - half_d]),
            'max': np.array([self.x + half_w, self.height, self.z_position + half_d])
        }
    
    def draw(self, renderer):
        """Draw the obstacle"""
        matrix = np.identity(4, dtype=np.float32)
        matrix[0, 3] = self.x
        matrix[1, 3] = self.y
        matrix[2, 3] = self.z_position
        
        # Draw Shadow
        shadow_radius = self.width * 0.6 if self.type == ObstacleType.TRAIN else self.width * 0.8
        if self.type == ObstacleType.TRAIN or self.type == ObstacleType.MOVING_TRAIN:
             renderer.draw_shadow([self.x, 0, self.z_position], radius=1.6, opacity=0.6)
        
        if self.model:
            # Bake if not baked (Optimization)
            if not self.model.display_list:
                self.model.bake(renderer)
                
            # Train model handles its own internal scaling for parts
            if self.moving:
                import math
                pulse = 0.8 + 0.2 * math.sin(self.x * 2)
            
            self.model.draw_explicit(renderer, matrix)
        
        elif self.mesh:
            # Barriers use simple mesh scaling
            matrix[0, 0] = self.width
            matrix[1, 1] = self.height
            matrix[2, 2] = self.depth
            
            # Use texture if available
            color = self.color
            if self.texture:
                color = (1, 1, 1, 1) # White so texture shows
                
            renderer.draw_mesh(self.mesh, matrix, color, texture=self.texture)
    
    def is_behind(self, z):
        return self.z_position + self.depth < z - 5


class ObstacleManager:
    """Manages obstacle spawning with moving trains"""
    
    def __init__(self):
        self.obstacles = []
        self.spawn_distance = 100.0
        self.last_spawn_z = 0.0
        self.difficulty = 1.0
        
        # Textures
        self.barrier_texture = TextureGenerator.create_stripes(
            256, (1.0, 0.8, 0.0), (0.1, 0.1, 0.1), stripe_width=32
        )
    
    def update(self, player_z, delta_time):
        # Update all obstacles (for moving ones)
        for obs in self.obstacles:
            obs.update(delta_time)
        
        # Remove passed obstacles
        self.obstacles = [o for o in self.obstacles if not o.is_behind(player_z)]
        
        # Spawn new obstacles
        spawn_threshold = player_z + self.spawn_distance
        
        while self.last_spawn_z < spawn_threshold:
            self.last_spawn_z += random.uniform(
                config.MIN_OBSTACLE_DISTANCE, 
                config.MIN_OBSTACLE_DISTANCE * 2.5 / self.difficulty
            )
            self._spawn_obstacle(self.last_spawn_z)
    
    def _spawn_obstacle(self, z):
        # Weighted random selection
        rand = random.random()
        
        if rand < 0.2:
            obs_type = ObstacleType.TRAIN
        elif rand < 0.35:
            obs_type = ObstacleType.MOVING_TRAIN
        elif rand < 0.5:
            obs_type = ObstacleType.BARRIER_LOW
        elif rand < 0.7:
            obs_type = ObstacleType.BARRIER_HIGH
        else:
            obs_type = ObstacleType.BARRIER_FULL
        
        # Random lane
        lane = random.randint(0, 2)
        
        if obs_type == ObstacleType.MOVING_TRAIN:
            self.obstacles.append(Obstacle(obs_type, lane, z, moving=True))
        elif obs_type in [ObstacleType.BARRIER_LOW, ObstacleType.BARRIER_HIGH, ObstacleType.BARRIER_FULL]:
            # Pass barrier texture
            self.obstacles.append(Obstacle(obs_type, lane, z, texture=self.barrier_texture))
        else:
            self.obstacles.append(Obstacle(obs_type, lane, z))
        
        # Sometimes add second obstacle
        if random.random() < 0.25 * self.difficulty:
            other_lane = (lane + random.choice([1, 2])) % 3
            # Avoid another moving train
            second_type = random.choice([
                ObstacleType.BARRIER_LOW, 
                ObstacleType.BARRIER_HIGH
            ])
            self.obstacles.append(Obstacle(second_type, other_lane, z, texture=self.barrier_texture))
    
    def increase_difficulty(self):
        self.difficulty = min(self.difficulty + config.OBSTACLE_DENSITY_INCREASE, 2.5)
    
    def draw(self, renderer):
        for obs in self.obstacles:
            if obs.active:
                obs.draw(renderer)
    
    def get_active_obstacles(self):
        return [o for o in self.obstacles if o.active]
    
    def reset(self):
        self.obstacles.clear()
        self.last_spawn_z = 30.0
        self.difficulty = 1.0
