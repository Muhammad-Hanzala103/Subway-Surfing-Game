"""
GLSL Shader Management
Handles shader compilation, linking, and uniform management
"""

from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np
import os

import config


class Shader:
    """Individual shader (vertex or fragment)"""
    
    def __init__(self, source, shader_type):
        """
        Create a shader from source code
        shader_type: GL_VERTEX_SHADER or GL_FRAGMENT_SHADER
        """
        self.shader_type = shader_type
        self.shader_id = self._compile(source)
    
    def _compile(self, source):
        """Compile shader source code"""
        try:
            shader = shaders.compileShader(source, self.shader_type)
            return shader
        except Exception as e:
            shader_type_name = "vertex" if self.shader_type == GL_VERTEX_SHADER else "fragment"
            print(f"Error compiling {shader_type_name} shader: {e}")
            raise
    
    def delete(self):
        """Delete the shader"""
        if self.shader_id:
            glDeleteShader(self.shader_id)
            self.shader_id = None


class ShaderProgram:
    """Complete shader program (vertex + fragment)"""
    
    def __init__(self, vertex_source=None, fragment_source=None, 
                 vertex_file=None, fragment_file=None):
        """Create shader program from source or files"""
        
        # Load from files if paths provided
        if vertex_file:
            vertex_source = self._load_file(vertex_file)
        if fragment_file:
            fragment_source = self._load_file(fragment_file)
        
        if not vertex_source or not fragment_source:
            raise ValueError("Both vertex and fragment shaders required")
        
        self.program_id = self._create_program(vertex_source, fragment_source)
        self._uniform_cache = {}
    
    def _load_file(self, filepath):
        """Load shader source from file"""
        full_path = os.path.join(config.SHADERS_PATH, filepath) if not os.path.isabs(filepath) else filepath
        try:
            with open(full_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Shader file not found: {full_path}")
            raise
    
    def _create_program(self, vertex_source, fragment_source):
        """Compile and link shader program"""
        try:
            # Compile shaders
            vertex_shader = shaders.compileShader(vertex_source, GL_VERTEX_SHADER)
            fragment_shader = shaders.compileShader(fragment_source, GL_FRAGMENT_SHADER)
            
            # Link program
            program = shaders.compileProgram(vertex_shader, fragment_shader)
            
            # Cleanup individual shaders
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
            
            return program
            
        except Exception as e:
            print(f"Error creating shader program: {e}")
            raise
    
    def use(self):
        """Use this shader program for rendering"""
        glUseProgram(self.program_id)
    
    def unuse(self):
        """Stop using this shader program"""
        glUseProgram(0)
    
    def _get_uniform_location(self, name):
        """Get uniform location (cached)"""
        if name not in self._uniform_cache:
            location = glGetUniformLocation(self.program_id, name)
            if location == -1:
                # Uniform not found (might be optimized out)
                pass
            self._uniform_cache[name] = location
        return self._uniform_cache[name]
    
    # Uniform setters
    def set_int(self, name, value):
        """Set integer uniform"""
        location = self._get_uniform_location(name)
        if location != -1:
            glUniform1i(location, value)
    
    def set_float(self, name, value):
        """Set float uniform"""
        location = self._get_uniform_location(name)
        if location != -1:
            glUniform1f(location, value)
    
    def set_vec2(self, name, x, y=None):
        """Set vec2 uniform"""
        location = self._get_uniform_location(name)
        if location != -1:
            if y is None and hasattr(x, '__len__'):
                glUniform2f(location, x[0], x[1])
            else:
                glUniform2f(location, x, y)
    
    def set_vec3(self, name, x, y=None, z=None):
        """Set vec3 uniform"""
        location = self._get_uniform_location(name)
        if location != -1:
            if y is None and hasattr(x, '__len__'):
                glUniform3f(location, x[0], x[1], x[2])
            else:
                glUniform3f(location, x, y, z)
    
    def set_vec4(self, name, x, y=None, z=None, w=None):
        """Set vec4 uniform"""
        location = self._get_uniform_location(name)
        if location != -1:
            if y is None and hasattr(x, '__len__'):
                glUniform4f(location, x[0], x[1], x[2], x[3])
            else:
                glUniform4f(location, x, y, z, w)
    
    def set_mat3(self, name, matrix):
        """Set mat3 uniform"""
        location = self._get_uniform_location(name)
        if location != -1:
            glUniformMatrix3fv(location, 1, GL_FALSE, np.array(matrix, dtype=np.float32))
    
    def set_mat4(self, name, matrix):
        """Set mat4 uniform"""
        location = self._get_uniform_location(name)
        if location != -1:
            glUniformMatrix4fv(location, 1, GL_FALSE, np.array(matrix, dtype=np.float32))
    
    def delete(self):
        """Delete the program"""
        if self.program_id:
            glDeleteProgram(self.program_id)
            self.program_id = None


# Default shader sources (GLSL 120 for compatibility)
DEFAULT_VERTEX_SHADER = """
#version 120

attribute vec3 aPosition;
attribute vec3 aNormal;
attribute vec2 aTexCoord;
attribute vec4 aColor;

varying vec3 vPosition;
varying vec3 vNormal;
varying vec2 vTexCoord;
varying vec4 vColor;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

void main() {
    vec4 worldPos = uModel * vec4(aPosition, 1.0);
    vPosition = worldPos.xyz;
    vNormal = normalize(mat3(uModel) * aNormal);
    vTexCoord = aTexCoord;
    vColor = aColor;
    
    gl_Position = uProjection * uView * worldPos;
}
"""

DEFAULT_FRAGMENT_SHADER = """
#version 120

varying vec3 vPosition;
varying vec3 vNormal;
varying vec2 vTexCoord;
varying vec4 vColor;

uniform vec4 uColor;
uniform vec3 uLightDir;
uniform vec3 uLightColor;
uniform vec3 uAmbientColor;
uniform float uTime;
uniform bool uUseTexture;
uniform sampler2D uTexture;

void main() {
    vec3 normal = normalize(vNormal);
    vec3 lightDir = normalize(uLightDir);
    
    // Diffuse lighting
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * uLightColor;
    
    // Combine lighting
    vec3 lighting = uAmbientColor + diffuse;
    
    // Get base color
    vec4 baseColor;
    if (uUseTexture) {
        baseColor = texture2D(uTexture, vTexCoord) * uColor;
    } else {
        baseColor = uColor * vColor;
    }
    
    // Apply lighting
    vec3 finalColor = baseColor.rgb * lighting;
    
    gl_FragColor = vec4(finalColor, baseColor.a);
}
"""

# Particle shader sources
PARTICLE_VERTEX_SHADER = """
#version 120

attribute vec3 aPosition;
attribute vec4 aColor;
attribute float aSize;

varying vec4 vColor;

uniform mat4 uView;
uniform mat4 uProjection;

void main() {
    vColor = aColor;
    vec4 viewPos = uView * vec4(aPosition, 1.0);
    gl_Position = uProjection * viewPos;
    gl_PointSize = aSize * (300.0 / -viewPos.z);
}
"""

PARTICLE_FRAGMENT_SHADER = """
#version 120

varying vec4 vColor;

void main() {
    vec2 coord = gl_PointCoord - vec2(0.5);
    float dist = length(coord);
    
    if (dist > 0.5) {
        discard;
    }
    
    float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
    gl_FragColor = vec4(vColor.rgb, vColor.a * alpha);
}
"""

# UI Shader sources
UI_VERTEX_SHADER = """
#version 120

attribute vec2 aPosition;
attribute vec2 aTexCoord;
attribute vec4 aColor;

varying vec2 vTexCoord;
varying vec4 vColor;

uniform mat4 uProjection;

void main() {
    vTexCoord = aTexCoord;
    vColor = aColor;
    gl_Position = uProjection * vec4(aPosition, 0.0, 1.0);
}
"""

UI_FRAGMENT_SHADER = """
#version 120

varying vec2 vTexCoord;
varying vec4 vColor;

uniform bool uUseTexture;
uniform sampler2D uTexture;
uniform float uTime;

void main() {
    if (uUseTexture) {
        gl_FragColor = texture2D(uTexture, vTexCoord) * vColor;
    } else {
        gl_FragColor = vColor;
    }
}
"""


def create_default_shader():
    """Create the default 3D shader program"""
    return ShaderProgram(
        vertex_source=DEFAULT_VERTEX_SHADER,
        fragment_source=DEFAULT_FRAGMENT_SHADER
    )


def create_particle_shader():
    """Create the particle shader program"""
    return ShaderProgram(
        vertex_source=PARTICLE_VERTEX_SHADER,
        fragment_source=PARTICLE_FRAGMENT_SHADER
    )


def create_ui_shader():
    """Create the UI shader program"""
    return ShaderProgram(
        vertex_source=UI_VERTEX_SHADER,
        fragment_source=UI_FRAGMENT_SHADER
    )

