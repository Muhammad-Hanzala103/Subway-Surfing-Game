"""
3D Camera System
Handles view and projection matrices for the game
"""

import numpy as np
import math

import config


class Camera:
    """3D Camera with follow and smooth movement"""
    
    def __init__(self):
        # Camera position and target
        self.position = np.array([0.0, config.CAMERA_HEIGHT, -config.CAMERA_DISTANCE], dtype=np.float32)
        self.target = np.array([0.0, 0.0, config.CAMERA_LOOK_AHEAD], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        
        # Smooth follow target
        self.target_position = self.position.copy()
        
        # Projection parameters
        self.fov = 60.0  # Field of view in degrees
        self.near = 0.1
        self.far = 500.0
        self.aspect_ratio = config.WINDOW_WIDTH / config.WINDOW_HEIGHT
        
        # Camera shake
        self.shake_amount = 0.0
        self.shake_decay = 5.0
        
        # Matrices
        self._view_matrix = None
        self._projection_matrix = None
        self._update_matrices()
    
    def _update_matrices(self):
        """Update view and projection matrices"""
        self._view_matrix = self._create_look_at()
        self._projection_matrix = self._create_perspective()
    
    def _create_look_at(self):
        """Create view matrix using look-at"""
        # Apply camera shake
        shake_offset = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        if self.shake_amount > 0.01:
            shake_offset = np.array([
                (np.random.random() - 0.5) * self.shake_amount,
                (np.random.random() - 0.5) * self.shake_amount,
                0.0
            ], dtype=np.float32)
        
        eye = self.position + shake_offset
        center = self.target
        up = self.up
        
        f = center - eye
        f = f / np.linalg.norm(f)
        
        s = np.cross(f, up)
        s = s / np.linalg.norm(s)
        
        u = np.cross(s, f)
        
        result = np.identity(4, dtype=np.float32)
        result[0, 0:3] = s
        result[1, 0:3] = u
        result[2, 0:3] = -f
        result[0, 3] = -np.dot(s, eye)
        result[1, 3] = -np.dot(u, eye)
        result[2, 3] = np.dot(f, eye)
        
        return result
    
    def _create_perspective(self):
        """Create perspective projection matrix"""
        fov_rad = math.radians(self.fov)
        f = 1.0 / math.tan(fov_rad / 2.0)
        
        result = np.zeros((4, 4), dtype=np.float32)
        result[0, 0] = f / self.aspect_ratio
        result[1, 1] = f
        result[2, 2] = (self.far + self.near) / (self.near - self.far)
        result[2, 3] = (2.0 * self.far * self.near) / (self.near - self.far)
        result[3, 2] = -1.0
        
        return result
    
    def update(self, delta_time, player_position=None):
        """Update camera to follow player"""
        if player_position is not None:
            # Target position behind and above player
            self.target_position = np.array([
                player_position[0],  # Follow x (lane)
                config.CAMERA_HEIGHT,
                player_position[2] - config.CAMERA_DISTANCE
            ], dtype=np.float32)
            
            # Update look target
            self.target = np.array([
                player_position[0],
                player_position[1] + 1.0,
                player_position[2] + config.CAMERA_LOOK_AHEAD
            ], dtype=np.float32)
        
        # Smooth follow
        smoothing = config.CAMERA_SMOOTHING * delta_time
        self.position = self.position + (self.target_position - self.position) * smoothing
        
        # Decay camera shake
        if self.shake_amount > 0:
            self.shake_amount -= self.shake_decay * delta_time
            if self.shake_amount < 0:
                self.shake_amount = 0
        
        self._update_matrices()
    
    def shake(self, amount):
        """Apply camera shake effect"""
        self.shake_amount = max(self.shake_amount, amount)
    
    def set_aspect_ratio(self, aspect_ratio):
        """Update aspect ratio (on window resize)"""
        self.aspect_ratio = aspect_ratio
        self._update_matrices()
    
    def get_view_matrix(self):
        """Get the view matrix"""
        return self._view_matrix
    
    def get_projection_matrix(self):
        """Get the projection matrix"""
        return self._projection_matrix
    
    def get_view_projection_matrix(self):
        """Get combined view-projection matrix"""
        return np.dot(self._projection_matrix, self._view_matrix)
    
    def screen_to_world(self, screen_x, screen_y, screen_width, screen_height, z_depth=0.0):
        """Convert screen coordinates to world coordinates"""
        # Normalize screen coordinates to [-1, 1]
        ndc_x = (2.0 * screen_x / screen_width) - 1.0
        ndc_y = 1.0 - (2.0 * screen_y / screen_height)
        
        # Create inverse matrices
        inv_proj = np.linalg.inv(self._projection_matrix)
        inv_view = np.linalg.inv(self._view_matrix)
        
        # Transform through inverse projection
        clip_coords = np.array([ndc_x, ndc_y, z_depth, 1.0], dtype=np.float32)
        eye_coords = np.dot(inv_proj, clip_coords)
        eye_coords = np.array([eye_coords[0], eye_coords[1], -1.0, 0.0], dtype=np.float32)
        
        # Transform through inverse view
        world_coords = np.dot(inv_view, eye_coords)
        
        return world_coords[:3]
    
    def reset(self):
        """Reset camera to default position"""
        self.position = np.array([0.0, config.CAMERA_HEIGHT, -config.CAMERA_DISTANCE], dtype=np.float32)
        self.target = np.array([0.0, 0.0, config.CAMERA_LOOK_AHEAD], dtype=np.float32)
        self.target_position = self.position.copy()
        self.shake_amount = 0.0
        self._update_matrices()


def create_orthographic_matrix(left, right, bottom, top, near, far):
    """Create orthographic projection matrix for UI"""
    result = np.zeros((4, 4), dtype=np.float32)
    
    result[0, 0] = 2.0 / (right - left)
    result[1, 1] = 2.0 / (top - bottom)
    result[2, 2] = -2.0 / (far - near)
    result[0, 3] = -(right + left) / (right - left)
    result[1, 3] = -(top + bottom) / (top - bottom)
    result[2, 3] = -(far + near) / (far - near)
    result[3, 3] = 1.0
    
    return result
