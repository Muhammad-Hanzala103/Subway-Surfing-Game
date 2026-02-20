"""
Subway Surfer Clone - Configuration
All game settings and constants
"""
from enum import Enum, auto

# Window Settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Rail Runners: Urban Escape"
FPS = 60
VSYNC = True

# OpenGL Settings
OPENGL_VERSION = (3, 3)
DEPTH_BUFFER_SIZE = 24
DOUBLE_BUFFER = True

# Game Physics
GRAVITY = -30.0
JUMP_FORCE = 12.0
PLAYER_SPEED = 15.0  # Forward speed
MAX_SPEED = 35.0
SPEED_INCREMENT = 0.5  # Speed increases over time
LANE_SWITCH_SPEED = 12.0

# Lane Configuration
LANE_WIDTH = 3.0  # Distance between lanes
LANES = [-LANE_WIDTH, 0, LANE_WIDTH]  # Left, Center, Right
NUM_LANES = 3

# Player Settings
PLAYER_HEIGHT = 1.8
PLAYER_WIDTH = 0.8
PLAYER_DEPTH = 0.6
SLIDE_HEIGHT = 0.6
JUMP_HEIGHT = 3.5
SLIDE_DURATION = 0.8  # seconds


# Track Settings
TRACK_WIDTH = 12.0
TRACK_SEGMENT_LENGTH = 50.0
NUM_TRACK_SEGMENTS = 5
TRACK_SPAWN_DISTANCE = 100.0

# Obstacle Settings
OBSTACLE_TYPES = ['train', 'barrier_low', 'barrier_high', 'barrier_full']
MIN_OBSTACLE_DISTANCE = 15.0
MAX_OBSTACLES_PER_SEGMENT = 4

# Train Dimensions
TRAIN_WIDTH = 2.5
TRAIN_HEIGHT = 4.0
TRAIN_LENGTH = 8.0

# Barrier Dimensions
BARRIER_WIDTH = 2.8
BARRIER_LOW_HEIGHT = 1.0  # Must slide
BARRIER_HIGH_HEIGHT = 2.5  # Must jump
BARRIER_FULL_HEIGHT = 4.0  # Must switch lane
BARRIER_DEPTH = 0.5

# Collectibles
COIN_RADIUS = 0.4
COIN_VALUE = 10
COIN_ROTATION_SPEED = 180  # degrees per second
COIN_SPAWN_CHANCE = 0.7
COINS_PER_GROUP = 5
COIN_SPACING = 2.0

# Power-ups
POWERUP_DURATION = 10.0  # seconds
POWERUP_SPAWN_CHANCE = 0.1
MAGNET_RANGE = 5.0
SCORE_MULTIPLIER = 2

# Scoring
DISTANCE_SCORE_RATE = 10  # points per meter
COMBO_TIMEOUT = 2.0  # seconds

# Colors (RGBA)
COLORS = {
    'player': (0.2, 0.6, 1.0, 1.0),  # Blue
    'player_alt': (1.0, 0.4, 0.2, 1.0),  # Orange
    'track': (0.15, 0.15, 0.2, 1.0),  # Dark gray
    'track_lines': (1.0, 1.0, 1.0, 0.8),  # White
    'train': (0.8, 0.2, 0.2, 1.0),  # Red
    'barrier': (0.6, 0.6, 0.1, 1.0),  # Yellow
    'coin': (1.0, 0.85, 0.0, 1.0),  # Gold
    'powerup_magnet': (0.8, 0.2, 0.8, 1.0),  # Purple
    'powerup_shield': (0.2, 0.8, 0.8, 1.0),  # Cyan
    'powerup_score': (0.2, 0.8, 0.2, 1.0),  # Green
    'sky_top': (0.1, 0.1, 0.3, 1.0),  # Dark blue
    'sky_bottom': (0.4, 0.2, 0.5, 1.0),  # Purple
    'ambient': (0.3, 0.3, 0.4, 1.0),
    'ui_primary': (0.2, 0.6, 1.0, 1.0),
    'ui_secondary': (1.0, 0.4, 0.2, 1.0),
    'ui_background': (0.1, 0.1, 0.15, 0.9),
}

# Camera Settings
CAMERA_DISTANCE = 8.0
CAMERA_HEIGHT = 4.0
CAMERA_LOOK_AHEAD = 5.0
CAMERA_SMOOTHING = 5.0

# Particle Settings
MAX_PARTICLES = 500
COIN_PARTICLE_COUNT = 15
CRASH_PARTICLE_COUNT = 50

# Audio Settings
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.7

# Controls
CONTROLS = {
    'left': ['a', 'left'],
    'right': ['d', 'right'],
    'jump': ['w', 'up', 'space'],
    'slide': ['s', 'down'],
    'pause': ['escape', 'p'],
}

# Game States
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    SHOP = auto()

# Difficulty Scaling
DIFFICULTY_INCREASE_INTERVAL = 30.0  # seconds
SPEED_INCREASE_AMOUNT = 2.0
OBSTACLE_DENSITY_INCREASE = 0.1

# File Paths
ASSETS_PATH = "assets"
TEXTURES_PATH = f"{ASSETS_PATH}/textures"
SOUNDS_PATH = f"{ASSETS_PATH}/sounds"
MUSIC_PATH = f"{ASSETS_PATH}/music"
FONTS_PATH = f"{ASSETS_PATH}/fonts"
SHADERS_PATH = f"{ASSETS_PATH}/shaders"

# High Score
HIGH_SCORE_FILE = "highscore.json"
