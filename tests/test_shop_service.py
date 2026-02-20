import pytest
from services.shop_service import ShopService

class DummyScoreManager:
    def __init__(self):
        self.total_coins = 500
        self.upgrades = {"jetpack_level": 1, "magnet_level": 2}
        
    def upgrade_powerup(self, key):
        if key in self.upgrades:
            self.upgrades[key] += 1
        else:
            self.upgrades[key] = 1

@pytest.fixture
def shop_service():
    score = DummyScoreManager()
    return ShopService(score)

def test_get_cost(shop_service):
    # Level 1 item
    cost = shop_service.get_cost("Jetpack")
    assert cost == 500  # Base logic: 500 * level
    
    # Level 2 item
    cost = shop_service.get_cost("Magnet")
    assert cost == 1000  # 500 * 2
    
def test_purchase_success(shop_service):
    # Initial coins = 500, jetpack level 1 cost = 500
    res = shop_service.purchase_upgrade("Jetpack")
    
    assert res == "purchased"
    assert shop_service.score.total_coins == 0
    assert shop_service.score.upgrades["jetpack_level"] == 2
    
def test_insufficient_funds(shop_service):
    # Initial coins = 500, magnet level 2 cost = 1000
    res = shop_service.purchase_upgrade("Magnet")
    
    assert res == "insufficient_funds"
    assert shop_service.score.total_coins == 500
    assert shop_service.score.upgrades["magnet_level"] == 2
    
def test_max_level(shop_service):
    shop_service.score.upgrades["jetpack_level"] = 5  # Max
    res = shop_service.purchase_upgrade("Jetpack")
    
    assert res == "maxed"
    assert shop_service.score.total_coins == 500
