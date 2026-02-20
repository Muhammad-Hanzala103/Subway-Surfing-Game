class GameOverScene:
    def __init__(self, app):
        self.app = app

    def enter(self):
        return None

    def exit(self):
        return None

    def update(self, dt, events, keys):
        self.app._handle_game_over_state(events, dt)

    def render(self):
        self.app.game.draw()
        if self.app.settings.get("particles_enabled"):
            self.app.particles.draw()
        self.app.menu.draw_game_over(self.app.game)

