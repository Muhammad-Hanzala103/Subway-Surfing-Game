class ShopScene:
    def __init__(self, app):
        self.app = app

    def enter(self):
        return None

    def exit(self):
        return None

    def update(self, dt, events, keys):
        self.app._handle_shop_state(events, dt)

    def render(self):
        self.app.menu.draw_shop()

