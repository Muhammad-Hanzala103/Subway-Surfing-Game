"""Save repository with schema versioning, migration and atomic writes."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from typing import Any

from core.logging import get_logger

log = get_logger(__name__)


class SaveRepository:
    SCHEMA_VERSION = 1
    PLAYER_PROFILE_FILE = "player_profile.json"
    PROGRESS_FILE = "progress.json"

    LEGACY_HIGH_SCORE_FILE = "highscore.json"
    LEGACY_PLAYER_DATA_FILE = "player_data.json"
    LEGACY_SETTINGS_FILE = "settings.json"

    def __init__(self, root_dir: str = ".") -> None:
        self.root_dir = root_dir

    def _path(self, filename: str) -> str:
        return os.path.join(self.root_dir, filename)

    def _safe_read_json(self, filename: str, default: dict[str, Any]) -> dict[str, Any]:
        path = self._path(filename)
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (OSError, json.JSONDecodeError) as exc:
            backup = f"{path}.corrupt.bak"
            try:
                shutil.copy2(path, backup)
            except OSError:
                pass
            log.warning("Corrupt JSON in %s: %s", filename, exc)
        return default

    def _atomic_write_json(self, filename: str, data: dict[str, Any]) -> None:
        path = self._path(filename)
        directory = os.path.dirname(path) or "."
        os.makedirs(directory, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(prefix=".tmp-save-", suffix=".json", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                json.dump(data, tmp, indent=2)
            os.replace(temp_path, path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _default_profile(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "total_coins": 0,
            "unlocked_characters": [],
            "settings_file": self.LEGACY_SETTINGS_FILE,
        }

    def _default_progress(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "high_score": 0,
            "upgrades": {
                "jetpack_level": 1,
                "magnet_level": 1,
                "sneakers_level": 1,
                "multiplier_level": 1,
            },
            "achievements": {"unlocked": [], "stats": {}},
            "daily_challenges": {"missions": [], "last_refresh": None, "total_completed": 0},
        }

    def ensure_migrated(self) -> None:
        profile_path = self._path(self.PLAYER_PROFILE_FILE)
        progress_path = self._path(self.PROGRESS_FILE)
        if os.path.exists(profile_path) and os.path.exists(progress_path):
            return

        profile = self._default_profile()
        progress = self._default_progress()

        legacy_high = self._safe_read_json(self.LEGACY_HIGH_SCORE_FILE, {})
        legacy_player = self._safe_read_json(self.LEGACY_PLAYER_DATA_FILE, {})
        legacy_ach = self._safe_read_json("achievements.json", {})
        legacy_daily = self._safe_read_json("daily_challenges.json", {})

        profile["total_coins"] = int(
            legacy_high.get("total_coins", legacy_player.get("total_coins", 0))
        )
        progress["high_score"] = int(legacy_high.get("high_score", 0))
        progress["upgrades"] = legacy_high.get("upgrades", progress["upgrades"])
        progress["achievements"] = {
            "unlocked": legacy_ach.get("unlocked", []),
            "stats": legacy_ach.get("stats", {}),
        }
        progress["daily_challenges"] = {
            "missions": legacy_daily.get("missions", []),
            "last_refresh": legacy_daily.get("last_refresh"),
            "total_completed": legacy_daily.get("total_completed", 0),
        }

        self.save_profile(profile)
        self.save_progress(progress)

    def load_profile(self) -> dict[str, Any]:
        self.ensure_migrated()
        return self._safe_read_json(self.PLAYER_PROFILE_FILE, self._default_profile())

    def save_profile(self, profile: dict[str, Any]) -> None:
        data = self._default_profile()
        data.update(profile)
        data["schema_version"] = self.SCHEMA_VERSION
        self._atomic_write_json(self.PLAYER_PROFILE_FILE, data)

    def load_progress(self) -> dict[str, Any]:
        self.ensure_migrated()
        return self._safe_read_json(self.PROGRESS_FILE, self._default_progress())

    def save_progress(self, progress: dict[str, Any]) -> None:
        data = self._default_progress()
        data.update(progress)
        data["schema_version"] = self.SCHEMA_VERSION
        self._atomic_write_json(self.PROGRESS_FILE, data)

