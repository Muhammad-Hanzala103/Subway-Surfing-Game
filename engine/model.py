"""
Hierarchical 3D Model System
Allows creating complex models from multiple meshes with parent-child relationships
"""

import numpy as np
import math
from OpenGL.GL import *


class ModelNode:
    """A single node in a model hierarchy"""
    
    def __init__(self, name, mesh=None, color=None, position=None, rotation=None, scale=None, texture=None):
        self.name = name
        self.mesh = mesh
        self.color = list(color) if color else [1, 1, 1, 1]
        self.texture = texture
        
        # Local transform
        self.position = np.array(position if position else [0, 0, 0], dtype=np.float32)
        self.rotation = np.array(rotation if rotation else [0, 0, 0], dtype=np.float32) # Euler angles in degrees
        self.scale = np.array(scale if scale else [1, 1, 1], dtype=np.float32)
        
        self.children = []
        self.parent = None
        
    # [Rest of class methods...]

    # Skip to _draw_node_explicit update:
    def _draw_node_explicit(self, renderer, node, parent_matrix):
        # Calculate local matrix
        local_matrix = np.identity(4, dtype=np.float32)
        
        # Translation
        trans = np.identity(4, dtype=np.float32)
        trans[0:3, 3] = node.position
        
        # Rotation (Euler ZYX)
        rx, ry, rz = np.radians(node.rotation)
        
        cx, sx = math.cos(rx), math.sin(rx)
        cy, sy = math.cos(ry), math.sin(ry)
        cz, sz = math.cos(rz), math.sin(rz)
        
        rot_x = np.array([[1,0,0,0], [0,cx,-sx,0], [0,sx,cx,0], [0,0,0,1]])
        rot_y = np.array([[cy,0,sy,0], [0,1,0,0], [-sy,0,cy,0], [0,0,0,1]])
        rot_z = np.array([[cz,-sz,0,0], [sz,cz,0,0], [0,0,1,0], [0,0,0,1]])
        
        rotation = rot_z @ rot_y @ rot_x
        
        # Scale
        scale = np.identity(4, dtype=np.float32)
        scale[0,0], scale[1,1], scale[2,2] = node.scale
        
        # Combine: T * R * S
        local_matrix = trans @ rotation @ scale
        
        # World matrix for this node
        world_matrix = parent_matrix @ local_matrix
        
        # Draw
        if node.mesh:
            # Use white for textured meshes so texture shows fully
            color = node.color
            if node.texture:
                color = (1, 1, 1, 1)
            renderer.draw_mesh(node.mesh, world_matrix, color, texture=node.texture)
        
        # Children
        for child in node.children:
            self._draw_node_explicit(renderer, child, world_matrix)
    
    def add_child(self, child):
        child.parent = self
        self.children.append(child)
        return child
    
    def get_child(self, name):
        """Find child by name (recursive)"""
        if self.name == name:
            return self
        
        for child in self.children:
            found = child.get_child(name)
            if found:
                return found
        return None
    
    def draw(self, renderer, parent_matrix=None):
        """Draw this node and children"""
        # Calculate local matrix
        glPushMatrix()
        
        # Apply transforms
        glTranslatef(*self.position)
        glRotatef(self.rotation[2], 0, 0, 1) # Z
        glRotatef(self.rotation[1], 0, 1, 0) # Y
        glRotatef(self.rotation[0], 1, 0, 0) # X
        glScalef(*self.scale)
        
        # Draw mesh if exists
        if self.mesh:
            # We use the renderer's shader context but immediate matrix transforms
            # This is mixed-mode (legacy matrix stack + shader)
            # The renderer needs to be aware, or we manually set uniforms
            # For simplicity with our legacy mesh system, we rely on current modelview matrix
            
            # Since our Renderer.draw_mesh uses uniforms, we need to extract the current matrix
            # Or simplified: We just bind the mesh and draw, assuming the renderer 
            # has set up the camera view matrix already.
            
            # Note: Our renderer expects to set u_model matrix. 
            # If we use glPushMatrix/glScalf, that affects the Fixed Function pipeline.
            # If we use shaders, we need to pass the matrix.
            
            # Solution: We will use the retrieve the current modelview matrix 
            # and pass it to the renderer if needed, OR we rely on the renderer 
            # handling Fixed Function ModelView if we switched to #version 120 (which we did).
            
            # renderer.draw_mesh_simple(self.mesh, self.color)
            pass
            
            # Actually, to integrate with our Renderer.draw_mesh which takes a matrix:
            # We can't easily mix internal glRotate with passing a matrix to draw_mesh.
            # So we will implement a recursive matrix calculation instead of using GL stack.
            pass
        
        for child in self.children:
            child.draw(renderer)
            
        glPopMatrix()


class Model:
    """Root container for a hierarchical model"""
    
    def __init__(self):
        self.root = ModelNode("root")
        self.nodes = {}
        self.display_list = None
    
    def add_node(self, name, parent_name="root", **kwargs):
        node = ModelNode(name, **kwargs)
        parent = self.root.get_child(parent_name)
        if parent:
            parent.add_child(node)
            self.nodes[name] = node
        else:
            print(f"Parent {parent_name} not found for {name}")
        return node
    
    def get_node(self, name):
        return self.nodes.get(name)
    
    def draw(self, renderer, position, rotation, scale=[1,1,1]):
        """Draw the entire model at specific location"""
        glPushMatrix()
        
        glTranslatef(position[0], position[1], position[2])
        glRotatef(rotation[2], 0, 0, 1)
        glRotatef(rotation[1], 0, 1, 0)
        glRotatef(rotation[0], 1, 0, 0)
        glScalef(scale[0], scale[1], scale[2])
        
        self._draw_node_recursive(renderer, self.root)
        
        glPopMatrix()
    
    def _draw_node_recursive(self, renderer, node):
        glPushMatrix()
        
        # Apply local transform
        glTranslatef(*node.position)
        glRotatef(node.rotation[2], 0, 0, 1) # Z
        glRotatef(node.rotation[1], 0, 1, 0) # Y
        glRotatef(node.rotation[0], 1, 0, 0) # X
        glScalef(*node.scale)
        
        # Draw mesh
        if node.mesh:
            # We need to get the current ModelView matrix to pass to the shader
            model_view = glGetFloatv(GL_MODELVIEW_MATRIX)
            
            # Since we are already in the correct coordinate space via GL stack,
            # we can pass Identity as the model matrix if the shader multiplies Model * View * Projection
            # BUT our shader expects Model, View, Projection separate.
            # With Legacy OpenGL (which we switched to), we don't need to pass matrices if we use ftransform()
            # or gl_ModelViewProjectionMatrix in shader.
            
            # Let's check shader.py. It uses "u_model", "u_view", "u_projection".
            # And vertex shader does: gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
            
            # HACK: To support hierarchy easily, we will capture the current GL matrix
            # and pass it as the Model matrix.
            # But the View matrix is already applied?
            # If we used gluLookAt, the View matrix is on the stack.
            
            # Better approach for this engine:
            # 1. Manually calculate matrix hierarchy (Node.world_transform)
            # 2. Pass that to renderer.draw_mesh
            
            pass
        
        # Recurse
        for child in node.children:
            self._draw_node_recursive(renderer, child)
            
        glPopMatrix()
    
    def bake(self, renderer):
        """Compile model to OpenGL display list for performance"""
        if self.display_list:
            glDeleteLists(self.display_list, 1)
            
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        
        # Draw at origin (local space)
        identity = np.identity(4, dtype=np.float32)
        self._draw_node_explicit(renderer, self.root, identity)
        
        glEndList()
        print(f"✅ Baked model {self.root.name} to list {self.display_list}")

    # REVISED DRAW METHOD using manual matrix multiplication for robustness
    def draw_explicit(self, renderer, world_matrix):
        """Draw using explicit matrix calculation"""
        if self.display_list:
            # Use baked display list for performance
            glPushMatrix()
            # glMultMatrixf expects column-major, numpy is row-major. 
            # But usually we need to transpose for OpenGL if the matrix is row-major.
            # However, my create_transform is producing standard math matrices.
            # Let's try passing transpose.
            glMultMatrixf(world_matrix.T) 
            glCallList(self.display_list)
            glPopMatrix()
        else:
            self._draw_node_explicit(renderer, self.root, world_matrix)
        
    def _draw_node_explicit(self, renderer, node, parent_matrix):
        # Calculate local matrix
        local_matrix = np.identity(4, dtype=np.float32)
        
        # Translation
        trans = np.identity(4, dtype=np.float32)
        trans[0:3, 3] = node.position
        
        # Rotation (Euler ZYX)
        rx, ry, rz = np.radians(node.rotation)
        
        cx, sx = math.cos(rx), math.sin(rx)
        cy, sy = math.cos(ry), math.sin(ry)
        cz, sz = math.cos(rz), math.sin(rz)
        
        rot_x = np.array([[1,0,0,0], [0,cx,-sx,0], [0,sx,cx,0], [0,0,0,1]])
        rot_y = np.array([[cy,0,sy,0], [0,1,0,0], [-sy,0,cy,0], [0,0,0,1]])
        rot_z = np.array([[cz,-sz,0,0], [sz,cz,0,0], [0,0,1,0], [0,0,0,1]])
        
        rotation = rot_z @ rot_y @ rot_x
        
        # Scale
        scale = np.identity(4, dtype=np.float32)
        scale[0,0], scale[1,1], scale[2,2] = node.scale
        
        # Combine: T * R * S
        local_matrix = trans @ rotation @ scale
        
        # World matrix for this node
        world_matrix = parent_matrix @ local_matrix
        
        # Draw
        if node.mesh:
            renderer.draw_mesh(node.mesh, world_matrix, node.color)
        
        # Children
        for child in node.children:
            self._draw_node_explicit(renderer, child, world_matrix)
