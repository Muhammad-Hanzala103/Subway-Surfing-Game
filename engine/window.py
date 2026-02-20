"""
Window Management with Pygame and OpenGL
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import config


class Window:
    """Manages the game window and OpenGL context"""
    
    def __init__(self, width=None, height=None, title=None):
        self.width = width or config.WINDOW_WIDTH
        self.height = height or config.WINDOW_HEIGHT
        self.title = title or config.WINDOW_TITLE
        self.running = True
        self.clock = None
        self.delta_time = 0.0
        self.fps = 0
        
        self._init_pygame()
        self._init_opengl()
    
    def _init_pygame(self):
        """Initialize Pygame with OpenGL context"""
        pygame.init()
        
        # Set basic OpenGL attributes (Windows compatible)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, config.DEPTH_BUFFER_SIZE)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        
        # Create window
        flags = DOUBLEBUF | OPENGL
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption(self.title)
        
        # Setup clock
        self.clock = pygame.time.Clock()
        
        # Show mouse cursor
        pygame.mouse.set_visible(True)
    
    def _init_opengl(self):
        """Initialize OpenGL settings"""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable face culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        
        # Set clear color
        glClearColor(0.1, 0.1, 0.15, 1.0)
        
        # Set viewport
        glViewport(0, 0, self.width, self.height)
        
        # Print OpenGL info
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
        print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
        print(f"Renderer: {glGetString(GL_RENDERER).decode()}")
    
    def clear(self):
        """Clear the screen"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    def swap_buffers(self):
        """Swap double buffers"""
        pygame.display.flip()
    
    def update(self):
        """Update window and return delta time"""
        self.delta_time = self.clock.tick(config.FPS) / 1000.0
        self.fps = self.clock.get_fps()
        return self.delta_time
    
    def handle_events(self):
        """Process window events and return list of game events"""
        events = []
        
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                events.append(('quit', None))
            
            elif event.type == KEYDOWN:
                events.append(('keydown', event.key))
            
            elif event.type == KEYUP:
                events.append(('keyup', event.key))
            
            elif event.type == MOUSEBUTTONDOWN:
                events.append(('mousedown', (event.button, event.pos)))
            
            elif event.type == MOUSEBUTTONUP:
                events.append(('mouseup', (event.button, event.pos)))
            
            elif event.type == MOUSEMOTION:
                events.append(('mousemove', event.pos))
            
            elif event.type == VIDEORESIZE:
                self.resize(event.w, event.h)
                events.append(('resize', (event.w, event.h)))
        
        return events
    
    def resize(self, width, height):
        """Handle window resize"""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
    
    def get_aspect_ratio(self):
        """Get window aspect ratio"""
        return self.width / self.height if self.height > 0 else 1.0
    
    def get_size(self):
        """Get window size"""
        return (self.width, self.height)
    
    def set_title(self, title):
        """Set window title"""
        pygame.display.set_caption(title)
    
    def is_key_pressed(self, key):
        """Check if a key is currently pressed"""
        keys = pygame.key.get_pressed()
        return keys[key]
    
    def get_mouse_pos(self):
        """Get current mouse position"""
        return pygame.mouse.get_pos()
    
    def close(self):
        """Clean up and close window"""
        pygame.quit()
        self.running = False
