"""
Shop Service - Decouples purchase logic from UI
"""

class ShopService:
    BASE_COSTS = {
        "Jetpack": 500,
        "Magnet": 500,
        "Sneakers": 500,
        "Multiplier": 2000
    }
    
    def __init__(self, score_manager):
        self.score = score_manager

    def get_upgrade_levels(self) -> dict:
        return self.score.get_upgrades()

    def get_wallet_balance(self) -> int:
        return self.score.total_coins

    def get_cost(self, item: str) -> int:
        upgrades = self.get_upgrade_levels()
        level_key = item.lower() + "_level"
        current_level = upgrades.get(level_key, 1)
        if current_level >= 6:
            return -1 # Maxed
        return self.BASE_COSTS.get(item, 0) * current_level

    def purchase_upgrade(self, item: str) -> str:
        cost = self.get_cost(item)
        
        if cost == -1:
            return "maxed"
            
        if self.score.total_coins >= cost:
            self.score.total_coins -= cost
            level_key = item.lower() + "_level"
            self.score.upgrade_powerup(level_key)
            return "purchased"
            
        return "insufficient_funds"
