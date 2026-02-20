"""
Daily Challenges / Mission System
"""

import random
from datetime import date
from enum import Enum


class MissionType(Enum):
    COLLECT_COINS = "collect_coins"
    TRAVEL_DISTANCE = "travel_distance"
    JUMP_COUNT = "jump_count"
    SLIDE_COUNT = "slide_count"
    NO_COINS = "no_coins"
    POWER_UP_COUNT = "power_up_count"
    NEAR_MISS_COUNT = "near_miss"
    SCORE_TARGET = "score_target"
    COMBO_TARGET = "combo_target"


class Mission:
    """Single mission/challenge"""
    
    MISSION_TEMPLATES = [
        {'type': MissionType.COLLECT_COINS, 'targets': [50, 100, 200, 500], 'reward_mult': 2},
        {'type': MissionType.TRAVEL_DISTANCE, 'targets': [500, 1000, 2000, 5000], 'reward_mult': 1},
        {'type': MissionType.JUMP_COUNT, 'targets': [10, 25, 50, 100], 'reward_mult': 3},
        {'type': MissionType.SLIDE_COUNT, 'targets': [10, 20, 40, 80], 'reward_mult': 3},
        {'type': MissionType.POWER_UP_COUNT, 'targets': [3, 5, 10, 20], 'reward_mult': 5},
        {'type': MissionType.NEAR_MISS_COUNT, 'targets': [5, 10, 20, 50], 'reward_mult': 10},
        {'type': MissionType.SCORE_TARGET, 'targets': [5000, 10000, 25000, 50000], 'reward_mult': 1},
        {'type': MissionType.COMBO_TARGET, 'targets': [10, 20, 30, 50], 'reward_mult': 5},
    ]
    
    def __init__(self, mission_type, target, difficulty=1):
        self.type = mission_type
        self.target = target
        self.difficulty = difficulty
        self.progress = 0
        self.completed = False
        self.reward_claimed = False
        self.reward = int(target * self._get_reward_mult() * difficulty)
    
    def _get_reward_mult(self):
        for template in self.MISSION_TEMPLATES:
            if template['type'] == self.type:
                return template['reward_mult']
        return 1
    
    def get_description(self):
        descriptions = {
            MissionType.COLLECT_COINS: f"Collect {self.target} coins",
            MissionType.TRAVEL_DISTANCE: f"Travel {self.target}m in a single run",
            MissionType.JUMP_COUNT: f"Jump {self.target} times",
            MissionType.SLIDE_COUNT: f"Slide {self.target} times",
            MissionType.POWER_UP_COUNT: f"Collect {self.target} power-ups",
            MissionType.NEAR_MISS_COUNT: f"Get {self.target} near misses",
            MissionType.SCORE_TARGET: f"Score {self.target:,} points",
            MissionType.COMBO_TARGET: f"Reach a {self.target}x combo",
        }
        return descriptions.get(self.type, "Complete challenge")
    
    def update_progress(self, amount):
        if not self.completed:
            self.progress = min(self.progress + amount, self.target)
            if self.progress >= self.target:
                self.completed = True
    
    def set_progress(self, amount):
        """Set absolute progress (for score/combo targets)"""
        if not self.completed:
            self.progress = min(amount, self.target)
            if self.progress >= self.target:
                self.completed = True
    
    def get_progress_percent(self):
        return min(1.0, self.progress / self.target)
    
    def claim_reward(self):
        if self.completed and not self.reward_claimed:
            self.reward_claimed = True
            return self.reward
        return 0
    
    def to_dict(self):
        return {
            'type': self.type.value,
            'target': self.target,
            'difficulty': self.difficulty,
            'progress': self.progress,
            'completed': self.completed,
            'reward_claimed': self.reward_claimed,
            'reward': self.reward
        }
    
    @classmethod
    def from_dict(cls, data):
        mission = cls(
            MissionType(data['type']),
            data['target'],
            data.get('difficulty', 1)
        )
        mission.progress = data.get('progress', 0)
        mission.completed = data.get('completed', False)
        mission.reward_claimed = data.get('reward_claimed', False)
        mission.reward = data.get('reward', mission.reward)
        return mission


class DailyChallenges:
    """Manages daily challenges"""
    
    SAVE_FILE = "daily_challenges.json"
    
    def __init__(self):
        self.missions = []
        self.last_refresh_date = None
        self.total_completed = 0
        self.load()
        self.check_refresh()
    
    def check_refresh(self):
        """Check if daily challenges need refresh"""
        today = date.today().isoformat()
        
        if self.last_refresh_date != today:
            self.refresh_missions()
            self.last_refresh_date = today
            self.save()
    
    def refresh_missions(self):
        """Generate new daily missions"""
        self.missions = []
        
        # Generate 3 daily missions with varying difficulty
        used_types = []
        
        for i, difficulty in enumerate([1, 2, 3]):
            available = [t for t in Mission.MISSION_TEMPLATES 
                        if t['type'] not in used_types]
            
            if available:
                template = random.choice(available)
                used_types.append(template['type'])
                
                # Pick target based on difficulty
                target_idx = min(difficulty, len(template['targets']) - 1)
                target = template['targets'][target_idx]
                
                mission = Mission(template['type'], target, difficulty)
                self.missions.append(mission)
    
    def update_mission_progress(self, mission_type, amount, absolute=False):
        """Update progress for missions of given type"""
        for mission in self.missions:
            if mission.type == mission_type:
                if absolute:
                    mission.set_progress(amount)
                else:
                    mission.update_progress(amount)
        self.save()
    
    def get_active_missions(self):
        """Get list of uncompleted missions"""
        return [m for m in self.missions if not m.completed]
    
    def get_claimable_rewards(self):
        """Get missions with unclaimed rewards"""
        return [m for m in self.missions if m.completed and not m.reward_claimed]
    
    def claim_all_rewards(self):
        """Claim all available rewards"""
        total = 0
        for mission in self.missions:
            reward = mission.claim_reward()
            total += reward
            if reward > 0:
                self.total_completed += 1
        self.save()
        return total
    
    def get_mission_list(self):
        """Get all missions with their info"""
        return [{
            'description': m.get_description(),
            'progress': m.progress,
            'target': m.target,
            'percent': m.get_progress_percent(),
            'completed': m.completed,
            'claimed': m.reward_claimed,
            'reward': m.reward,
            'difficulty': m.difficulty
        } for m in self.missions]
    
    def save(self):
        """Save to file"""
        from game.save_repository import SaveRepository
        try:
            repo = SaveRepository()
            progress = repo.load_progress()
            progress["daily_challenges"] = {
                'last_refresh': self.last_refresh_date,
                'total_completed': self.total_completed,
                'missions': [m.to_dict() for m in self.missions]
            }
            repo.save_progress(progress)
        except Exception as e:
            print(f"Error saving challenges: {e}")
    
    def load(self):
        """Load from file"""
        from game.save_repository import SaveRepository
        try:
            repo = SaveRepository()
            progress = repo.load_progress()
            data = progress.get("daily_challenges", {})
            self.last_refresh_date = data.get('last_refresh')
            self.total_completed = data.get('total_completed', 0)
            self.missions = [Mission.from_dict(m) for m in data.get('missions', [])]
        except Exception as e:
            print(f"Error loading challenges: {e}")
            self.missions = []


class Achievements:
    """Achievement/badge system"""
    
    SAVE_FILE = "achievements.json"
    
    ACHIEVEMENTS = [
        {'id': 'first_run', 'name': 'First Steps', 'description': 'Complete your first run', 'icon': '🏃'},
        {'id': 'distance_100', 'name': 'Sprinter', 'description': 'Travel 100m in one run', 'icon': '🏃'},
        {'id': 'distance_500', 'name': 'Marathon', 'description': 'Travel 500m in one run', 'icon': '🏅'},
        {'id': 'distance_1000', 'name': 'Ultra Runner', 'description': 'Travel 1000m in one run', 'icon': '🏆'},
        {'id': 'coins_100', 'name': 'Coin Collector', 'description': 'Collect 100 coins total', 'icon': '🪙'},
        {'id': 'coins_1000', 'name': 'Rich Runner', 'description': 'Collect 1000 coins total', 'icon': '💰'},
        {'id': 'combo_10', 'name': 'Combo Starter', 'description': 'Reach 10x combo', 'icon': '⚡'},
        {'id': 'combo_30', 'name': 'Combo Master', 'description': 'Reach 30x combo', 'icon': '🔥'},
        {'id': 'near_miss_10', 'name': 'Close Call', 'description': 'Get 10 near misses total', 'icon': '😅'},
        {'id': 'powerups_20', 'name': 'Power Player', 'description': 'Collect 20 power-ups total', 'icon': '⭐'},
        {'id': 'unlock_char', 'name': 'New Friend', 'description': 'Unlock a new character', 'icon': '👤'},
        {'id': 'score_10000', 'name': 'High Scorer', 'description': 'Score 10,000 points', 'icon': '📊'},
        {'id': 'score_50000', 'name': 'Score Legend', 'description': 'Score 50,000 points', 'icon': '🌟'},
        {'id': 'missions_10', 'name': 'Mission Possible', 'description': 'Complete 10 daily missions', 'icon': '📋'},
        {'id': 'play_10', 'name': 'Dedicated', 'description': 'Play 10 games', 'icon': '🎮'},
    ]
    
    def __init__(self):
        self.unlocked = set()
        self.stats = {
            'total_coins': 0,
            'total_distance': 0,
            'total_games': 0,
            'max_combo': 0,
            'total_near_miss': 0,
            'total_powerups': 0,
            'missions_completed': 0
        }
        self.load()
    
    def check_achievement(self, achievement_id):
        """Check if achievement should be unlocked"""
        if achievement_id in self.unlocked:
            return False
        
        checks = {
            'first_run': lambda: self.stats['total_games'] >= 1,
            'distance_100': lambda: self.stats['total_distance'] >= 100,
            'distance_500': lambda: self.stats['total_distance'] >= 500,
            'distance_1000': lambda: self.stats['total_distance'] >= 1000,
            'coins_100': lambda: self.stats['total_coins'] >= 100,
            'coins_1000': lambda: self.stats['total_coins'] >= 1000,
            'combo_10': lambda: self.stats['max_combo'] >= 10,
            'combo_30': lambda: self.stats['max_combo'] >= 30,
            'near_miss_10': lambda: self.stats['total_near_miss'] >= 10,
            'powerups_20': lambda: self.stats['total_powerups'] >= 20,
            'score_10000': lambda: True,  # Checked externally
            'score_50000': lambda: True,
            'missions_10': lambda: self.stats['missions_completed'] >= 10,
            'play_10': lambda: self.stats['total_games'] >= 10,
        }
        
        if achievement_id in checks and checks[achievement_id]():
            self.unlocked.add(achievement_id)
            self.save()
            return True
        return False
    
    def check_all(self):
        """Check all achievements and return newly unlocked"""
        newly_unlocked = []
        for ach in self.ACHIEVEMENTS:
            if self.check_achievement(ach['id']):
                newly_unlocked.append(ach)
        return newly_unlocked
    
    def update_stats(self, **kwargs):
        """Update stats"""
        for key, value in kwargs.items():
            if key in self.stats:
                if key == 'max_combo':
                    self.stats[key] = max(self.stats[key], value)
                else:
                    self.stats[key] += value
        self.save()
    
    def get_achievement_list(self):
        """Get all achievements with unlock status"""
        return [{
            **ach,
            'unlocked': ach['id'] in self.unlocked
        } for ach in self.ACHIEVEMENTS]
    
    def get_progress(self):
        """Get overall progress"""
        return len(self.unlocked) / len(self.ACHIEVEMENTS)
    
    def save(self):
        from game.save_repository import SaveRepository
        try:
            repo = SaveRepository()
            progress = repo.load_progress()
            progress["achievements"] = {
                'unlocked': list(self.unlocked),
                'stats': self.stats
            }
            repo.save_progress(progress)
        except Exception as e:
            print(f"Error saving achievements: {e}")
    
    def load(self):
        from game.save_repository import SaveRepository
        try:
            repo = SaveRepository()
            progress = repo.load_progress()
            data = progress.get("achievements", {})
            self.unlocked = set(data.get('unlocked', []))
            self.stats.update(data.get('stats', {}))
        except Exception as e:
            print(f"Error loading achievements: {e}")
