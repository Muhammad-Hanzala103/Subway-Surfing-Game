"""
Texture Management System
"""

from OpenGL.GL import *
from PIL import Image
import os
import numpy as np
import config


class Texture:
    """OpenGL Texture wrapper"""
    
    def __init__(self, filepath=None, data=None, width=None, height=None):
        self.texture_id = glGenTextures(1)
        self.width = width or 0
        self.height = height or 0
        
        if filepath:
            self._load_from_file(filepath)
        elif data is not None:
            self._load_from_data(data, width, height)
        else:
            self._create_default()
    
    def _load_from_file(self, filepath):
        try:
            if not os.path.exists(filepath):
                filepath = os.path.join(config.TEXTURES_PATH, filepath)
            
            image = Image.open(filepath).transpose(Image.FLIP_TOP_BOTTOM)
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            self.width, self.height = image.width, image.height
            self._upload_data(np.array(image, dtype=np.uint8))
        except Exception as e:
            print(f"Error loading texture {filepath}: {e}")
            self._create_default()
    
    def _load_from_data(self, data, width, height):
        self.width, self.height = width, height
        self._upload_data(np.array(data, dtype=np.uint8))
    
    def _create_default(self):
        self.width = self.height = 2
        data = np.array([[255,255,255,255], [200,200,200,255],
                         [200,200,200,255], [255,255,255,255]], dtype=np.uint8)
        self._upload_data(data)
    
    def _upload_data(self, data):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def bind(self, unit=0):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
    
    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def delete(self):
        if self.texture_id:
            glDeleteTextures(1, [self.texture_id])
            self.texture_id = None


class TextureManager:
    """Manages loading and caching textures"""
    
    def __init__(self):
        self._textures = {}
        self._default_texture = None
    
    def load(self, name, filepath):
        if name not in self._textures:
            self._textures[name] = Texture(filepath)
        return self._textures[name]
    
    def get(self, name):
        return self._textures.get(name, self.get_default())
    
    def get_default(self):
        if self._default_texture is None:
            self._default_texture = Texture()
        return self._default_texture
    
    def create_color_texture(self, name, color, size=2):
        if name not in self._textures:
            r, g, b = int(color[0]*255), int(color[1]*255), int(color[2]*255)
            a = int(color[3]*255) if len(color) > 3 else 255
            data = np.full((size, size, 4), [r, g, b, a], dtype=np.uint8)
            self._textures[name] = Texture(data=data, width=size, height=size)
        return self._textures[name]
    
    def unload_all(self):
        for texture in self._textures.values():
            texture.delete()
        self._textures.clear()
        if self._default_texture:
            self._default_texture.delete()
            self._default_texture = None

class TextureGenerator:
    """Generates procedural textures"""
    
    @staticmethod
    def create_checkers(size, color1, color2, num_checks=4):
        """Create checkerboard pattern"""
        arr = np.zeros((size, size, 4), dtype=np.uint8)
        check_size = size // num_checks
        
        # Ensure RGBA and uint8
        c1 = list(color1)
        if len(c1) == 3: c1.append(1.0)
        c1 = (np.array(c1) * 255).astype(np.uint8)
        
        c2 = list(color2)
        if len(c2) == 3: c2.append(1.0)
        c2 = (np.array(c2) * 255).astype(np.uint8)
        
        for y in range(size):
            for x in range(size):
                cx = (x // check_size) % 2
                cy = (y // check_size) % 2
                
                if (cx + cy) % 2 == 0:
                    arr[y, x] = c1
                else:
                    arr[y, x] = c2
                    
        return Texture(data=arr, width=size, height=size)

    @staticmethod
    def create_noise(size, color, intensity=0.1):
        """Create noise texture (good for asphalt/ground)"""
        # Ensure RGBA
        col = list(color)
        if len(col) == 3:
            col.append(1.0)
            
        # Base color shape (1, 1, 4) for broadcasting
        base = np.array(col, dtype=np.float32) * 255
        base = base.reshape(1, 1, 4)
        
        # Generate random noise [-1, 1]
        noise = np.random.rand(size, size, 4) * 2 - 1
        noise[:, :, 3] = 0  # No alpha noise
        
        # Apply intensity
        noise = noise * (intensity * 255)
        
        # Add to base
        arr = base + noise
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        arr[:, :, 3] = 255 # Ensure full opacity
        
        return Texture(data=arr, width=size, height=size)

    @staticmethod
    def create_stripes(size, color1, color2, stripe_width=20):
        """Create diagonal stripes (hazard warning)"""
        arr = np.zeros((size, size, 4), dtype=np.uint8)
        
        # Ensure RGBA
        c1 = list(color1)
        if len(c1) == 3: c1.append(1.0)
        c1 = (np.array(c1) * 255).astype(np.uint8)
        
        c2 = list(color2)
        if len(c2) == 3: c2.append(1.0)
        c2 = (np.array(c2) * 255).astype(np.uint8)
        
        for y in range(size):
            for x in range(size):
                # Diagonal x+y
                if ((x + y) // stripe_width) % 2 == 0:
                    arr[y, x] = c1
                else:
                    arr[y, x] = c2
                    
        return Texture(data=arr, width=size, height=size)

    @staticmethod
    def create_bricks(size, brick_color, mortar_color, bricks_h=4, bricks_v=8):
        """Create brick pattern"""
        # Ensure RGBA
        mc = list(mortar_color)
        if len(mc) == 3: mc.append(1.0)
        
        bc = list(brick_color)
        if len(bc) == 3: bc.append(1.0)
        
        arr = np.full((size, size, 4), mc, dtype=np.float32) * 255
        
        brick_h = size // bricks_h
        brick_w = size // bricks_v
        mortar_size = size // 40
        
        b_col = np.array(brick_color) * 255
        
        for y in range(size):
            row = y // brick_h
            # Offset every other row
            x_offset = (brick_w // 2) if row % 2 == 1 else 0
            
            for x in range(size):
                if (y % brick_h > mortar_size) and ((x + x_offset) % brick_w > mortar_size):
                    # Add some noise to bricks
                    noise = (np.random.random() - 0.5) * 20
                    col = np.clip(b_col + noise, 0, 255)
                    arr[y, x] = col
                    
        return Texture(data=arr.astype(np.uint8), width=size, height=size)
