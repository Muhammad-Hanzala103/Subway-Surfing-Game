from config import GameState


class MenuScene:
    def __init__(self, app):
        self.app = app

    def enter(self):
        return None

    def exit(self):
        return None

    def update(self, dt, events, keys):
        self.app._handle_menu_state(events, dt)

    def render(self):
        if self.app.settings_menu.active:
            self.app.settings_menu.draw(self.app.menu.animation_time)
        elif self.app.char_select.active:
            self.app.char_select.draw(self.app.game.score.total_coins)
        else:
            self.app.menu.draw_main_menu()

