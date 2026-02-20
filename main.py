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
import pygame
from app.game_app import GameApp

def main():
    """Entry point"""
    try:
        game = GameApp()
        game.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
