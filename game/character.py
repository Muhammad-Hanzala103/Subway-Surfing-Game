"""
Character System - Multiple playable characters with stats
"""

from enum import Enum
from engine.mesh import create_cube


class CharacterType(Enum):
    JAKE = "jake"
    TRICKY = "tricky"
    FRESH = "fresh"
    SPIKE = "spike"
    YUTANI = "yutani"
    NINJA = "ninja"


class Character:
    """Playable character with unique stats"""
    
    # Character definitions
    CHARACTERS = {
        CharacterType.JAKE: {
            'name': 'Jake',
            'description': 'The original surfer! Balanced stats.',
            'color': (0.2, 0.6, 1.0, 1.0),  # Blue
            'alt_color': (0.3, 0.7, 1.0, 1.0),
            'speed_bonus': 0,
            'jump_bonus': 0,
            'magnet_bonus': 0,
            'unlocked': True,
            'cost': 0
        },
        CharacterType.TRICKY: {
            'name': 'Tricky',
            'description': 'Skateboard expert! +10% Speed.',
            'color': (1.0, 0.4, 0.6, 1.0),  # Pink
            'alt_color': (1.0, 0.5, 0.7, 1.0),
            'speed_bonus': 0.1,
            'jump_bonus': 0,
            'magnet_bonus': 0,
            'unlocked': True,
            'cost': 0
        },
        CharacterType.FRESH: {
            'name': 'Fresh',
            'description': 'Street dancer! +15% Jump height.',
            'color': (0.2, 0.8, 0.4, 1.0),  # Green
            'alt_color': (0.3, 0.9, 0.5, 1.0),
            'speed_bonus': 0,
            'jump_bonus': 0.15,
            'magnet_bonus': 0,
            'unlocked': True,
            'cost': 0
        },
        CharacterType.SPIKE: {
            'name': 'Spike',
            'description': 'Punk rocker! +20% Coin magnet range.',
            'color': (1.0, 0.3, 0.2, 1.0),  # Red
            'alt_color': (1.0, 0.4, 0.3, 1.0),
            'speed_bonus': 0,
            'jump_bonus': 0,
            'magnet_bonus': 0.2,
            'unlocked': False,
            'cost': 500
        },
        CharacterType.YUTANI: {
            'name': 'Yutani',
            'description': 'Space explorer! +5% Speed, +10% Jump.',
            'color': (0.6, 0.3, 0.9, 1.0),  # Purple
            'alt_color': (0.7, 0.4, 1.0, 1.0),
            'speed_bonus': 0.05,
            'jump_bonus': 0.1,
            'magnet_bonus': 0,
            'unlocked': False,
            'cost': 1000
        },
        CharacterType.NINJA: {
            'name': 'Ninja',
            'description': 'Silent runner! +10% all stats.',
            'color': (0.1, 0.1, 0.1, 1.0),  # Black
            'alt_color': (0.2, 0.2, 0.2, 1.0),
            'speed_bonus': 0.1,
            'jump_bonus': 0.1,
            'magnet_bonus': 0.1,
            'unlocked': False,
            'cost': 2000
        }
    }
    
    def __init__(self, char_type=CharacterType.JAKE):
        self.type = char_type
        self.data = self.CHARACTERS[char_type]
        self.mesh = create_cube(1.0)
    
    @property
    def name(self):
        return self.data['name']
    
    @property
    def description(self):
        return self.data['description']
    
    @property
    def color(self):
        return self.data['color']
    
    @property
    def alt_color(self):
        return self.data['alt_color']
    
    @property
    def speed_bonus(self):
        return self.data['speed_bonus']
    
    @property
    def jump_bonus(self):
        return self.data['jump_bonus']
    
    @property
    def magnet_bonus(self):
        return self.data['magnet_bonus']
    
    @property
    def is_unlocked(self):
        return self.data['unlocked']
    
    @property
    def cost(self):
        return self.data['cost']
    
    @classmethod
    def get_all_characters(cls):
        return list(CharacterType)
    
    @classmethod
    def unlock_character(cls, char_type):
        if char_type in cls.CHARACTERS:
            cls.CHARACTERS[char_type]['unlocked'] = True
    
    @classmethod
    def is_character_unlocked(cls, char_type):
        return cls.CHARACTERS.get(char_type, {}).get('unlocked', False)


class CharacterManager:
    """Manages character selection and unlocks"""
    
    def __init__(self):
        self.current_character = CharacterType.JAKE
        self.selected_index = 0
        self.total_coins_earned = 0
    
    def get_current_character(self):
        return Character(self.current_character)
    
    def select_next(self):
        chars = Character.get_all_characters()
        self.selected_index = (self.selected_index + 1) % len(chars)
        return chars[self.selected_index]
    
    def select_previous(self):
        chars = Character.get_all_characters()
        self.selected_index = (self.selected_index - 1) % len(chars)
        return chars[self.selected_index]
    
    def get_selected(self):
        chars = Character.get_all_characters()
        return Character(chars[self.selected_index])
    
    def confirm_selection(self):
        chars = Character.get_all_characters()
        selected = chars[self.selected_index]
        
        if Character.is_character_unlocked(selected):
            self.current_character = selected
            return True
        return False
    
    def try_unlock(self, char_type, available_coins):
        char = Character(char_type)
        if not char.is_unlocked and available_coins >= char.cost:
            Character.unlock_character(char_type)
            return char.cost
        return 0
    
    def get_character_list(self):
        """Get list of all characters with their info"""
        result = []
        for char_type in Character.get_all_characters():
            char = Character(char_type)
            result.append({
                'type': char_type,
                'name': char.name,
                'description': char.description,
                'color': char.color,
                'unlocked': char.is_unlocked,
                'cost': char.cost,
                'speed_bonus': char.speed_bonus,
                'jump_bonus': char.jump_bonus,
                'magnet_bonus': char.magnet_bonus
            })
        return result
