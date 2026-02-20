import os
import pytest

# Force headless mode for Pygame tests to avoid opening a real window or audio device
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

def test_imports():
    """Verify that all core modules can be imported without syntax errors."""
    try:
        import config
        import main
        import engine
        import game
        import ui
        assert config is not None
        assert main is not None
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")

def test_config_sanity():
    """Verify that critical constants are logically correct."""
    import config
    assert config.WINDOW_WIDTH > 0
    assert config.WINDOW_HEIGHT > 0
    assert hasattr(config, "GameState")
