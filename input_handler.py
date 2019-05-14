import arcade


class InputHandler:
    def __init__(self, button_a, button_s, button_left, button_right, trigger_stop_walking):
        self.buttonA = button_a
        self.buttonS = button_s
        self.buttonLEFT = button_left
        self.buttonRIGHT = button_right
        self.triggerSTOPWALKING = trigger_stop_walking

    def swap(self):
        temp_button = self.buttonA
        self.buttonA = self.buttonS
        self.buttonS = temp_button

    def handle_key_press(self, key):
        if key == arcade.key.A:
            return self.buttonA
        elif key == arcade.key.S:
            return self.buttonS
        elif key == arcade.key.LEFT:
            return self.buttonLEFT
        elif key == arcade.key.RIGHT:
            return self.buttonRIGHT
        elif key == arcade.key.T:
            self.swap()
        return None

    def handle_key_release(self, key):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            return self.triggerSTOPWALKING
