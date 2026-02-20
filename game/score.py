"""
Score System - Enhanced with combos and near miss
"""

import json
import os
import config
from core.logging import get_logger
from .save_repository import SaveRepository

log = get_logger(__name__)


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
        
        self.save_repo = SaveRepository()
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
        self.high_score = 0
        self.total_coins = 0
        try:
            progress = self.save_repo.load_progress()
            profile = self.save_repo.load_profile()
            self.high_score = int(progress.get("high_score", 0))
            self.total_coins = int(profile.get("total_coins", 0))
            self.upgrades = progress.get("upgrades", self.upgrades)
        except (OSError, ValueError, TypeError) as exc:
            log.warning("Failed to load score data: %s", exc)
    
    def save_high_score(self):
        """Save high score and upgrades to file"""
        try:
            progress = self.save_repo.load_progress()
            profile = self.save_repo.load_profile()
            progress["high_score"] = self.high_score
            progress["upgrades"] = self.upgrades
            profile["total_coins"] = self.total_coins
            self.save_repo.save_progress(progress)
            self.save_repo.save_profile(profile)

            # Backward compatible adapter for legacy readers.
            with open(config.HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "high_score": self.high_score,
                        "total_coins": self.total_coins,
                        "upgrades": self.upgrades,
                    },
                    f,
                )
        except (OSError, ValueError, TypeError) as exc:
            log.error("Error saving score data: %s", exc)
    
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
