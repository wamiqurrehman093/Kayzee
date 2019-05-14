import arcade
from arcade.sprite import *
from variables import *


class Player(Sprite):
    def __init__(self, scale: float = 1,
                 image_x: float = 0, image_y: float = 0,
                 center_x: float = 0, center_y: float = 0):
        super().__init__(scale=scale, image_x=image_x, image_y=image_y,
                         center_x=center_x, center_y=center_y)
        self.state = FACE_RIGHT

        self.stand_right_textures = None
        self.stand_left_textures = None

        self.walk_left_textures = None
        self.walk_right_textures = None
        self.walk_up_textures = None
        self.walk_down_textures = None

        self.shoot_right_textures = None
        self.shoot_left_textures = None
        self.is_shooting = None

        self.cur_texture_index = 0
        self.texture_change_distance = 20
        self.last_texture_change_center_x = 0
        self.last_texture_change_center_y = 0

        self.physics_engine = None
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.gun_sound = arcade.sound.load_sound("sounds/laser1.wav")

        self.bullet_list = arcade.SpriteList()

    def stop_walking(self):
        self.change_x = 0

    def walk_left(self):
        self.change_x = -MOVEMENT_SPEED

    def walk_right(self):
        self.change_x = MOVEMENT_SPEED

    def jump(self):
        if self.physics_engine.can_jump():
            self.change_y = JUMP_SPEED
            arcade.play_sound(self.jump_sound)

    def shoot_bullet(self):
        arcade.sound.play_sound(self.gun_sound)
        bullet = arcade.Sprite("images/items/bullet.png", BULLET_SCALE)
        if self.state == FACE_LEFT:
            bullet.angle = 90
            bullet.change_x = -BULLET_SPEED
            bullet.center_x = self.center_x
            bullet.center_y = self.center_y
            bullet.right = self.left
        elif self.state == FACE_RIGHT:
            bullet.angle = -90
            bullet.change_x = BULLET_SPEED
            bullet.center_x = self.center_x
            bullet.center_y = self.center_y
            bullet.left = self.right

        self.bullet_list.append(bullet)

    def shoot(self):
        if self.is_shooting and self.state == FACE_RIGHT:
            texture_list = self.walk_right_textures
            if texture_list is None or len(texture_list) == 0:
                raise RuntimeError("update_animation was called on a sprite that doesn't have a list of "
                                   "walk right textures.")
        elif self.is_shooting and self.state == FACE_LEFT:
            texture_list = self.walk_left_textures
            if texture_list is None or len(texture_list) == 0:
                raise RuntimeError("update_animation was called on a sprite that doesn't have a "
                                   "list of walk left textures.")

            self.cur_texture_index += 1
            if self.cur_texture_index >= len(texture_list):
                self.cur_texture_index = 0

            self.texture = texture_list[self.cur_texture_index]

        if self._texture is None:
            print("Error, no texture set")
        else:
            self.width = self._texture.width * self.scale
            self.height = self._texture.height * self.scale

    def update_animation(self):
        x1 = self.center_x
        x2 = self.last_texture_change_center_x
        y1 = self.center_y
        y2 = self.last_texture_change_center_y
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        texture_list = []

        change_direction = False
        if self.change_x > 0 \
                and self.change_y == 0 \
                and self.state != FACE_RIGHT \
                and self.walk_right_textures \
                and len(self.walk_right_textures) > 0:
            self.state = FACE_RIGHT
            change_direction = True
        elif self.change_x < 0 and self.change_y == 0 and self.state != FACE_LEFT \
                and self.walk_left_textures and len(self.walk_left_textures) > 0:
            self.state = FACE_LEFT
            change_direction = True
        elif self.change_y < 0 and self.change_x == 0 and self.state != FACE_DOWN \
                and self.walk_down_textures and len(self.walk_down_textures) > 0:
            self.state = FACE_DOWN
            change_direction = True
        elif self.change_y > 0 and self.change_x == 0 and self.state != FACE_UP \
                and self.walk_up_textures and len(self.walk_up_textures) > 0:
            self.state = FACE_UP
            change_direction = True

        if self.change_x == 0 and self.change_y == 0:
            if self.state == FACE_LEFT:
                self.texture = self.stand_left_textures[0]
            elif self.state == FACE_RIGHT:
                self.texture = self.stand_right_textures[0]
            elif self.state == FACE_UP:
                self.texture = self.walk_up_textures[0]
            elif self.state == FACE_DOWN:
                self.texture = self.walk_down_textures[0]

        elif change_direction or distance >= self.texture_change_distance:
            self.last_texture_change_center_x = self.center_x
            self.last_texture_change_center_y = self.center_y

            if self.state == FACE_LEFT:
                texture_list = self.walk_left_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError("update_animation was called on a sprite that doesn't have a "
                                       "list of walk left textures.")
            elif self.state == FACE_RIGHT:
                texture_list = self.walk_right_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError("update_animation was called on a sprite that doesn't have a list of "
                                       "walk right textures.")
            elif self.state == FACE_UP:
                texture_list = self.walk_up_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError("update_animation was called on a sprite that doesn't have a list of "
                                       "walk up textures.")
            elif self.state == FACE_DOWN:
                texture_list = self.walk_down_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a list of walk down textures.")

            self.cur_texture_index += 1
            if self.cur_texture_index >= len(texture_list):
                self.cur_texture_index = 0

            self.texture = texture_list[self.cur_texture_index]

        if self._texture is None:
            print("Error, no texture set")
        else:
            self.width = self._texture.width * self.scale
            self.height = self._texture.height * self.scale


def get_distance_between_sprites(sprite1: Sprite, sprite2: Sprite) -> float:
    distance = math.sqrt((sprite1.center_x - sprite2.center_x) ** 2 + (sprite1.center_y - sprite2.center_y) ** 2)
    return distance
