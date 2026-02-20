"""
3D Mesh System - Legacy OpenGL Compatible
Uses display lists and immediate mode for maximum compatibility
"""

from OpenGL.GL import *
import numpy as np
import math


class Mesh:
    """3D Mesh using legacy OpenGL for compatibility"""
    
    def __init__(self, vertices, indices=None, normals=None, tex_coords=None, colors=None):
        self.vertices = np.array(vertices, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32) if indices else None
        
        # Generate default normals if not provided
        if normals is None:
            self.normals = np.zeros_like(self.vertices)
            self.normals[:, 1] = 1.0
        else:
            self.normals = np.array(normals, dtype=np.float32)
        
        # Generate default tex coords
        if tex_coords is None:
            self.tex_coords = np.zeros((len(vertices), 2), dtype=np.float32)
        else:
            self.tex_coords = np.array(tex_coords, dtype=np.float32)
        
        # Generate default colors
        if colors is None:
            self.colors = np.ones((len(vertices), 4), dtype=np.float32)
        else:
            self.colors = np.array(colors, dtype=np.float32)
        
        self.vertex_count = len(vertices)
        self.index_count = len(indices) if indices is not None else 0
        self.use_indices = indices is not None
        
        # Create display list for faster rendering
        self.display_list = glGenLists(1)
        self._compile_display_list()
    
    def _compile_display_list(self):
        """Compile mesh into a display list"""
        glNewList(self.display_list, GL_COMPILE)
        
        if self.use_indices:
            glBegin(GL_TRIANGLES)
            for idx in self.indices:
                if idx < len(self.vertices):
                    glNormal3fv(self.normals[idx])
                    glTexCoord2fv(self.tex_coords[idx])
                    glColor4fv(self.colors[idx])
                    glVertex3fv(self.vertices[idx])
            glEnd()
        else:
            glBegin(GL_TRIANGLES)
            for i in range(self.vertex_count):
                glNormal3fv(self.normals[i])
                glTexCoord2fv(self.tex_coords[i])
                glColor4fv(self.colors[i])
                glVertex3fv(self.vertices[i])
            glEnd()
        
        glEndList()
    
    def draw(self, mode=GL_TRIANGLES):
        """Draw the mesh"""
        glCallList(self.display_list)
    
    def delete(self):
        """Clean up resources"""
        if self.display_list:
            glDeleteLists(self.display_list, 1)
            self.display_list = None


def create_cube(size=1.0, color=None):
    """Create a cube mesh"""
    s = size / 2.0
    
    vertices = [
        # Front face
        [-s, -s,  s], [ s, -s,  s], [ s,  s,  s], [-s,  s,  s],
        # Back face
        [ s, -s, -s], [-s, -s, -s], [-s,  s, -s], [ s,  s, -s],
        # Top face
        [-s,  s,  s], [ s,  s,  s], [ s,  s, -s], [-s,  s, -s],
        # Bottom face
        [-s, -s, -s], [ s, -s, -s], [ s, -s,  s], [-s, -s,  s],
        # Right face
        [ s, -s,  s], [ s, -s, -s], [ s,  s, -s], [ s,  s,  s],
        # Left face
        [-s, -s, -s], [-s, -s,  s], [-s,  s,  s], [-s,  s, -s],
    ]
    
    normals = [
        [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],
        [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],
        [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0],
        [0, -1, 0], [0, -1, 0], [0, -1, 0], [0, -1, 0],
        [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0],
        [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0],
    ]
    
    tex_coords = [[0, 0], [1, 0], [1, 1], [0, 1]] * 6
    
    indices = []
    for i in range(6):
        base = i * 4
        indices.extend([base, base+1, base+2, base, base+2, base+3])
    
    colors = None
    if color:
        colors = [color] * len(vertices)
    
    return Mesh(vertices, indices, normals, tex_coords, colors)


def create_plane(width=1.0, depth=1.0, color=None):
    """Create a horizontal plane mesh"""
    w = width / 2.0
    d = depth / 2.0
    
    vertices = [[-w, 0, -d], [w, 0, -d], [w, 0, d], [-w, 0, d]]
    normals = [[0, 1, 0]] * 4
    tex_coords = [[0, 0], [1, 0], [1, 1], [0, 1]]
    indices = [0, 1, 2, 0, 2, 3]
    
    colors = [color] * 4 if color else None
    return Mesh(vertices, indices, normals, tex_coords, colors)


def create_cylinder(radius=0.5, height=1.0, segments=12, color=None):
    """Create a cylinder mesh"""
    vertices = []
    normals = []
    tex_coords = []
    indices = []
    
    half_h = height / 2.0
    
    # Side vertices
    for i in range(segments + 1):
        angle = (i / segments) * 2.0 * math.pi
        x = math.cos(angle) * radius
        z = math.sin(angle) * radius
        u = i / segments
        
        vertices.append([x, -half_h, z])
        normals.append([math.cos(angle), 0, math.sin(angle)])
        tex_coords.append([u, 0])
        
        vertices.append([x, half_h, z])
        normals.append([math.cos(angle), 0, math.sin(angle)])
        tex_coords.append([u, 1])
    
    # Side indices
    for i in range(segments):
        base = i * 2
        indices.extend([base, base+1, base+3, base, base+3, base+2])
    
    # Top cap
    top_center = len(vertices)
    vertices.append([0, half_h, 0])
    normals.append([0, 1, 0])
    tex_coords.append([0.5, 0.5])
    
    for i in range(segments):
        angle = (i / segments) * 2.0 * math.pi
        x = math.cos(angle) * radius
        z = math.sin(angle) * radius
        vertices.append([x, half_h, z])
        normals.append([0, 1, 0])
        tex_coords.append([0.5 + math.cos(angle)*0.5, 0.5 + math.sin(angle)*0.5])
    
    for i in range(segments):
        indices.extend([top_center, top_center+1+i, top_center+1+((i+1)%segments)])
    
    colors = [color] * len(vertices) if color else None
    return Mesh(vertices, indices, normals, tex_coords, colors)


def create_sphere(radius=0.5, segments=12, rings=8, color=None):
    """Create a sphere mesh"""
    vertices = []
    normals = []
    tex_coords = []
    indices = []
    
    for ring in range(rings + 1):
        phi = math.pi * ring / rings
        y = math.cos(phi) * radius
        ring_radius = math.sin(phi) * radius
        v = ring / rings
        
        for seg in range(segments + 1):
            theta = 2.0 * math.pi * seg / segments
            x = math.cos(theta) * ring_radius
            z = math.sin(theta) * ring_radius
            u = seg / segments
            
            vertices.append([x, y, z])
            nx, ny, nz = x/radius if radius else 0, y/radius if radius else 0, z/radius if radius else 0
            normals.append([nx, ny, nz])
            tex_coords.append([u, v])
    
    for ring in range(rings):
        for seg in range(segments):
            current = ring * (segments + 1) + seg
            next_ring = (ring + 1) * (segments + 1) + seg
            indices.extend([current, next_ring, next_ring + 1, current, next_ring + 1, current + 1])
    
    colors = [color] * len(vertices) if color else None
    return Mesh(vertices, indices, normals, tex_coords, colors)
