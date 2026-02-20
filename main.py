"""
Subway Surfer - Industrial Edition Ultimate
Main Entry Point with ALL Advanced Features

Features:
- 6 Playable Characters with unique stats
- Hoverboard, Jetpack, Super Sneakers power-ups
- Mystery Boxes with random rewards
- Combo System with multiplier
- Near Miss Bonus scoring
- 4 Environment Themes (Urban, Sunset, Neon, Forest)
- Moving Trains
- Daily Challenges & Missions
- Achievements System
- Tutorial for new players
- Settings Menu (Audio, Graphics)
- Particle Effects
- Sound Effects (Generated)
- Revive System
- Double Jump
- Trail Effects

Controls:
- A/D or Left/Right: Switch lanes
- W/Up/Space: Jump (press again for double jump)
- S/Down: Slide
- ESC: Pause
- R: Revive (game over)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from pygame.locals import *

import config
from config import GameState
from engine import Window, Renderer
from game import GameManager, CharacterManager, DailyChallenges, Achievements
from game.player import PlayerState
from game.collectible import PowerUpType
from game.missions import MissionType
from audio import AudioManager
from ui import MenuSystem, HUD, TutorialSystem, SettingsMenu, CharacterSelectMenu, Settings
from effects import ParticleSystem


class SubwaySurferGame:
    """Main game class with ALL advanced features"""
    
    def __init__(self):
        self._print_banner()
        
        # Core systems
        self.window = Window()
        self.renderer = Renderer(self.window)
        self.audio = AudioManager()
        
        # Settings
        self.settings = Settings()
        self.audio.set_music_volume(self.settings.get('music_volume'))
        self.audio.set_sfx_volume(self.settings.get('sfx_volume'))
        
        # Character system
        self.char_manager = CharacterManager()
        
        # Game manager
        self.game = GameManager(self.renderer, self.audio)
        
        # UI systems
        self.menu = MenuSystem(self.window)
        self.menu.set_game_manager(self.game) # Link Shop
        
        self.hud = HUD(self.window)
        self.tutorial = TutorialSystem(self.window)
        self.settings_menu = SettingsMenu(self.window)
        self.char_select = CharacterSelectMenu(self.window, self.char_manager)
        
        # Effects
        self.particles = ParticleSystem(max_particles=2000)
        
        # Progress systems
        self.challenges = DailyChallenges()
        self.achievements = Achievements()
        
        # State tracking
        self.menu_state = 'main'  # main, settings, characters
        self.total_coins = 0
        self.show_tutorial = self.settings.get('show_tutorial')
        self.prev_coins = 0
        self.prev_combo = 0
        self.jumps_this_run = 0
        self.slides_this_run = 0
        self.powerups_this_run = 0
        
        self._load_player_data()
        
        print("\n✅ Game initialized with ALL features!")
        self._print_features()
        
    def _print_banner(self):
        print("=" * 65)
        print("  🎮 RAIL RUNNERS: URBAN ESCAPE 🎮")
        print("  HCI Semester Project - Full Feature Implementation")
        print("=" * 65)
    
    def _print_features(self):
        print("\n🎯 ALL FEATURES:")
        print("   👤 6 Characters | 🛹 Shop & Upgrades | 🚂 Trains")
        print("   🌍 4 Themes | ⛅ Fog & Shadows | 💨 Optimization")
        print("\n🎮 Press ENTER to start...")

    def on_resize(self, width, height):
        if hasattr(self, 'renderer'):
            self.renderer.camera.update_aspect_ratio(width, height)
    
    def _load_player_data(self):
        """Load persistent player data"""
        import json
        try:
            if os.path.exists('player_data.json'):
                with open('player_data.json', 'r') as f:
                    data = json.load(f)
                    self.total_coins = data.get('total_coins', 0)
        except Exception as e:
            print(f"Error loading player data: {e}")
    def _save_player_data(self):
        """Save persistent player data"""
        import json
        try:
            with open('player_data.json', 'w') as f:
                json.dump({
                    'total_coins': self.total_coins
                }, f)
        except Exception as e:
            print(f"Error saving player data: {e}")
    def run(self):
        """Main game loop"""
        while self.window.running:
            delta_time = self.window.update()
            events = self.window.handle_events()
            keys = pygame.key.get_pressed()
            
            # Handle based on state
            if self.game.state == GameState.MENU:
                self._handle_menu_state(events, delta_time)
            
            elif self.game.state == GameState.SHOP:
                self._handle_shop_state(events, delta_time)
            
            elif self.game.state == GameState.PLAYING:
                self._handle_playing_state(events, keys, delta_time)
            
            elif self.game.state == GameState.PAUSED:
                self._handle_paused_state(events, delta_time)
            
            elif self.game.state == GameState.GAME_OVER:
                self._handle_game_over_state(events, delta_time)
            
            # Clear and draw
            self.window.clear()
            self._draw()
            self.window.swap_buffers()
        
        self._save_player_data()
        self.cleanup()
    
    def _handle_shop_state(self, events, delta_time):
        """Handle shop state"""
        self.menu.update(delta_time)
        if self.menu.shop_menu:
            for event_type, event_data in events:
                if event_type == 'keydown':
                    result = self.menu.shop_menu.handle_key(event_data)
                    if result == "back":
                        self.game.state = GameState.MENU
                        self.total_coins = self.game.score.total_coins  # sync back

    def _handle_menu_state(self, events, delta_time):
        """Handle menu state"""
        self.menu.update(delta_time)
        
        # Check which menu is active
        if self.settings_menu.active:
            result = self.settings_menu.handle_input(events)
            if result == 'back':
                self.menu_state = 'main'
                # Apply settings
                self.audio.set_music_volume(self.settings_menu.settings.get('music_volume'))
                self.audio.set_sfx_volume(self.settings_menu.settings.get('sfx_volume'))
        
        elif self.char_select.active:
            self.char_select.update(delta_time)
            result = self.char_select.handle_input(events, self.total_coins)
            if result == 'selected':
                self.menu_state = 'main'
            elif result == 'back':
                self.menu_state = 'main'
            elif isinstance(result, tuple) and result[0] == 'unlock':
                self.total_coins -= result[1]
        
        else:
            # Main menu
            for event_type, event_data in events:
                if event_type == 'keydown':
                    key = event_data
                    
                    if key == K_RETURN:
                        self._start_game()
                    elif key == K_c:
                        self.char_select.open()
                        self.menu_state = 'characters'
                    elif key == K_s:
                        if self.game.state == GameState.MENU:
                            # Enter shop
                            self.game.state = GameState.SHOP
                            # Sync coins
                            self.game.score.total_coins = self.total_coins # Ensure synced
                    elif key == K_o: # Changed from s to o for settings to avoid conflict? No s is Shop now.
                        self.settings_menu.open()
                        self.menu_state = 'settings'
    
    def _handle_playing_state(self, events, keys, delta_time):
        """Handle playing state"""
        # Tutorial first
        if self.tutorial.active:
            if self.tutorial.handle_input(events):
                if self.tutorial.completed:
                    self.settings.set('show_tutorial', False)
            self.particles.update(delta_time)
            return
        
        # Game input
        self.game.handle_input(events, keys)
        
        # Track actions for missions
        for event_type, event_data in events:
            if event_type == 'keydown':
                if event_data in [K_w, K_UP, K_SPACE]:
                    self.jumps_this_run += 1
                elif event_data in [K_s, K_DOWN]:
                    self.slides_this_run += 1
        
        # Update game
        self.game.update(delta_time)
        self.particles.update(delta_time)
        
        # Player effects
        self._update_player_effects(delta_time)
        
        # Check collections for particles
        self._check_collection_events()
        
        # Update missions
        self._update_missions()
    
    def _handle_paused_state(self, events, delta_time):
        """Handle paused state"""
        self.menu.update(delta_time)
        
        for event_type, event_data in events:
            if event_type == 'keydown':
                if event_data in [K_ESCAPE, K_p]:
                    self.game.resume_game()
    
    def _handle_game_over_state(self, events, delta_time):
        """Handle game over state"""
        self.menu.update(delta_time)
        self.particles.update(delta_time)
        
        for event_type, event_data in events:
            if event_type == 'keydown':
                if event_data == K_RETURN:
                    self._end_run()
                    self._start_game()
                elif event_data == K_ESCAPE:
                    self._end_run()
                    self.game.state = GameState.MENU
                elif event_data == K_r:
                    self.game.revive_player()
    
    def _start_game(self):
        """Start a new game"""
        self.game.start_game()
        
        # Apply character bonuses
        char = self.char_manager.get_current_character()
        self.game.player.forward_speed *= (1 + char.speed_bonus)
        self.game.player.base_jump_force *= (1 + char.jump_bonus)
        self.game.player.color = char.color
        
        # Reset run stats
        self.jumps_this_run = 0
        self.slides_this_run = 0
        self.powerups_this_run = 0
        self.prev_coins = 0
        self.prev_combo = 0
        
        # Start tutorial if first time
        if self.show_tutorial and self.settings.get('show_tutorial'):
            self.tutorial.start()
            self.show_tutorial = False
        
        # Update achievements
        self.achievements.update_stats(total_games=1)
    
    def _end_run(self):
        """End of run - update stats"""
        stats = self.game.score.get_stats()
        
        # Update totals
        self.total_coins += stats['coins']
        
        # Update achievements
        self.achievements.update_stats(
            total_coins=stats['coins'],
            total_distance=stats['distance'],
            max_combo=self.game.collectibles.combo_count,
            total_near_miss=stats['near_misses'],
            total_powerups=self.powerups_this_run
        )
        
        # Check achievements
        new_achievements = self.achievements.check_all()
        for ach in new_achievements:
            print(f"🏆 Achievement Unlocked: {ach['name']}")
        
        # Claim mission rewards
        reward = self.challenges.claim_all_rewards()
        if reward > 0:
            self.total_coins += reward
            print(f"🎯 Mission rewards claimed: {reward} coins!")
        
        self._save_player_data()
    
    def _update_player_effects(self, delta_time):
        """Update player particle effects"""
        if not self.settings.get('particles_enabled'):
            return
        
        player = self.game.player
        
        if player.state == PlayerState.HOVERBOARD:
            self.particles.emit_hoverboard_trail(player.position)
        elif player.state == PlayerState.JETPACK:
            self.particles.emit_jetpack_fire(player.position)
        elif player.forward_speed > config.PLAYER_SPEED * 1.5:
            color = player.get_color()
            self.particles.emit_trail(player.position, color,
                                      player.forward_speed / config.MAX_SPEED)
    
    def _check_collection_events(self):
        """Check for collection events and emit particles"""
        current_coins = self.game.score.coins
        current_combo = self.game.collectibles.combo_count
        
        if current_coins > self.prev_coins and self.settings.get('particles_enabled'):
            pos = self.game.player.position.copy()
            pos[1] += 1
            self.particles.emit_coin_collect(pos)
        
        if current_combo > self.prev_combo and current_combo in [5, 10, 20, 50]:
            pos = self.game.player.position.copy()
            pos[1] += 2
            self.particles.emit_powerup_collect(pos, (1.0, 1.0, 0.3, 1.0))
        
        if self.game.player.near_miss_timer > 0.4:
            pos = self.game.player.position.copy()
            self.particles.emit_near_miss(pos)
        
        self.prev_coins = current_coins
        self.prev_combo = current_combo
    
    def _update_missions(self):
        """Update mission progress"""
        score = self.game.score
        
        self.challenges.update_mission_progress(MissionType.COLLECT_COINS, score.coins, absolute=True)
        self.challenges.update_mission_progress(MissionType.TRAVEL_DISTANCE, score.distance, absolute=True)
        self.challenges.update_mission_progress(MissionType.SCORE_TARGET, score.score, absolute=True)
        self.challenges.update_mission_progress(MissionType.COMBO_TARGET, self.game.collectibles.combo_count, absolute=True)
        self.challenges.update_mission_progress(MissionType.JUMP_COUNT, self.jumps_this_run, absolute=True)
        self.challenges.update_mission_progress(MissionType.SLIDE_COUNT, self.slides_this_run, absolute=True)
        self.challenges.update_mission_progress(MissionType.NEAR_MISS_COUNT, score.near_misses, absolute=True)
    
    def _draw(self):
        """Draw everything based on state"""
        if self.game.state == GameState.MENU:
            if self.settings_menu.active:
                self.settings_menu.draw(self.menu.animation_time)
            elif self.char_select.active:
                self.char_select.draw(self.total_coins)
            else:
                self.menu.draw_main_menu()
        
        elif self.game.state == GameState.PLAYING:
            self.game.draw()
            if self.settings.get('particles_enabled'):
                self.particles.draw()
            self.hud.draw(self.game)
            
            if self.settings.get('show_fps'):
                self.hud.draw_fps(self.window.fps)
            
            if self.tutorial.active:
                self.tutorial.draw(self.menu.animation_time)
        
        elif self.game.state == GameState.PAUSED:
            self.game.draw()
            self.hud.draw(self.game)
            self.menu.draw_pause_menu()
        
        elif self.game.state == GameState.GAME_OVER:
            self.game.draw()
            if self.settings.get('particles_enabled'):
                self.particles.draw()
            self.menu.draw_game_over(self.game)
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n🔄 Cleaning up...")
        self.renderer.cleanup()
        self.window.close()
        print("👋 Thanks for playing!")


def main():
    """Entry point"""
    try:
        game = SubwaySurferGame()
        game.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
