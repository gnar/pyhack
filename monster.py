import ui
import misc
import monster_template

class Location(object):
  def __init__(self, level, x=0, y=0, move_pts=0):
    self.level = level
    self.x = x
    self.y = y
    self.move_pts = move_pts

class Monster(object):
  def __init__(self, tmpl):
    if isinstance(tmpl, str):
      tmpl = monster_template.db[tmpl]
    self.template = tmpl

    self._hp = self.max_hp
    self.mp = self.max_hp

    self.location = None

  def __getattr__(self, name):
    t = self.__dict__.get("template", None)
    try:
      return getattr(t, name)
    except:
      raise AttributeError(name)

  ################################################################################ 
  # Hitpoints                                                                    #
  ################################################################################ 

  def set_hp(self, hp):
    self._hp = hp
    if self._hp > self.max_hp:
      self._hp = self.max_hp
  def get_hp(self):
    return self._hp
  hp = property(get_hp, set_hp)

  def heal(self, hp):
    if not self.is_dead:
      self.hp += hp

  def injure(self, hp):
    self.hp -= hp

  def kill(self):
    self.set_hp(0)

  @property
  def is_dead(self):
    return self.hp <= 0

  @property
  def is_alive(self):
    return self.hp > 0

  ################################################################################ 
  # Melee attack                                                                 #
  ################################################################################ 

  def attack(self, target):
    ui.ifpc(self, "You attack the %s", target.name)
    if not target.is_pc:
      target.kill()

class PC(Monster):
  def __init__(self):
    super(PC, self).__init__("pc")

    self.max_mp = 24
    self.mp = 12
    self.speed = 125
    self.fov = 10
