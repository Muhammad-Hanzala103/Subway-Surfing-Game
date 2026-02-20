"""Shop service abstraction."""


class ShopService:
    BASE_COSTS = {
        "jetpack_level": 500,
        "magnet_level": 500,
        "sneakers_level": 500,
        "multiplier_level": 2000,
    }
    MAX_LEVEL = 6

    def __init__(self, score_manager):
        self.score = score_manager

    def get_upgrade_levels(self):
        return dict(self.score.get_upgrades())

    def get_wallet_balance(self):
        return int(self.score.total_coins)

    def purchase_upgrade(self, upgrade_id):
        levels = self.score.get_upgrades()
        level = int(levels.get(upgrade_id, 1))
        if level >= self.MAX_LEVEL:
            return False, "maxed"
        cost = self.BASE_COSTS.get(upgrade_id, 0) * level
        if self.score.total_coins < cost:
            return False, "insufficient_funds"
        self.score.total_coins -= cost
        self.score.upgrade_powerup(upgrade_id)
        self.score.save_high_score()
        return True, "purchased"

