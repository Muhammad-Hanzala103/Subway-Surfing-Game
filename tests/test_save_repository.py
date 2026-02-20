import pytest
import os
import json
import tempfile
from game.save_repository import SaveRepository

@pytest.fixture
def temp_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        repo = SaveRepository(base_path=temp_dir)
        yield repo, temp_dir

def test_save_and_load_profile(temp_repo):
    repo, temp_dir = temp_repo
    profile_data = {"test_key": "test_value"}
    repo.save_profile(profile_data)
    
    loaded = repo.load_profile()
    assert loaded["test_key"] == "test_value"
    assert loaded["version"] == repo.SCHEMA_VERSION

def test_migration_from_legacy(temp_repo):
    repo, temp_dir = temp_repo
    
    # Create legacy file
    legacy_path = os.path.join(temp_dir, "highscore.json")
    with open(legacy_path, "w") as f:
        json.dump({"high_score": 12345, "total_coins": 500, "jetpack_level": 2}, f)
        
    # Loading should trigger migration
    progress = repo.load_progress()
    profile = repo.load_profile()
    
    assert progress["high_score"] == 12345
    assert profile["total_coins"] == 500
    assert progress["upgrades"]["jetpack_level"] == 2
    
    # Legacy file should be backed up
    assert os.path.exists(legacy_path + ".bak")

def test_corrupted_file_recovery(temp_repo):
    repo, temp_dir = temp_repo
    
    # Save valid
    repo.save_profile({"valid": True})
    
    # Corrupt the file
    path = repo._path(repo.PROFILE_FILE)
    with open(path, "w") as f:
        f.write("{invalid json format...")
        
    # Loading should recover from backup or return default
    loaded = repo.load_profile()
    assert isinstance(loaded, dict)
    assert loaded.get("version") == repo.SCHEMA_VERSION
