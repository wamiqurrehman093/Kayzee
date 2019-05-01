import arcade
from player import Player, get_distance_between_sprites

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Kayzee"

CHARACTER_SCALING = 0.2
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

MOVEMENT_SPEED = 8
GRAVITY = 1
JUMP_SPEED = 20

LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
TOP_VIEWPORT_MARGIN = 100
BOTTOM_VIEWPORT_MARGIN = 150

PLAYER_START_X = 128
PLAYER_START_Y = 128


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.coin_list = None
        self.wall_list = None
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.player_list = None

        self.player = None
        self.physics_engine = None

        self.view_bottom = 0
        self.view_left = 0

        self.score = 0

        self.end_of_map = 0

        self.level = 1

        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.game_over = arcade.load_sound("sounds/gameover1.wav")

    def setup(self, level):
        self.view_bottom = 0
        self.view_left = 0

        self.score = 0

        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.dont_touch_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        # self.player_sprite = arcade.Sprite("images/player.png", CHARACTER_SCALING)
        # self.player_sprite.center_x = PLAYER_START_X
        # self.player_sprite.center_y = PLAYER_START_Y
        # self.player_list.append(self.player_sprite)

        self.player = Player()

        self.player.stand_right_textures = []
        self.player.stand_left_textures = []
        self.player.walk_right_textures = []
        self.player.walk_left_textures = []

        self.player.stand_right_textures.append(arcade.load_texture("images/player_3/stand/0.png",
                                                                    scale=CHARACTER_SCALING))
        self.player.stand_left_textures.append(arcade.load_texture("images/player_3/stand/0.png",
                                                                   scale=CHARACTER_SCALING, mirrored=True))
        for i in range(8):
            self.player.walk_right_textures.append(arcade.load_texture("images/player_3/walk/"+str(i)+".png",
                                                                       scale=CHARACTER_SCALING))
        for i in range(8):
            self.player.walk_left_textures.append(arcade.load_texture("images/player_3/walk/"+str(i)+".png",
                                                                      scale=CHARACTER_SCALING, mirrored=True))

        self.player.texture_change_distance = 30

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player.scale = 0.2
        self.player_list.append(self.player)

        platforms_layer_name = "Platforms"
        coins_layer_name = "Coins"
        foreground_layer_name = "Foreground"
        background_layer_name = "Background"
        dont_touch_layer_name = "Don't Touch"

        map_name = f"map2_level_{level}.tmx"
        my_map = arcade.read_tiled_map(map_name, TILE_SCALING)
        map_array = my_map.layers_int_data[platforms_layer_name]
        self.end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE

        self.background_list = arcade.generate_sprites(my_map, background_layer_name, TILE_SCALING)
        self.foreground_list = arcade.generate_sprites(my_map, foreground_layer_name, TILE_SCALING)
        self.wall_list = arcade.generate_sprites(my_map, platforms_layer_name, TILE_SCALING)
        self.wall_list = arcade.generate_sprites(my_map, platforms_layer_name, TILE_SCALING)
        self.coin_list = arcade.generate_sprites(my_map, coins_layer_name, TILE_SCALING)
        self.dont_touch_list = arcade.generate_sprites(my_map, dont_touch_layer_name, TILE_SCALING)

        self.end_of_map = (len(map_array[0])-1) * GRID_PIXEL_SIZE

        if my_map.backgroundcolor:
            arcade.set_background_color(my_map.backgroundcolor)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,
                                                             self.wall_list,
                                                             GRAVITY)

    def on_draw(self):
        arcade.start_render()
        self.wall_list.draw()
        self.background_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.dont_touch_list.draw()
        try:
            self.player_list.draw()
        except:
            pass
        self.foreground_list.draw()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left,
                         10 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.UP or symbol == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player.change_y = JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.player.change_x = -MOVEMENT_SPEED
        elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.player.change_x = MOVEMENT_SPEED

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT or symbol == arcade.key.A:
            self.player.change_x = 0
        elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
            self.player.change_x = 0

    def update(self, delta_time: float):
        self.physics_engine.update()
        self.player_list.update_animation()

        coin_hitlist = arcade.check_for_collision_with_list(self.player,
                                                            self.coin_list)
        for coin in coin_hitlist:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        changed_viewport = False

        if self.player.center_y < 100:
            self.player.center_x = PLAYER_START_X
            self.player.center_Y = PLAYER_START_Y

            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

            arcade.play_sound(self.game_over)

        if arcade.check_for_collision_with_list(self.player, self.dont_touch_list):
            self.player.center_x = PLAYER_START_X
            self.player.center_y = PLAYER_START_Y

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)

        if self.player.center_x >= self.end_of_map:
            print("Advance ****")
            self.level += 1
            self.setup(self.level)

            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            changed_viewport = True

        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            changed_viewport = True

        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary
            changed_viewport = True

        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom
            changed_viewport = True

        if changed_viewport:
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            arcade.set_viewport(self.view_left,
                                self.view_left + SCREEN_WIDTH,
                                self.view_bottom,
                                self.view_bottom + SCREEN_HEIGHT)


def main():
    window = MyGame()
    window.setup(window.level)
    arcade.run()


if __name__ == '__main__':
    main()
