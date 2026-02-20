"""
Track/Road Generation System - Enhanced with Multiple Themes
"""

import numpy as np
import random
import config
from engine.mesh import create_plane, create_cube


class EnvironmentTheme:
    """Environment theme configuration"""
    
    THEMES = {
        'urban': {
            'track_color': (0.15, 0.15, 0.2, 1.0),
            'line_color': (1.0, 1.0, 1.0, 0.8),
            'barrier_color': (0.3, 0.3, 0.35, 1.0),
            'bg_color_top': (0.1, 0.1, 0.3, 1.0),
            'bg_color_bottom': (0.4, 0.2, 0.5, 1.0),
            'building_colors': [(0.2, 0.2, 0.25, 1.0), (0.25, 0.25, 0.3, 1.0)],
        },
        'sunset': {
            'track_color': (0.2, 0.15, 0.1, 1.0),
            'line_color': (1.0, 0.9, 0.7, 0.8),
            'barrier_color': (0.4, 0.3, 0.2, 1.0),
            'bg_color_top': (0.9, 0.4, 0.2, 1.0),
            'bg_color_bottom': (0.5, 0.1, 0.3, 1.0),
            'building_colors': [(0.15, 0.1, 0.1, 1.0), (0.2, 0.15, 0.15, 1.0)],
        },
        'neon': {
            'track_color': (0.05, 0.05, 0.1, 1.0),
            'line_color': (0.0, 1.0, 1.0, 0.9),
            'barrier_color': (0.1, 0.1, 0.15, 1.0),
            'bg_color_top': (0.0, 0.05, 0.15, 1.0),
            'bg_color_bottom': (0.1, 0.0, 0.2, 1.0),
            'building_colors': [(0.05, 0.05, 0.1, 1.0), (0.08, 0.08, 0.12, 1.0)],
        },
        'forest': {
            'track_color': (0.15, 0.1, 0.05, 1.0),
            'line_color': (0.8, 0.9, 0.7, 0.7),
            'barrier_color': (0.2, 0.15, 0.1, 1.0),
            'bg_color_top': (0.2, 0.4, 0.3, 1.0),
            'bg_color_bottom': (0.1, 0.2, 0.15, 1.0),
            'building_colors': [(0.1, 0.15, 0.1, 1.0), (0.15, 0.2, 0.15, 1.0)],
        },
    }
    
    @classmethod
    def get_theme(cls, name):
        return cls.THEMES.get(name, cls.THEMES['urban'])
    
    @classmethod
    def get_random_theme(cls):
        return random.choice(list(cls.THEMES.keys()))


class Building:
    """Background building for environment"""
    
    def __init__(self, x, z, width, height, depth, color):
        self.position = np.array([x, height/2, z], dtype=np.float32)
        self.width = width
        self.height = height
        self.depth = depth
        self.color = color
        self.mesh = create_cube(1.0)
    
    def get_model_matrix(self):
        matrix = np.identity(4, dtype=np.float32)
        matrix[0, 0] = self.width
        matrix[1, 1] = self.height
        matrix[2, 2] = self.depth
        matrix[0, 3] = self.position[0]
        matrix[1, 3] = self.position[1]
        matrix[2, 3] = self.position[2]
        return matrix


class TrackSegment:
    """Single segment of the infinite track"""
    
    def __init__(self, z_position, theme_name='urban'):
        self.z_position = z_position
        self.length = config.TRACK_SEGMENT_LENGTH
        self.theme = EnvironmentTheme.get_theme(theme_name)
        
        # Create track mesh
        self.track_mesh = create_plane(config.TRACK_WIDTH, self.length)
        self.track_color = self.theme['track_color']
        
        # Generate track texture
        from engine.texture import TextureGenerator
        self.texture = TextureGenerator.create_noise(
            256,
            self.track_color[:3],  # RGB only
            intensity=0.05
        )
        
        # Side barriers
        self.left_barrier = create_cube(1.0)
        self.right_barrier = create_cube(1.0)
        self.barrier_color = self.theme['barrier_color']
        
        # Background buildings
        self.buildings = []
        self._generate_buildings()
    
    def _generate_buildings(self):
        """Generate random buildings on sides"""
        building_colors = self.theme['building_colors']
        
        for side in [-1, 1]:
            x_base = side * (config.TRACK_WIDTH / 2 + 5)
            
            z = self.z_position
            while z < self.z_position + self.length:
                if random.random() < 0.7:
                    width = random.uniform(3, 8)
                    height = random.uniform(5, 25)
                    depth = random.uniform(5, 15)
                    x = x_base + side * random.uniform(2, 8)
                    color = random.choice(building_colors)
                    
                    self.buildings.append(Building(x, z + depth/2, width, height, depth, color))
                    z += depth + random.uniform(2, 10)
                else:
                    z += random.uniform(5, 15)
    
    def get_track_matrix(self):
        matrix = np.identity(4, dtype=np.float32)
        matrix[0, 3] = 0
        matrix[1, 3] = -0.01
        matrix[2, 3] = self.z_position + self.length / 2
        return matrix
    
    def get_barrier_matrices(self):
        left = np.identity(4, dtype=np.float32)
        left[0, 0] = 0.5
        left[1, 1] = 2.0
        left[2, 2] = self.length
        left[0, 3] = -config.TRACK_WIDTH / 2 - 0.25
        left[1, 3] = 1.0
        left[2, 3] = self.z_position + self.length / 2
        
        right = np.identity(4, dtype=np.float32)
        right[0, 0] = 0.5
        right[1, 1] = 2.0
        right[2, 2] = self.length
        right[0, 3] = config.TRACK_WIDTH / 2 + 0.25
        right[1, 3] = 1.0
        right[2, 3] = self.z_position + self.length / 2
        
        return left, right
    
    def is_behind(self, z):
        return self.z_position + self.length < z - 10


from engine.texture import TextureGenerator


class TrackManager:
    """Manages infinite track generation with environment themes"""
    
    def __init__(self):
        self.segments = []
        self.next_segment_z = 0.0
        self.current_theme = 'urban'
        self.theme_change_distance = 500.0
        self.next_theme_change = self.theme_change_distance
        
        # Generate theme textures
        self.theme_textures = {}
        self._generate_theme_textures()
        
        # Initialize segments
        for _ in range(config.NUM_TRACK_SEGMENTS):
            self._spawn_segment()
            
    def _generate_theme_textures(self):
        """Generate procedural textures for each theme"""
        # Urban - Asphalt Noise
        self.theme_textures['urban'] = TextureGenerator.create_noise(
            256, (0.15, 0.15, 0.2), intensity=0.1
        )
        
        # Sunset - Dusty/Sandy Noise
        self.theme_textures['sunset'] = TextureGenerator.create_noise(
            256, (0.2, 0.15, 0.1), intensity=0.15
        )
        
        # Neon - Digital Grid / Checkers
        self.theme_textures['neon'] = TextureGenerator.create_checkers(
            256, (0.05, 0.05, 0.1), (0.1, 0.0, 0.2), num_checks=8
        )
        
        # Forest - Dirt/Grass Noise
        self.theme_textures['forest'] = TextureGenerator.create_noise(
            256, (0.15, 0.1, 0.05), intensity=0.2
        )
    
    def _spawn_segment(self):
        segment = TrackSegment(self.next_segment_z, self.current_theme)
        # Assign texture to segment for easy access during draw
        segment.texture = self.theme_textures.get(self.current_theme)
        self.segments.append(segment)
        self.next_segment_z += config.TRACK_SEGMENT_LENGTH
    
    def update(self, player_z):
        # Check for theme change
        if player_z > self.next_theme_change:
            themes = list(EnvironmentTheme.THEMES.keys())
            if self.current_theme in themes:
                themes.remove(self.current_theme)
            self.current_theme = random.choice(themes)
            self.next_theme_change += self.theme_change_distance
        
        # Remove segments behind player
        self.segments = [s for s in self.segments if not s.is_behind(player_z)]
        
        # Spawn new segments ahead
        while self.next_segment_z < player_z + config.TRACK_SPAWN_DISTANCE:
            self._spawn_segment()
    
    def draw(self, renderer):
        for segment in self.segments:
            # Draw track with texture
            # Use white color so texture colors show through fully
            renderer.draw_mesh(
                segment.track_mesh, 
                segment.get_track_matrix(), 
                (1, 1, 1, 1), 
                texture=segment.texture
            )
            
            # Draw barriers (no texture yet, or reuse?)
            left_mat, right_mat = segment.get_barrier_matrices()
            renderer.draw_mesh(segment.left_barrier, left_mat, segment.barrier_color)
            renderer.draw_mesh(segment.right_barrier, right_mat, segment.barrier_color)
            
            # Draw buildings
            for building in segment.buildings:
                renderer.draw_mesh(building.mesh, building.get_model_matrix(), building.color)
    
    def get_current_theme(self):
        return self.current_theme
    
    def reset(self):
        self.segments.clear()
        self.next_segment_z = 0.0
        self.current_theme = random.choice(list(EnvironmentTheme.THEMES.keys()))
        self.next_theme_change = self.theme_change_distance
        
        for _ in range(config.NUM_TRACK_SEGMENTS):
            self._spawn_segment()
