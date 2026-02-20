"""
Enhanced Particle System with multiple effect types
"""

import numpy as np
import random
import math
from OpenGL.GL import *
import config


class Particle:
    """Single particle with physics"""
    
    def __init__(self, position, velocity, color, size, lifetime, gravity=True):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity, dtype=np.float32)
        self.color = list(color)
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.active = True
        self.gravity = gravity
        self.rotation = random.random() * 360
        self.rotation_speed = random.uniform(-180, 180)
    
    def update(self, delta_time):
        if not self.active:
            return
        
        self.position += self.velocity * delta_time
        
        if self.gravity:
            self.velocity[1] += config.GRAVITY * 0.3 * delta_time
        
        self.rotation += self.rotation_speed * delta_time
        
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.active = False
        
        # Fade out
        alpha = self.lifetime / self.max_lifetime
        self.color[3] = alpha
        
        # Shrink
        self.size *= 0.98


class ParticleSystem:
    """Advanced particle system with multiple effects"""
    
    def __init__(self, max_particles=1000):
        self.max_particles = max_particles
        self.particles = []
    
    def emit(self, position, count, color, speed_range=(2, 5), 
             size_range=(5, 15), lifetime=1.0, gravity=True, spread=1.0):
        """Emit particles at position"""
        
        # FPS-aware scaling: scale down particle count if FPS drops to maintain performance
        fps_ratio = min(1.0, config.FPS / 60.0) 
        actual_count = max(1, int(count * fps_ratio))
        
        for _ in range(actual_count):
            if len(self.particles) >= self.max_particles:
                # Remove oldest particle if at limit
                self.particles.pop(0)
            
            velocity = np.array([
                random.uniform(-spread, spread),
                random.uniform(0.5, 1.5),
                random.uniform(-spread, spread)
            ], dtype=np.float32)
            velocity = velocity / np.linalg.norm(velocity)
            velocity *= random.uniform(speed_range[0], speed_range[1])
            
            size = random.uniform(size_range[0], size_range[1])
            life = lifetime * random.uniform(0.7, 1.3)
            
            self.particles.append(Particle(
                position.copy(), velocity, list(color), size, life, gravity
            ))
    
    def emit_coin_collect(self, position):
        """Golden coin collection effect"""
        self.emit(
            position, 
            20, 
            (1.0, 0.85, 0.0, 1.0),
            speed_range=(4, 8),
            size_range=(8, 15),
            lifetime=0.8,
            spread=0.5
        )
        # Sparkles
        self.emit(
            position,
            10,
            (1.0, 1.0, 0.5, 1.0),
            speed_range=(2, 4),
            size_range=(3, 6),
            lifetime=0.5,
            gravity=False,
            spread=1.5
        )
    
    def emit_powerup_collect(self, position, color):
        """Power-up collection effect"""
        self.emit(
            position,
            30,
            color,
            speed_range=(5, 10),
            size_range=(10, 20),
            lifetime=1.0,
            spread=1.0
        )
        # Ring effect
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            vel = np.array([math.cos(angle), 0.5, math.sin(angle)], dtype=np.float32) * 5
            self.particles.append(Particle(
                position.copy(), vel, list(color), 15, 1.0, False
            ))
    
    def emit_mystery_box(self, position):
        """Mystery box opening effect"""
        # Golden burst
        self.emit(
            position,
            40,
            (1.0, 0.8, 0.2, 1.0),
            speed_range=(6, 12),
            size_range=(12, 25),
            lifetime=1.2
        )
        # Stars
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            vel = np.array([math.cos(angle), 2, math.sin(angle)], dtype=np.float32) * 8
            self.particles.append(Particle(
                position.copy(), vel, [1.0, 1.0, 0.3, 1.0], 20, 1.5, True
            ))
    
    def emit_crash(self, position):
        """Crash/death effect"""
        # Red explosion
        self.emit(
            position,
            60,
            (1.0, 0.2, 0.1, 1.0),
            speed_range=(8, 18),
            size_range=(15, 30),
            lifetime=1.5,
            spread=2.0
        )
        # Debris
        self.emit(
            position,
            30,
            (0.5, 0.5, 0.5, 1.0),
            speed_range=(4, 10),
            size_range=(5, 12),
            lifetime=2.0
        )
    
    def emit_near_miss(self, position):
        """Near miss celebration effect"""
        self.emit(
            position,
            15,
            (0.2, 1.0, 0.5, 1.0),
            speed_range=(3, 6),
            size_range=(8, 15),
            lifetime=0.6,
            gravity=False,
            spread=0.3
        )
    
    def emit_trail(self, position, color, intensity=1.0):
        """Emit trail particles behind player"""
        if random.random() > intensity * 0.5:
            return
        
        pos = position.copy()
        pos[1] += 0.3
        
        vel = np.array([
            random.uniform(-0.5, 0.5),
            random.uniform(0, 1),
            -3  # Moving backward
        ], dtype=np.float32)
        
        self.particles.append(Particle(
            pos, vel, list(color) + [0.6], random.uniform(5, 10), 0.5, False
        ))
    
    def emit_hoverboard_trail(self, position):
        """Hoverboard glow trail"""
        pos = position.copy()
        pos[1] = 0.2
        
        for _ in range(2):
            vel = np.array([
                random.uniform(-0.3, 0.3),
                random.uniform(-0.5, 0.5),
                -5
            ], dtype=np.float32)
            
            self.particles.append(Particle(
                pos.copy(), vel, [1.0, 0.5, 0.0, 0.8], 12, 0.4, False
            ))
    
    def emit_jetpack_fire(self, position):
        """Jetpack fire effect"""
        pos = position.copy()
        pos[1] -= 0.5
        
        for _ in range(3):
            vel = np.array([
                random.uniform(-0.5, 0.5),
                random.uniform(-8, -5),
                random.uniform(-0.5, 0.5)
            ], dtype=np.float32)
            
            # Fire colors
            color_choice = random.choice([
                [1.0, 0.5, 0.0, 1.0],
                [1.0, 0.3, 0.0, 1.0],
                [1.0, 0.8, 0.2, 1.0]
            ])
            
            self.particles.append(Particle(
                pos.copy(), vel, color_choice, random.uniform(15, 25), 0.3, False
            ))
    
    def update(self, delta_time):
        """Update all particles"""
        for particle in self.particles:
            particle.update(delta_time)
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.active]
    
    def draw(self):
        """Draw all particles"""
        if not self.particles:
            return
        
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_POINT_SMOOTH)
        
        for particle in self.particles:
            glPointSize(particle.size)
            glBegin(GL_POINTS)
            glColor4f(*particle.color)
            glVertex3f(*particle.position)
            glEnd()
        
        glPopAttrib()
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()
