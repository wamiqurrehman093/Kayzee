import os
import arcade
from player import Player, get_distance_between_sprites
from enemy import Enemy
from input_handler import *
from commands import *
from variables import *
import random
import timeit


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_file_path()
        self.init_lists_player()
        self.init_game_mechanics()
        self.init_sounds()
        self.init_handlers()
        self.init_commands()
        self.background = None
        self.font_color = None
        self.bg_music = None
        self.prev_music = None
        self.bg_music_length = None
        self.total_time = 0.0

    def set_file_path(self):
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

    def init_lists_player(self):
        self.coin_list = None
        self.wall_list = None
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.player_list = None
        self.bullet_list = None
        self.enemy_list = None
        self.flag_list = None
        self.player = None

    def init_game_mechanics(self):
        self.physics_engine = None
        self.view_bottom = 0
        self.view_left = 0
        self.score = 0
        self.end_of_map = 0
        self.level = 1
        self.processing_time = 0
        self.draw_time = 0
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None

    def init_sounds(self):
        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.game_over = arcade.load_sound("sounds/gameover1.wav")
        self.gun_sound = arcade.sound.load_sound("sounds/laser1.wav")
        self.hit_sound = arcade.sound.load_sound("sounds/laser4.wav")

    def init_handlers(self):
        self.input_handler = None

    def init_commands(self):
        self.jump_command = None
        self.shoot_command = None
        self.walk_left_command = None
        self.walk_right_command = None
        self.stop_walking_command = None

    def setup(self, level):
        self.setup_game_mechanics()
        my_map = self.read_map(level)
        self.setup_lists(my_map)
        self.setup_enemies(my_map)
        self.setup_player()
        self.setup_commands()
        self.setup_handler()
        self.font_color = arcade.color.WHITE
        if self.level == 1 or self.level == 3 or self.level == 6:
            self.font_color = arcade.color.BLACK
        self.prev_music = self.bg_music
        self.bg_music = arcade.load_sound(f"music/music_{self.level}.mp3")
        if self.prev_music is not None:
            if not arcade.is_queued(self.prev_music):
                arcade.play_sound(self.bg_music)
        else:
            arcade.play_sound(self.bg_music)
        if self.level == 1:
            self.bg_music_length = 34
        elif self.level == 2:
            self.bg_music_length = 32
        elif self.level == 3:
            self.bg_music_length = 53
        elif self.level == 4:
            self.bg_music_length = 39
        elif self.level == 5:
            self.bg_music_length = 27
        elif self.level == 6:
            self.bg_music_length = 42
        self.total_time = 0.0
        self.background = arcade.load_texture(f"images/backgrounds/BG_{self.level}.png")

    def setup_game_mechanics(self):
        self.view_bottom = 0
        self.view_left = 0
        self.score = 0

    def setup_commands(self):
        self.jump_command = JumpCommand()
        self.shoot_command = ShootCommand()
        self.walk_left_command = WalkLeftCommand()
        self.walk_right_command = WalkRightCommand()
        self.stop_walking_command = StopWalkingCommand()

    def setup_handler(self):
        self.input_handler = InputHandler(self.shoot_command, self.jump_command, self.walk_left_command,
                                          self.walk_right_command, self.stop_walking_command)

    def setup_player(self):
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

        self.player.texture_change_distance = 25
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.player.scale = CHARACTER_SCALING
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,
                                                             self.wall_list,
                                                             GRAVITY)
        self.player.physics_engine = self.physics_engine
        self.player_list.append(self.player)

    def setup_lists(self, my_map):
        self.assign_lists()
        self.generate_lists(my_map)
        if my_map.backgroundcolor:
            arcade.set_background_color(my_map.backgroundcolor)

    def assign_lists(self):
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.dont_touch_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.flag_list = arcade.SpriteList()

    def generate_lists(self, my_map):
        platforms_layer_name = "Platforms"
        coins_layer_name = "Coins"
        foreground_layer_name = "Foreground"
        background_layer_name = "Background"
        dont_touch_layer_name = "Don't Touch"
        flag_layer_name = "Flags"

        self.background_list = arcade.generate_sprites(my_map, background_layer_name, TILE_SCALING)
        self.foreground_list = arcade.generate_sprites(my_map, foreground_layer_name, TILE_SCALING)
        self.wall_list = arcade.generate_sprites(my_map, platforms_layer_name, TILE_SCALING)
        #self.wall_list = arcade.generate_sprites(my_map, platforms_layer_name, TILE_SCALING)
        self.coin_list = arcade.generate_sprites(my_map, coins_layer_name, TILE_SCALING)
        self.dont_touch_list = arcade.generate_sprites(my_map, dont_touch_layer_name, TILE_SCALING)
        self.flag_list = arcade.generate_sprites(my_map, flag_layer_name, TILE_SCALING)

    def read_map(self, level):
        platforms_layer_name = "Platforms"
        map_name = f"map2_level_{level}.tmx"
        my_map = arcade.read_tiled_map(map_name, TILE_SCALING)
        map_array = my_map.layers_int_data[platforms_layer_name]
        self.end_of_map = (len(map_array[0])-1) * GRID_PIXEL_SIZE
        return my_map


    def setup_enemies(self, my_map):
        enemy_layer_name = "Enemies"
        e_list = arcade.generate_sprites(my_map, enemy_layer_name, ENEMY_SCALE)
        for e in e_list:
            enemy = Enemy()

            enemy.stand_right_textures = []
            enemy.stand_left_textures = []
            enemy.walk_right_textures = []
            enemy.walk_left_textures = []

            enemy.stand_right_textures.append(arcade.load_texture("images/zombies/stand/0.png",
                                                                  scale=ENEMY_SCALE))
            enemy.stand_left_textures.append(arcade.load_texture("images/zombies/stand/0.png",
                                                                 scale=ENEMY_SCALE, mirrored=True))
            for i in range(10):
                enemy.walk_right_textures.append(
                    arcade.load_texture("images/zombies/walk/" + str(i) + ".png",
                                        scale=ENEMY_SCALE))
            for i in range(10):
                enemy.walk_left_textures.append(arcade.load_texture("images/zombies/walk/" + str(i) + ".png",
                                                                    scale=ENEMY_SCALE, mirrored=True))

            enemy.texture_change_distance = 20

            enemy.center_x = e.center_x
            enemy.center_y = e.center_y + 64
            enemy.scale = ENEMY_SCALE
            enemy.change_x = -ENEMY_SPEED
            self.enemy_list.append(enemy)

    def on_draw(self):
        # Start timing how long this takes
        draw_start_time = timeit.default_timer()
        self.calculate_fps()
        arcade.start_render()
        arcade.draw_texture_rectangle((SCREEN_WIDTH // 2) + self.view_left, (SCREEN_HEIGHT // 2) + self.view_bottom,
                                      SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        self.background_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.dont_touch_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        try:
            self.player_list.draw()
        except:
            pass
        self.foreground_list.draw()
        self.draw_hud(draw_start_time)


    def calculate_fps(self):
        if self.frame_count % 60 == 0:
            if self.fps_start_timer is not None:
                total_time = timeit.default_timer() - self.fps_start_timer
                self.fps = 60 / total_time
            self.fps_start_timer = timeit.default_timer()
        self.frame_count += 1

    def draw_bottom_hud(self):
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left,
                         10 + self.view_bottom,
                         self.font_color, 18)
        level_text = f"Level: {self.level}"
        arcade.draw_text(level_text, 150 + self.view_left,
                         10 + self.view_bottom,
                         self.font_color, 18)

    def draw_top_hud(self, draw_start_time):
        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 10 + self.view_left, self.view_bottom + (SCREEN_HEIGHT-20),
                        self.font_color, 16)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 10 + self.view_left, self.view_bottom + (SCREEN_HEIGHT-40), self.font_color, 16)

        if self.fps is not None:
            output = f"FPS: {self.fps:.0f}"
            arcade.draw_text(output, 10 + self.view_left, self.view_bottom + (SCREEN_HEIGHT-60), self.font_color, 16)

        self.draw_time = timeit.default_timer() - draw_start_time

    def draw_hud(self, draw_start_time):
        self.draw_bottom_hud()
        self.draw_top_hud(draw_start_time)

    def on_key_press(self, symbol: int, modifiers: int):
        command = self.input_handler.handle_key_press(symbol)
        if command:
            command.execute(self.player)

    def on_key_release(self, symbol: int, modifiers: int):
        command = self.input_handler.handle_key_release(symbol)
        if command:
            command.execute(self.player)

    def update(self, delta_time: float):
        # self.total_time += delta_time
        # seconds = int(self.total_time) % 60
        # if seconds > self.bg_music_length:
        #     arcade.play_sound(self.bg_music)
        #     self.total_time = 0.0

        if not arcade.is_queued(self.bg_music) and not arcade.is_queued(self.prev_music):
            arcade.play_sound(self.bg_music)
        draw_start_time = timeit.default_timer()
        self.physics_engine.update()
        changed_viewport = self.update_player()
        self.update_view_port(changed_viewport)
        self.update_bullets()
        self.update_enemies()
        self.processing_time = timeit.default_timer() - draw_start_time


    def update_player(self):
        self.player_list.update_animation()
        coin_hitlist = arcade.check_for_collision_with_list(self.player,
                                                            self.coin_list)
        for coin in coin_hitlist:
            coin.kill()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        enemy_player_hitlist = arcade.check_for_collision_with_list(self.player,
                                                                    self.enemy_list)
        if len(enemy_player_hitlist) > 0:
            self.player.center_x = PLAYER_START_X
            self.player.center_y = PLAYER_START_Y
            arcade.play_sound(self.game_over)

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
            # if self.bg_music is not None:
            #     arcade.stop_sound(self.bg_music)
            self.setup(self.level)

            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
        return changed_viewport

    def update_bullets(self):
        self.bullet_list = self.player.bullet_list
        self.bullet_list.update()
        for bullet in self.bullet_list:
            enemy_bullet_hitlist = arcade.check_for_collision_with_list(bullet,
                                                                         self.enemy_list)

            if len(enemy_bullet_hitlist) > 0:
                bullet.kill()

            for enemy in enemy_bullet_hitlist:
                enemy.kill()
                self.score += 100
                arcade.play_sound(self.hit_sound)

    def update_enemies(self):
        self.enemy_list.update_animation()
        for enemy in self.enemy_list:
            enemy.center_x += enemy.change_x
            enemy_flag_hitlist = arcade.check_for_collision_with_list(enemy, self.flag_list)
            if enemy_flag_hitlist:
                enemy.change_x = -enemy.change_x

    def update_view_port(self, changed_viewport):
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
