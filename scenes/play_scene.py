class PlayScene:
    def __init__(self, app):
        self.app = app

    def enter(self):
        return None

    def exit(self):
        return None

    def update(self, dt, events, keys):
        self.app._handle_playing_state(events, keys, dt)

    def render(self):
        self.app.game.draw()
        if self.app.settings.get("particles_enabled"):
            self.app.particles.draw()
        self.app.hud.draw(self.app.game)
        if self.app.settings.get("show_fps"):
            self.app.hud.draw_fps(self.app.window.fps)
        if self.app.tutorial.active:
            self.app.tutorial.draw(self.app.menu.animation_time)

