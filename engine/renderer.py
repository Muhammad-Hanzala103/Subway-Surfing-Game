"""
Main Renderer - Legacy OpenGL Compatible
Uses immediate mode and fixed-function pipeline
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

from .camera import Camera, create_orthographic_matrix
from .mesh import create_cube, create_plane
from .texture import TextureManager
import config


from .shader import ShaderProgram

class Renderer:
    """Main rendering system using legacy OpenGL"""
    
    def __init__(self, window):
        self.window = window
        self.camera = Camera()
        
        # Shaders
        try:
            self.shader = ShaderProgram(vertex_file="world_curver.vert", 
                                      fragment_file="world_curver.frag")
            print("✅ World Shader Loaded")
        except Exception as e:
            print(f"❌ Shader Error: {e}")
            self.shader = None
            
        self.texture_manager = TextureManager()
        
        # Lighting
        self.light_dir = np.array([0.3, 1.0, 0.5], dtype=np.float32)
        # ... (rest of init)
        self.light_color = np.array([1.0, 0.95, 0.9], dtype=np.float32)
        self.ambient_color = np.array([0.4, 0.4, 0.5], dtype=np.float32)
        
        # Time
        self.time = 0.0
        
        # Setup fixed-function lighting
        self._setup_lighting()
    
    def _setup_lighting(self):
        """Setup OpenGL fixed-function lighting"""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Light position/direction
        light_pos = [self.light_dir[0], self.light_dir[1], self.light_dir[2], 0.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        
        # Light colors
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.95, 0.9, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.5, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        
        # Enable color material
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Smooth shading
        glShadeModel(GL_SMOOTH)
        
        # Fog Setup
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_EXP2)
        glFogfv(GL_FOG_COLOR, [0.6, 0.5, 0.6, 1.0]) # Purple/Haze tint
        glFogf(GL_FOG_DENSITY, 0.012)
        glHint(GL_FOG_HINT, GL_NICEST)
    
    def update(self, delta_time, player_position=None):
        self.time += delta_time
        self.camera.update(delta_time, player_position)
        
        if self.window.width != self.camera.aspect_ratio * self.window.height:
            self.camera.set_aspect_ratio(self.window.get_aspect_ratio())

    def begin_3d(self):
        """Begin 3D rendering"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_LIGHTING)
        
        # Set projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera.fov, self.camera.aspect_ratio, 
                       self.camera.near, self.camera.far)
        
        # Set view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Apply camera transform
        pos = self.camera.position
        target = self.camera.target
        up = self.camera.up
        gluLookAt(pos[0], pos[1], pos[2],
                  target[0], target[1], target[2],
                  up[0], up[1], up[2])
        
        # Update light position
        light_pos = [self.light_dir[0], self.light_dir[1], self.light_dir[2], 0.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        
        # Activate Shader
        if self.shader:
            self.shader.use()
            # Update Uniforms
            # We assume ShaderProgram has set_uniform methods or we use raw glUniform
            # But ShaderProgram in `shader.py` doesn't seem to have helper methods yet?
            # Let's check shader.py again or use direct gl calls if program_id is available.
            # Wrapper in shader.py likely has logic.
            
            # Checking shader.py content from earlier view:
            # It has `_get_uniform_location`. It does NOT have set_uniform methods visible in first 100 lines.
            # I will assume I need to implement them or use glUniform directly.
            # Let's use direct GL calls for now using shader.program_id
            
            pid = self.shader.program_id
            t_loc = glGetUniformLocation(pid, "uTime")
            if t_loc != -1: glUniform1f(t_loc, self.time)
            
            c_loc = glGetUniformLocation(pid, "uCurveStrength")
            if c_loc != -1: glUniform1f(c_loc, 0.001) # Tuning value
            
            # Handle texture uniform in draw calls or set default here
            tex_loc = glGetUniformLocation(pid, "uUseTexture")
            if tex_loc != -1: glUniform1i(tex_loc, 0) # Default false
            
    def end_3d(self):
        # Disable Shader
        if self.shader:
            self.shader.unuse()
    
    def begin_ui(self):
        """Begin 2D UI rendering"""
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.window.width, 0, self.window.height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
    
    def end_ui(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    def draw_mesh(self, mesh, model_matrix, color=(1, 1, 1, 1), texture=None):
        """Draw a mesh with transform, color, and optional texture"""
        glPushMatrix()
        
        # Apply model transformation
        glMultMatrixf(model_matrix.T.flatten())
        
        # Set color
        glColor4f(color[0], color[1], color[2], color[3] if len(color) > 3 else 1.0)
        
        # Bind texture if provided
        use_texture = False
        if texture:
            glEnable(GL_TEXTURE_2D)
            texture.bind()
            use_texture = True
        else:
            # For non-textured objects, we can either:
            # 1. Disable texturing (if shader handles it)
            # 2. Use a white texture (recommended for simple shader logic)
            # Since shader uses "uUseTexture", we can toggle that.
            # But we should also bind white texture to be safe or disable GL_TEXTURE_2D
            
            # Use White texture and Enable = safer for fixed pipeline
            glEnable(GL_TEXTURE_2D)
            self.texture_manager.get_default().bind()
            use_texture = False # Logic: Color only
            
        # Update Shader Uniform
        if self.shader:
            pid = self.shader.program_id
            tex_loc = glGetUniformLocation(pid, "uUseTexture")
            if tex_loc != -1: glUniform1i(tex_loc, 1 if use_texture else 0)
            
            # Also ensure texture unit 0 is set
            sampler_loc = glGetUniformLocation(pid, "uTexture")
            if sampler_loc != -1: glUniform1i(sampler_loc, 0)
        
        # Draw the mesh
        mesh.draw()
        
        # Unbind texture
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
        
        glPopMatrix()
    
    def draw_shadow(self, position, radius, opacity=0.4):
        """Draw a simple circular shadow"""
        # Ensure shader knows we aren't using a texture
        if self.shader:
             pid = self.shader.program_id
             tex_loc = glGetUniformLocation(pid, "uUseTexture")
             if tex_loc != -1: glUniform1i(tex_loc, 0)
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_TEXTURE_2D)
        
        glPushMatrix()
        glTranslatef(position[0], 0.02, position[2]) # Slightly above ground
        glRotatef(-90, 1, 0, 0) # Flat on ground
        
        glColor4f(0, 0, 0, opacity)
        
        # Draw circle using simple fan
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0, 0)
        for i in range(13): # 12 segments
            angle = i * (2.0 * 3.14159 / 12)
            glVertex2f(math.cos(angle) * radius, math.sin(angle) * radius)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()

    def shake_camera(self, amount):
        self.camera.shake(amount)
    
    def cleanup(self):
        self.texture_manager.unload_all()
