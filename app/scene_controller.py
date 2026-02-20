"""Simple scene controller with explicit transition ownership."""

from config import GameState


class SceneController:
    def __init__(self, app):
        self.app = app
        self.current_scene = None
        self.scenes = {}

    def register(self, state: GameState, scene) -> None:
        self.scenes[state] = scene

    def sync(self) -> None:
        target = self.scenes.get(self.app.game.state)
        if target is self.current_scene:
            return
        if self.current_scene is not None:
            self.current_scene.exit()
        self.current_scene = target
        if self.current_scene is not None:
            self.current_scene.enter()

    def update(self, dt, events, keys) -> None:
        self.sync()
        if self.current_scene is not None:
            self.current_scene.update(dt, events, keys)

    def render(self) -> None:
        if self.current_scene is not None:
            self.current_scene.render()

