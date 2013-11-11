import ui
import dice

class Cell(object):
  alias = None
  default_cell_info = ()
  default_kick_msg = "Ouch! You hurt your foot!"
  default_open_msg = "You see nothing you could open."
  default_close_msg = "You see nothing you could open."
  default_enter_msg = "You don't see stairs."
  default_descr = "<no-descr>"
  default_properties = {}

  def __init__(self, **kwargs):
    self.__dict__.update(self.default_properties)
    self.__dict__.update(kwargs)

  def gfx(self):
    return self.default_gfx

  def describe(self):
    return self.default_descr

  def is_opaque(self):
    return self.default_is_opaque

  def is_walkable(self):
    return self.default_is_walkable

  # Actions on cell by monsters

  def kick(self, level, who, x, y):
    ui.ifpc(who, self.default_kick_msg)

  def walk(self, level, who, x, y):
    if self.is_walkable():
      level.move_monster(who, x, y)

  def open(self, level, who, x, y):
    ui.ifpc(who, self.default_open_msg)

  def close(self, level, who, x, y):
    ui.ifpc(who, self.default_close_msg)

  def enter(self, level, who, x, y):
    ui.ifpc(who, self.default_enter_msg)


class Door(Cell):
  alias = '+'
  default_properties = {'state': 'closed', 'material': 'metal'}

  def is_walkable(self):
    return self.state in ('open', 'smashed')

  def is_opaque(self):
    return self.state == 'closed'

  def kick(self, level, who, x, y):
    if self.state in ('open', 'smashed'):
      ui.ifpc(who, "You kick at air.")
    elif self.state == 'closed':
      ui.ifpc(who, "You smash the door to pieces.")
      self.state = 'smashed'
    level.set_cell(x, y, self)

  def walk(self, level, who, x, y):
    if self.state != 'closed':
      super(Door, self).walk(level, who, x, y)
    else:
      bonk_tab = {'wood': "*bong!*", 'metal': "*plang!*"}
      ui.ifpc(who, bonk_tab[self.material])

  def open(self, level, who, x, y):
    if self.state == "closed":
      ui.ifpc(who, "You open the door.")
      self.state = 'open'
    else:
      ui.ifpc(who, "The door is already open.")
    level.set_cell(x, y, self)

  def close(self, level, who, x, y):
    if self.state == "open":
      ui.ifpc(who, "You close the door.")
      self.state = 'closed'
    else:
      ui.ifpc(who, "The door is already closed.")
    level.set_cell(x, y, self)

  _ch_map = {'open': '/', 'closed': '+', 'smashed': '.'}
  _col_map = {'wood': 6, 'metal': 8}

  def gfx(self):
    return (Door._ch_map[self.state], Door._col_map[self.material])

class Floor(Cell):
  alias = '.'
  default_is_walkable = True
  default_is_opaque = False
  default_gfx = ('.', 7)
  default_descr = "Floor."

class Grass(Cell):
  default_is_walkable = True
  default_is_opaque = False
  default_gfx = ('.', 10)
  default_descr = "gras"

class Tree(Cell):
  alias = 'T'
  default_is_walkable = True
  default_is_opaque = False
  default_gfx = ('T', 10)
  default_descr = "tree"
  default_properties = {'looted': False}

  def kick(self, level, who, x, y):
    ui.ifpc(who, "You kick the tree.")
    if dice.chance(20):
      ui.ifpc(who, "You hurt your foot!")
    if not self.looted:
      if dice.chance(20):
        ui.ifpc(who, "Some apples drop down.")
      if dice.chance(20):
        self.looted = True

class Wall(Cell):
  alias = '#'
  default_is_walkable = False
  default_is_opaque = True
  default_gfx = ('#', 7)
  default_descr = "a wall"

class Water(Cell):
  alias = '='
  default_is_walkable = False
  default_is_opaque = False
  default_gfx = ('=', 1)
  default_descr = "water"

  def kick(self, level, who, x, y):
    ui.ifpc(who, "*splash*")

class Lava(Cell):
  default_is_walkable = False
  default_is_opaque = False
  default_gfx = ('=', 4)
  default_descr = "lava"

class Altar(Cell):
  alias = '_'
  default_is_walkable = True
  default_is_opaque = False
  default_gfx = ('_', 7)
  default_cell_info = ('neutral',)

class AbstractPortal(Cell):
  default_is_walkable = True
  default_is_opaque = False
  default_properties = {'connection': (None, 0, 0)} # (level, x, y)

  def enter(self, level, who, x, y):
    if not who.is_pc: return

    new_level, x, y = self.connection
    if not new_level:
      ui.ifpc(who, "This path leads nowhere...")
    else:
      level.remove_monster(who)
      new_level.nudge_monster_at(x, y)
      new_level.add_monster(who, x, y)

class StairsUp(AbstractPortal):
  alias = '<'
  default_gfx = ('<', 7)

class StairsDown(AbstractPortal):
  alias = '>'
  default_gfx = ('>', 7)

class Tunnel(AbstractPortal):
  alias = '*'
  default_gfx = ('*', 7)

# Throne, Ice

####################################################################

def gfx(cell):
  return cell.gfx()

def describe(cell):
  return cell.describe()

def is_walkable(cell):
  return cell.is_walkable()

def is_opaque(cell):
  return cell.is_opaque()

def walk(level, who, cell, x, y):
  return cell.walk(level, who, x, y)

def kick(level, who, cell, x, y):
  return cell.kick(level, who, x, y)

def open(level, who, cell, x, y):
  return cell.open(level, who, x, y)

def close(level, who, cell, x, y):
  return cell.close(level, who, x, y)

def enter(level, who, cell, x, y):
  return cell.enter(level, who, x, y)

####################################################################

db = {
  'floor': Floor,
  'grass': Grass,
  'wall': Wall,
  'door': Door,
  'water': Water,
  'tree': Tree,
  'stairs_up': StairsUp,
  'stairs_down': StairsDown,
  'tunnel': Tunnel,
}

db_alias = {cell_class.alias: cell_class for cell_class in db.values() if cell_class.alias is not None}

def make_cell_from_alias(ch, *args, **kwargs):
  return db_alias.get(ch, Floor)(*args, **kwargs)
