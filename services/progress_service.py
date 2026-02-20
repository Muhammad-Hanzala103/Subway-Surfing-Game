"""
Progress Service - Handles long-term persistence logic independently of running match
"""
from game.save_repository import SaveRepository
from services.run_service import RunSummary

class ProgressService:
    """Service to handle player progression and stats"""
    def __init__(self, save_repo: SaveRepository):
        self.save_repo = save_repo
        
    def process_run(self, score: int, coins: int, distance: int, near_misses: int, 
                    powerups: int, mystery_boxes: int) -> RunSummary:
        """Process end of run and save progress"""
        progress = self.save_repo.load_progress()
        profile = self.save_repo.load_profile()
        
        current_high = int(progress.get("high_score", 0))
        new_high_score = score > current_high
        
        if new_high_score:
            progress["high_score"] = score
            self.save_repo.save_progress(progress)
            
        profile["total_coins"] = profile.get("total_coins", 0) + coins
        self.save_repo.save_profile(profile)
        
        return RunSummary(
            score=score,
            high_score=max(score, current_high),
            coins_collected=coins,
            distance=distance,
            near_misses=near_misses,
            powerups_collected=powerups,
            mystery_boxes_opened=mystery_boxes,
            new_high_score=new_high_score
        )
