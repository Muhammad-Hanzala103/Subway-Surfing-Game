"""
Score System - Enhanced with combos and near miss
"""

import json
import os
import config


class ScoreManager:
    """Manages scoring with combo and near miss bonuses"""
    
    def __init__(self):
        self.score = 0
        self.coins = 0
        self.distance = 0.0
        self.multiplier = 1
        
        # Power-up Upgrades
        self.upgrades = {
            'jetpack_level': 1,
            'magnet_level': 1,
            'sneakers_level': 1,
            'multiplier_level': 1
        }
        self.total_coins = 0 # Persistent wallet
        
        self.load_high_score()
    
    def update(self, distance_delta, multiplier=1):
        """Update score based on distance traveled"""
        self.distance += distance_delta
        self.multiplier = multiplier
        
        distance_points = int(distance_delta * config.DISTANCE_SCORE_RATE * self.multiplier)
        self.score += distance_points
    
    def add_coins(self, count):
        """Add collected coins"""
        self.coins += count
        self.coins_collected += count
        self.total_coins += count # Add to wallet
        self.score += count * config.COIN_VALUE * self.multiplier
        self.save_high_score() # Auto-save wallet
    
    def add_near_miss_bonus(self, bonus):
        """Add near miss bonus score"""
        self.near_misses += 1
        self.score += int(bonus * self.multiplier)
    
    def add_powerup_bonus(self):
        """Track powerup collection"""
        self.powerups_collected += 1
        self.score += 25  # Bonus for collecting powerup
    
    def add_mystery_box_bonus(self):
        """Track mystery box opening"""
        self.mystery_boxes_opened += 1
        self.score += 50  # Bonus for opening box
    
    def get_score(self):
        return self.score
    
    def get_coins(self):
        return self.coins
    
    def get_distance(self):
        return int(self.distance)
    
    def get_upgrades(self):
        return self.upgrades
        
    def upgrade_powerup(self, key):
        if key in self.upgrades:
            self.upgrades[key] += 1
            self.save_high_score() # Save progress
    
    def get_stats(self):
        """Get game stats for game over screen"""
        return {
            'score': self.score,
            'high_score': self.high_score,
            'coins': self.coins_collected,
            'distance': int(self.distance),
            'near_misses': self.near_misses,
            'powerups': self.powerups_collected,
            'mystery_boxes': self.mystery_boxes_opened
        }
    
    def check_high_score(self):
        """Check and update high score"""
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            return True
        return False
    
    def load_high_score(self):
        """Load high score and save data from file"""
        try:
            if os.path.exists(config.HIGH_SCORE_FILE):
                with open(config.HIGH_SCORE_FILE, 'r') as f:
                    data = json.load(f)
                    self.high_score = data.get('high_score', 0)
                    self.total_coins = data.get('total_coins', 0)
                    self.upgrades = data.get('upgrades', self.upgrades)
        except Exception:
            self.high_score = 0
            self.total_coins = 0
    
    def save_high_score(self):
        """Save high score and upgrades to file"""
        try:
            with open(config.HIGH_SCORE_FILE, 'w') as f:
                json.dump({
                    'high_score': self.high_score,
                    'total_coins': self.total_coins,
                    'upgrades': self.upgrades
                }, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def reset(self):
        """Reset for new game"""
        self.score = 0
        self.coins = 0
        self.distance = 0.0
        self.multiplier = 1
        self.coins_collected = 0
        self.near_misses = 0
        self.powerups_collected = 0
        self.mystery_boxes_opened = 0
