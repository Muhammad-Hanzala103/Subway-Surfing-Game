class PauseScene:
    def __init__(self, app):
        self.app = app

    def enter(self):
        return None

    def exit(self):
        return None

    def update(self, dt, events, keys):
        self.app._handle_paused_state(events, dt)

    def render(self):
        self.app.game.draw()
        self.app.hud.draw(self.app.game)
        self.app.menu.draw_pause_menu()

