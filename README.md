# Subway Surfing Game

A fast-paced endless runner game developed in Python using `pygame` and `PyOpenGL`.

## Features
- Dynamic obstacle generation (trains, barriers, coins)
- 3D perspective rendering using OpenGL
- Unlockable characters and hoverboards
- Daily challenges and achievements
- Interactive menus and shop system

## Prerequisites
- Python 3.9+ 
- Dependencies listed in `requirements.txt`

## Installation
1. Clone or download the repository.
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game
To start the game, run the `main.py` script:
```bash
python main.py
```

## Running Tests
This project uses `pytest` for automated testing. To run the tests:
```bash
python -m pytest
```

## Project Structure
- `app/`: Game application entry points and core initialization.
- `assets/`: 3D models and textures (e.g., characters, obstacles, items).
- `audio/`: Sound effects and background music assets.
- `core/`: Core data structures, enums, and constants.
- `effects/`: Particle systems, shaders, and visual effects.
- `engine/`: Low-level rendering, OpenGL wrappers, and camera logic.
- `game/`: Gameplay logic, entity management, level generation, and physics.
- `scenes/`: Game states (Menu, Play, Pause, Shop, GameOver).
- `services/`: Business logic decoupled from UI (Shop, Progress, Challenges).
- `ui/`: User interface components, HUD, and text rendering.
- `tests/`: Automated test suite for game mechanics and rendering sanity.

## Data Files
User progress and settings are stored locally in the following JSON files (automatically generated on first run):
- `player_data.json`: Profile unlocks, coins, and current selection.
- `highscore.json`: Local highscore records.
- `settings.json`: User preferences (audio, graphics, controls).
- `achievements.json`: Unlocked achievements and stats.
- `daily_challenges.json`: Active missions and progress.

## Controls
- **Arrow Keys / WASD:** Move left/right, jump, and duck.
- **Space:** Select / Confirm in menus.
- **Esc:** Pause the game or go back in menus.
