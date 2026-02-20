"""Progress service to centralize reward and coin persistence."""

from dataclasses import dataclass


@dataclass
class RunSummary:
    coins: int
    distance: int
    near_misses: int
    powerups: int
    max_combo: int


class ProgressService:
    def __init__(self, score_manager, achievements, challenges):
        self.score = score_manager
        self.achievements = achievements
        self.challenges = challenges

    def get_wallet_balance(self):
        return int(self.score.total_coins)

    def award_run_rewards(self, run_summary: RunSummary):
        self.score.total_coins += int(run_summary.coins)
        self.achievements.update_stats(
            total_coins=run_summary.coins,
            total_distance=run_summary.distance,
            max_combo=run_summary.max_combo,
            total_near_miss=run_summary.near_misses,
            total_powerups=run_summary.powerups,
        )
        reward = self.challenges.claim_all_rewards()
        if reward > 0:
            self.score.total_coins += reward
        self.score.save_high_score()
        return reward

