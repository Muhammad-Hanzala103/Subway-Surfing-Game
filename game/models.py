"""
Game Models definitions
Procedural generation of complex game objects
"""

import math
from engine.model import Model
from engine.mesh import create_cube
import config


from engine.texture import TextureGenerator

class Models:
    """Factory for game models"""
    
    _train_texture = None
    
    @staticmethod
    def _get_train_texture():
        if Models._train_texture is None:
            # Grungy red metal
            Models._train_texture = TextureGenerator.create_noise(
                256, config.COLORS['train'][:3], intensity=0.15
            )
        return Models._train_texture

    @staticmethod
    def create_player(color=(0.2, 0.6, 1.0, 1.0)):
        """Create a humanoid player model"""
        model = Model()
        
        # Colors
        skin_color = (1.0, 0.8, 0.6, 1.0)
        shirt_color = color
        pants_color = (0.2, 0.2, 0.3, 1.0)
        
        # Body
        model.add_node("body", "root",
                      mesh=create_cube(1.0),
                      color=shirt_color,
                      scale=[0.5, 0.6, 0.25],
                      position=[0, 1.3, 0])
        
        # Head
        model.add_node("head", "body",
                      mesh=create_cube(1.0),
                      color=skin_color,
                      scale=[0.8, 0.8, 1.2],
                      position=[0, 0.8, 0])

        # Arms
        arm_mesh = create_cube(1.0)
        arm_scale = [0.15, 0.6, 0.15]
        
        # Left Arm
        model.add_node("l_arm", "root",
                      mesh=arm_mesh,
                      color=shirt_color,
                      scale=arm_scale,
                      position=[-0.35, 1.3, 0])
        
        # Right Arm
        model.add_node("r_arm", "root",
                      mesh=arm_mesh,
                      color=shirt_color,
                      scale=arm_scale,
                      position=[0.35, 1.3, 0])
        
        # Legs
        leg_mesh = create_cube(1.0)
        leg_scale = [0.2, 0.7, 0.2]
        
        # Left Leg
        model.add_node("l_leg", "root",
                      mesh=leg_mesh,
                      color=pants_color,
                      scale=leg_scale,
                      position=[-0.15, 0.65, 0])
        
        # Right Leg
        model.add_node("r_leg", "root",
                      mesh=leg_mesh,
                      color=pants_color,
                      scale=leg_scale,
                      position=[0.15, 0.65, 0])
                             
        return model
    
    @staticmethod
    def animate_player(model, time, speed_ratio, state):
        """Animate player model based on state"""
        # Running animation
        run_freq = 15.0 * speed_ratio
        arm_angle = math.sin(time * run_freq) * 45
        leg_angle = math.sin(time * run_freq) * 60
        
        l_arm = model.get_node("l_arm")
        r_arm = model.get_node("r_arm")
        l_leg = model.get_node("l_leg")
        r_leg = model.get_node("r_leg")
        body = model.get_node("body")
        
        if not (l_arm and r_arm and l_leg and r_leg and body):
            return

        # Reset defaults
        body.position[1] = 1.3 + math.sin(time * run_freq * 2) * 0.05
        body.rotation = [0, 0, 0]
        
        if state == "jumping":
            l_arm.rotation = [150, 0, 0]
            r_arm.rotation = [150, 0, 0]
            l_leg.rotation = [-30, 0, 0]
            r_leg.rotation = [-30, 0, 0]
            
        elif state == "sliding":
            body.rotation = [-45, 0, 0]
            body.position[1] = 0.5
            l_arm.rotation = [60, 0, 0]
            r_arm.rotation = [60, 0, 0]
            l_leg.rotation = [-70, 0, 0]
            r_leg.rotation = [-70, 0, 0]
            
        elif state == "hoverboard":
            body.rotation = [0, -20, 0] 
            l_arm.rotation = [0, 0, -30]
            r_arm.rotation = [0, 0, 30]
            l_leg.rotation = [10, 0, 0]
            r_leg.rotation = [-10, 0, 0]
            
        elif state == "jetpack":
            body.rotation = [45, 0, 0]
            l_arm.rotation = [180, 0, -20]
            r_arm.rotation = [180, 0, 20]
            l_leg.rotation = [20, 0, 0]
            r_leg.rotation = [20, 0, 0]

        else: # Running
            l_arm.rotation = [-arm_angle, 0, 0]
            r_arm.rotation = [arm_angle, 0, 0]
            l_leg.rotation = [leg_angle, 0, 0]
            r_leg.rotation = [-leg_angle, 0, 0]

    @staticmethod
    def create_train():
        """Create a detailed train model"""
        model = Model()
        
        # Main carriage
        carriage_mesh = create_cube(1.0)
        model.add_node("carriage", "root",
                      mesh=carriage_mesh,
                      color=config.COLORS['train'],
                      scale=[3.0, 3.5, 14.0],
                      position=[0, 2.2, 0],
                      texture=Models._get_train_texture())

        
        # Windows
        window_mesh = create_cube(1.0)
        model.add_node("windows", "carriage",
                      mesh=window_mesh,
                      color=(0.1, 0.1, 0.2, 1.0),
                      scale=[1.02, 0.4, 0.8], 
                      position=[0, 0.2, 0])
        
        # Headlights
        light_mesh = create_cube(1.0)
        model.add_node("light_l", "carriage",
                      mesh=light_mesh,
                      color=(1.0, 1.0, 0.8, 1.0),
                      scale=[0.2, 0.2, 0.1],
                      position=[-0.3, -0.3, 0.51])
        
        model.add_node("light_r", "carriage",
                      mesh=light_mesh,
                      color=(1.0, 1.0, 0.8, 1.0),
                      scale=[0.2, 0.2, 0.1],
                      position=[0.3, -0.3, 0.51])
        
        return model
