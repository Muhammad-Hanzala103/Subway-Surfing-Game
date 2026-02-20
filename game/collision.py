"""
Collision Detection System - Enhanced
Handles obstacles, coins, power-ups, mystery boxes, and near misses
"""

import numpy as np
import config


class CollisionManager:
    """Handles collision detection between game objects"""
    
    def __init__(self):
        self.near_miss_distance = 1.5  # Distance for near miss
    
    def check_aabb_overlap(self, bounds_a, bounds_b):
        """Check if two AABBs overlap"""
        return (
            bounds_a['min'][0] < bounds_b['max'][0] and
            bounds_a['max'][0] > bounds_b['min'][0] and
            bounds_a['min'][1] < bounds_b['max'][1] and
            bounds_a['max'][1] > bounds_b['min'][1] and
            bounds_a['min'][2] < bounds_b['max'][2] and
            bounds_a['max'][2] > bounds_b['min'][2]
        )
    
    def check_near_miss(self, player_bounds, obs_bounds):
        """Check if player narrowly avoided an obstacle"""
        # Expand player bounds slightly for near miss detection
        expanded_bounds = {
            'min': player_bounds['min'] - np.array([self.near_miss_distance, 0, 0]),
            'max': player_bounds['max'] + np.array([self.near_miss_distance, 0, 0])
        }
        
        # Check if obstacle is in near miss zone but not actually colliding
        if self.check_aabb_overlap(expanded_bounds, obs_bounds):
            if not self.check_aabb_overlap(player_bounds, obs_bounds):
                return True
        return False
    
    def check_player_obstacle_collision(self, player, obstacles):
        """Check player collision with obstacles"""
        player_bounds = player.get_bounds()
        near_misses = []
        
        for obs in obstacles:
            if not obs.active:
                continue
            
            obs_bounds = obs.get_bounds()
            
            # Skip if obstacle is behind player
            if obs_bounds['max'][2] < player_bounds['min'][2] - 2:
                continue
            
            if self.check_aabb_overlap(player_bounds, obs_bounds):
                return obs, near_misses
            
            # Check near miss
            if self.check_near_miss(player_bounds, obs_bounds):
                if obs not in near_misses:
                    near_misses.append(obs)
        
        return None, near_misses
    
    def check_player_coin_collision(self, player, coins):
        """Check player collision with coins"""
        collected = []
        player_bounds = player.get_bounds()
        player_center = (player_bounds['min'] + player_bounds['max']) / 2
        player_radius = config.PLAYER_WIDTH
        
        # Magnet effect - increased collection range
        collect_radius = player_radius
        if player.has_magnet:
            collect_radius = config.MAGNET_RANGE
        
        for coin in coins:
            if coin.collected:
                continue
            
            dist = np.linalg.norm(player_center[:2] - coin.position[:2])  # XY distance
            z_dist = abs(player_center[2] - coin.position[2])
            
            if dist < collect_radius and z_dist < 2.0:
                coin.collected = True
                collected.append(coin)
        
        return collected
    
    def check_player_powerup_collision(self, player, powerups):
        """Check player collision with power-ups"""
        collected = []
        player_bounds = player.get_bounds()
        player_center = (player_bounds['min'] + player_bounds['max']) / 2
        
        for powerup in powerups:
            if powerup.collected:
                continue
            
            dist = np.linalg.norm(player_center - powerup.position)
            
            if dist < config.PLAYER_WIDTH + powerup.size:
                powerup.collected = True
                collected.append(powerup)
        
        return collected
    
    def check_player_mystery_box_collision(self, player, mystery_boxes):
        """Check player collision with mystery boxes"""
        collected = []
        player_bounds = player.get_bounds()
        player_center = (player_bounds['min'] + player_bounds['max']) / 2
        
        for box in mystery_boxes:
            if box.collected:
                continue
            
            dist = np.linalg.norm(player_center - box.position)
            
            if dist < config.PLAYER_WIDTH + 0.8:
                box.collected = True
                collected.append(box)
        
        return collected
    
    def update(self, player, obstacles, coins, powerups, mystery_boxes=None):
        """Run all collision checks"""
        results = {
            'obstacle_hit': None,
            'coins_collected': [],
            'powerups_collected': [],
            'mystery_boxes_collected': [],
            'near_misses': []
        }
        
        # Obstacle collision
        hit_obstacle, near_misses = self.check_player_obstacle_collision(player, obstacles)
        if hit_obstacle:
            results['obstacle_hit'] = hit_obstacle
        results['near_misses'] = near_misses
        
        # Coin collection
        results['coins_collected'] = self.check_player_coin_collision(player, coins)
        
        # Power-up collection
        results['powerups_collected'] = self.check_player_powerup_collision(player, powerups)
        
        # Mystery box collection
        if mystery_boxes:
            results['mystery_boxes_collected'] = self.check_player_mystery_box_collision(player, mystery_boxes)
        
        return results
