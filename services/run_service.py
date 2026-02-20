"""
Run Service - End of run data transfer logic
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class RunSummary:
    """DTO for end of run stats"""
    score: int
    high_score: int
    coins_collected: int
    distance: int
    near_misses: int
    powerups_collected: int
    mystery_boxes_opened: int
    new_high_score: bool

    def to_dict(self) -> Dict:
        return {
            'score': self.score,
            'high_score': self.high_score,
            'coins': self.coins_collected,
            'distance': self.distance,
            'near_misses': self.near_misses,
            'powerups': self.powerups_collected,
            'mystery_boxes': self.mystery_boxes_opened,
            'new_high_score': self.new_high_score
        }
