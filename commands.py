class Command:
    def execute(self):
        pass


class JumpCommand(Command):
    def execute(self, actor):
        actor.jump()


class ShootCommand(Command):
    def execute(self, actor):
        actor.shoot_bullet()


class WalkLeftCommand(Command):
    def execute(self, actor):
        actor.walk_left()


class WalkRightCommand(Command):
    def execute(self, actor):
        actor.walk_right()


class StopWalkingCommand(Command):
    def execute(self, actor):
        actor.stop_walking()
