"""
Game Manager - Enhanced with All Advanced Features
"""

import pygame
from pygame.locals import *
import random
import config
from config import GameState

from .player import Player, PlayerState
from .track import TrackManager
from .obstacle import ObstacleManager
from .collectible import CollectibleManager, PowerUpType
from .collision import CollisionManager
from .score import ScoreManager


class GameManager:
    """Main game controller with advanced features"""
    
    def __init__(self, renderer, audio_manager=None):
        self.renderer = renderer
        self.audio = audio_manager
        
        # Game state
        self.state = GameState.MENU
        self.time_played = 0.0
        self.difficulty_timer = 0.0
        
        # Game objects
        self.player = Player()
        self.track = TrackManager()
        self.obstacles = ObstacleManager()
        self.collectibles = CollectibleManager()
        self.collision = CollisionManager()
        self.score = ScoreManager()
        
        # Power-up timers
        self.magnet_timer = 0.0
        self.shield_timer = 0.0
        self.score_boost_timer = 0.0
        
        # Screen effects
        self.screen_shake = 0.0
        self.slow_motion = False
        self.slow_motion_timer = 0.0
        self.slow_motion_factor = 0.3
        
        # Near miss bonus
        self.near_miss_score = 50
        
        # Revive system
        self.can_revive = True
        self.revive_cost = 100  # coins
    
    def start_game(self):
        """Start a new game"""
        self.state = GameState.PLAYING
        self.time_played = 0.0
        self.difficulty_timer = 0.0
        
        self.player.reset()
        self.track.reset()
        self.obstacles.reset()
        self.collectibles.reset()
        self.score.reset()
        
        self.magnet_timer = 0.0
        self.shield_timer = 0.0
        self.score_boost_timer = 0.0
        self.screen_shake = 0.0
        self.slow_motion = False
        self.can_revive = True
        
        self.renderer.camera.reset()
        
        if self.audio:
            self.audio.play_music()
    
    def pause_game(self):
        """Pause the game"""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            if self.audio:
                self.audio.pause_music()
    
    def resume_game(self):
        """Resume from pause"""
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            if self.audio:
                self.audio.resume_music()
    
    def revive_player(self):
        """Try to revive player"""
        if self.can_revive and self.score.coins >= self.revive_cost:
            self.score.coins -= self.revive_cost
            self.can_revive = False
            
            # Reset player state
            self.player.state = PlayerState.RUNNING
            self.player.is_invincible = True
            self.player.invincible_timer = 3.0
            self.player.has_shield = True
            
            self.state = GameState.PLAYING
            
            if self.audio:
                self.audio.play_sound('powerup')
            
            return True
        return False
    
    def game_over(self):
        """Handle game over"""
        self.state = GameState.GAME_OVER
        self.score.check_high_score()
        
        if self.audio:
            self.audio.stop_music()
            self.audio.play_sound('crash')
        
        self.screen_shake = 0.8
        self.renderer.shake_camera(0.8)
    
    def handle_input(self, events, keys_pressed):
        """Handle player input"""
        if not hasattr(self, 'settings'):
            from ui.settings import Settings
            self.settings = Settings()
            
        if self.state == GameState.PLAYING:
            for event_type, event_data in events:
                if event_type == 'keydown':
                    action = self.settings.get_action(event_data)
                    
                    # Lane switching
                    if action == 'left':
                        if self.player.move_right() and self.audio:
                            self.audio.play_sound('swoosh')
                    elif action == 'right':
                        if self.player.move_left() and self.audio:
                            self.audio.play_sound('swoosh')
                    
                    # Jump
                    elif action == 'jump':
                        if self.player.jump() and self.audio:
                            self.audio.play_sound('jump')
                    
                    # Slide
                    elif action == 'slide':
                        if self.player.slide() and self.audio:
                            self.audio.play_sound('slide')
                    
                    # Pause
                    elif action == 'pause':
                        self.pause_game()
        
        elif self.state == GameState.PAUSED:
            for event_type, event_data in events:
                if event_type == 'keydown':
                    action = self.settings.get_action(event_data)
                    if action == 'pause':
                        self.resume_game()
        
        elif self.state == GameState.GAME_OVER:
            for event_type, event_data in events:
                if event_type == 'keydown':
                    if event_data == K_RETURN:
                        self.start_game()
                    elif event_data == K_ESCAPE:
                        self.state = GameState.MENU
                    elif event_data == K_r:  # Revive
                        self.revive_player()
        
        elif self.state == GameState.MENU:
            for event_type, event_data in events:
                if event_type == 'keydown':
                    if event_data == K_RETURN:
                        self.start_game()
    
    def update(self, delta_time):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        # Apply slow motion
        actual_dt = delta_time
        if self.slow_motion:
            actual_dt *= self.slow_motion_factor
            self.slow_motion_timer -= delta_time
            if self.slow_motion_timer <= 0:
                self.slow_motion = False
        
        self.time_played += actual_dt
        
        # Update difficulty
        self.difficulty_timer += actual_dt
        if self.difficulty_timer >= config.DIFFICULTY_INCREASE_INTERVAL:
            self.difficulty_timer = 0
            self.obstacles.increase_difficulty()
            self.player.forward_speed = min(
                self.player.forward_speed + config.SPEED_INCREASE_AMOUNT,
                config.MAX_SPEED
            )
        
        # Update power-up timers
        self._update_powerups(actual_dt)
        
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= actual_dt * 3
            if self.screen_shake < 0:
                self.screen_shake = 0
        
        # Update game objects
        prev_z = self.player.position[2]
        self.player.update(actual_dt)
        distance_delta = self.player.position[2] - prev_z
        
        player_z = self.player.position[2]
        self.track.update(player_z)
        self.obstacles.update(player_z, actual_dt)
        self.collectibles.update(player_z, actual_dt)
        
        # Update score
        combo_mult = self.collectibles.get_combo_multiplier()
        score_mult = 2 if self.score_boost_timer > 0 else 1
        self.score.update(distance_delta, score_mult * combo_mult)
        
        # Check collisions
        collision_results = self.collision.update(
            self.player,
            self.obstacles.get_active_obstacles(),
            self.collectibles.get_coins(),
            self.collectibles.get_powerups(),
            self.collectibles.get_mystery_boxes()
        )
        
        # Handle near misses
        for _ in collision_results['near_misses']:
            if self.player.register_near_miss():
                self.score.add_near_miss_bonus(self.near_miss_score)
                if self.audio:
                    self.audio.play_sound('near_miss')
        
        # Handle obstacle collision
        if collision_results['obstacle_hit']:
            if self.player.die():
                self.game_over()
            else:
                # Survived due to power-up
                self.screen_shake = 0.3
                self.renderer.shake_camera(0.3)
        
        # Handle coin collection
        if collision_results['coins_collected']:
            count = len(collision_results['coins_collected'])
            combo = self.collectibles.collect_coin()
            self.score.add_coins(count)
            if self.audio:
                self.audio.play_sound('coin')
        
        # Handle power-up collection
        for powerup in collision_results['powerups_collected']:
            self._apply_powerup(powerup)
            if self.audio:
                self.audio.play_sound('powerup')
        
        # Handle mystery box collection
        for box in collision_results['mystery_boxes_collected']:
            self._open_mystery_box(box)
            if self.audio:
                self.audio.play_sound('mystery')
        
        # Update renderer
        self.renderer.update(actual_dt, self.player.position)
    
    def _update_powerups(self, delta_time):
        """Update power-up timers"""
        if self.magnet_timer > 0:
            self.magnet_timer -= delta_time
            if self.magnet_timer <= 0:
                self.player.has_magnet = False
        
        if self.shield_timer > 0:
            self.shield_timer -= delta_time
            if self.shield_timer <= 0:
                self.player.has_shield = False
        
        if self.score_boost_timer > 0:
            self.score_boost_timer -= delta_time
    
    def _apply_powerup(self, powerup):
        """Apply power-up effect"""
        # Get upgrade levels
        upgrades = self.score.get_upgrades()
        
        # Base durations
        jetpack_dur = 10.0
        magnet_dur = 10.0
        sneakers_dur = 15.0
        multiplier_dur = 15.0
        
        # Apply upgrades (Level 1 is base, +5s per level)
        # Jetpack
        level = upgrades.get('jetpack_level', 1)
        jetpack_dur += (level - 1) * 2.0
        
        # Magnet
        level = upgrades.get('magnet_level', 1)
        magnet_dur += (level - 1) * 5.0
        
        # Sneakers
        level = upgrades.get('sneakers_level', 1)
        sneakers_dur += (level - 1) * 5.0
        
        # Multiplier
        level = upgrades.get('multiplier_level', 1)
        multiplier_dur += (level - 1) * 5.0
        
        
        if powerup.type == PowerUpType.MAGNET:
            self.player.has_magnet = True
            self.magnet_timer = magnet_dur
        
        elif powerup.type == PowerUpType.SHIELD:
            self.player.has_shield = True
            self.shield_timer = 15.0 # Shield has no upgrade yet
        
        elif powerup.type == PowerUpType.SCORE_BOOST:
            self.score_boost_timer = multiplier_dur
        
        elif powerup.type == PowerUpType.HOVERBOARD:
            # Hoverboard is consumable activation, handled by input usually?
            # Or is this a pickup? The collectible is usually a "Mystery Box" or specific item.
            # If we have hoverboard pickup:
            self.player.activate_hoverboard(duration=15.0) # Fixed duration for now
            
        elif powerup.type == PowerUpType.JETPACK:
            self.player.activate_jetpack(duration=jetpack_dur)
            
        elif powerup.type == PowerUpType.SUPER_SNEAKERS:
            self.player.activate_super_sneakers(duration=sneakers_dur)
    
    def _open_mystery_box(self, box):
        """Open mystery box and apply reward"""
        reward_type, reward_value = box.get_reward()
        
        if reward_type == 'coins':
            self.score.add_coins(reward_value)
        elif reward_type == 'powerup':
            # Create temporary powerup object to apply
            class TempPowerup:
                def __init__(self, power_type):
                    self.type = power_type
            self._apply_powerup(TempPowerup(reward_value))
        elif reward_type == 'score':
            self.score.score += reward_value
    
    def trigger_slow_motion(self, duration=1.0):
        """Trigger slow motion effect"""
        self.slow_motion = True
        self.slow_motion_timer = duration
    
    def draw(self):
        """Draw game objects"""
        self.renderer.begin_3d()
        
        # Draw track
        self.track.draw(self.renderer)
        
        # Draw collectibles
        self.collectibles.draw(self.renderer)
        
        # Draw obstacles
        self.obstacles.draw(self.renderer)
        
        # Draw player trail
        self._draw_player_trail()
        
        # Draw player
        # Color handled internally by player model for parts, but invincibility needs handling
        # For now, we rely on player.draw() which uses model colors
        # To support flashing, we would need to pass color override to draw_explicit
        # But our simple model system doesn't support override comfortably yet without recursion update
        # We will ignore detailed flashing for parts for now, or just not flash
        
        self.player.draw(self.renderer)
        
        self.renderer.end_3d()
    
    def _draw_player_trail(self):
        """Draw trail behind player"""
        trail = self.player.get_trail_positions()
        if len(trail) < 2:
            return
        
        # Simple trail effect using small cubes
        from engine.mesh import create_cube
        trail_mesh = create_cube(0.2)
        
        for i, pos in enumerate(trail[:-1]):
            alpha = i / len(trail) * 0.5
            color = self.player.get_color()
            trail_color = (color[0], color[1], color[2], alpha)
            
            import numpy as np
            matrix = np.identity(4, dtype=np.float32)
            matrix[0, 3] = pos[0]
            matrix[1, 3] = pos[1] + 0.5
            matrix[2, 3] = pos[2]
            scale = 0.1 + (i / len(trail)) * 0.2
            matrix[0, 0] = matrix[1, 1] = matrix[2, 2] = scale
            
            self.renderer.draw_mesh(trail_mesh, matrix, trail_color)
    
    def get_active_powerups(self):
        """Get list of active power-ups for HUD"""
        active = []
        if self.player.has_magnet:
            active.append(('MAGNET', self.magnet_timer))
        if self.player.has_shield:
            active.append(('SHIELD', self.shield_timer))
        if self.score_boost_timer > 0:
            active.append(('2X SCORE', self.score_boost_timer))
        if self.player.has_hoverboard:
            active.append(('HOVERBOARD', self.player.hoverboard_timer))
        if self.player.has_jetpack:
            active.append(('JETPACK', self.player.jetpack_timer))
        if self.player.has_super_sneakers:
            active.append(('SUPER JUMP', self.player.super_sneakers_timer))
        return active
