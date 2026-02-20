import pytest
from app.scene_controller import SceneController
from config import GameState

class DummyApp:
    def __init__(self):
        self.game = None

class DummyScene:
    def __init__(self):
        self.entered = False
        self.exited = False
        
    def enter(self):
        self.entered = True
        
    def exit(self):
        self.exited = True
        
    def update(self, dt, events, keys):
        pass
        
    def render(self):
        pass

def test_scene_registration():
    app = DummyApp()
    controller = SceneController(app)
    scene = DummyScene()
    
    controller.register(GameState.MENU, scene)
    assert GameState.MENU in controller.scenes
    assert controller.scenes[GameState.MENU] == scene

def test_scene_transition():
    app = DummyApp()
    controller = SceneController(app)
    
    scene1 = DummyScene()
    scene2 = DummyScene()
    
    controller.register(GameState.MENU, scene1)
    controller.register(GameState.PLAYING, scene2)
    
    # Needs a dummy game state property on app.game usually, 
    # but SceneController expects app.game.state
    class DummyGame:
        def __init__(self):
            self.state = GameState.MENU
            
    app.game = DummyGame()
    
    # First update should enter the scene
    controller.update(0.1, [], [])
    assert controller.current_state == GameState.MENU
    assert scene1.entered
    assert not scene1.exited
    
    # Change state and update should trigger transition
    app.game.state = GameState.PLAYING
    controller.update(0.1, [], [])
    
    assert scene1.exited
    assert scene2.entered
    assert controller.current_state == GameState.PLAYING
