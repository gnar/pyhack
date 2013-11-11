import sys
import operator
import random

import monster
import monster_template
#import item
#import item_template
import level_template

import maptool

import term
import dice
import cells

class Level(object):

  # Mappings:
  #   cell_map (contains level cells)
  #   explored_map (cells seen by pc: (ch,col) pairs)
  #
  # Derived:
  #   monsters_map (derived from self.monsters)

  def _make_mapping(self, default_entry=None):
    return [[default_entry for x in range(self.width)] for y in range(self.height)]

  def __init__(self, template):
    if isinstance(template, str):
      template = level_template.db[template]
    self.template = template

    self.monsters = []

    # initial level generation
    self.generate_cells()
    while self.num_monsters < self.max_spawn_monsters:
      self.spawn_random_monster()

  def __getattr__(self, name):
    t = self.__dict__.get("template", None)
    if name == "maptool":
      return self._rebuild_maptool()
    elif name == "monsters_map":
      return self._rebuild_monsters_map()
    else:
      try:
        return getattr(t, name)
      except:
        raise AttributeError(name)

  def turn(self):
    # update and spawn monsters
    self.remove_dead_monsters()
    if self.num_monsters < self.max_spawn_monsters:
      if dice.chance(self.spawn_rate):
        self.spawn_random_monster()

  # pickling management

  def _rebuild_maptool(self):
    self.maptool = maptool.MapTool(self.width, self.height)
    for y in range(self.height):
      for x in range(self.width):
        self.set_cell(x, y, self.cells_map[y][x])
    return self.maptool

  def _rebuild_monsters_map(self):
    self.monsters_map = self._make_mapping()
    for mon in self.monsters:
      x, y = self.get_monster_pos(mon)
      self.monsters_map[y][x] = mon
    return self.monsters_map

  def __getstate__(self):
    data = dict(self.__dict__)
    data.pop("maptool", None)
    data.pop("monsters_map", None)
    return data

  ################################################################################
  # Level generation                                                             #
  ################################################################################

  def generate_cells(self):
    self.maptool = maptool.MapTool(self.width, self.height)
    self.cells_map = self._make_mapping()
    self.explored_map = self._make_mapping((' ', 8))

    ch_map = self.map.split()

    # parse cell_alias
    cell_alias = {}
    for ch, info in dict(getattr(self, 'cell_alias', [])).items():
      if isinstance(info, str):
        cell_class, cell_kwargs = cells.db[info], {}
      else:
        cell_class, cell_kwargs = cells.db[info[0]], info[1]
      cell_alias[ch] = (cell_class, cell_kwargs)

    # create all cells
    for y in range(self.height):
      for x in range(self.width):
        ch = ch_map[y][x]
        if ch in cell_alias:
          cell_class, cell_kwargs = cell_alias[ch]
        else:
          cell_class, cell_kwargs = cells.db_alias[ch], {}
        self.set_cell(x, y, cell_class(**cell_kwargs))

  def spawn_random_monster(self):
    mon = monster.Monster(monster_template.random_select(1, self.danger_level))
    x, y = self.find_empty_cell()
    self.add_monster(mon, x, y)

  ################################################################################
  # Cells                                                                        #
  ################################################################################

  def iter_cells(self, x_range=None, y_range=None):
    x_range = x_range or (0, self.width)
    y_range = y_range or (0, self.height)
    for y in range(*y_range):
      row = self.cells_map[y]
      for x in range(*x_range):
        yield x, y, row[x]

  def find_empty_cell(self):
    """Return (x,y) cell position of an empty cell without a monster"""
    while True:
      x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
      if cells.is_walkable(self.cells_map[y][x]) and not self.get_monster_at(x, y):
        return x, y

  def get_cell(self, x, y):
    return self.cells_map[y][x]

  def set_cell(self, x, y, cell):
    self.cells_map[y][x] = cell
    self.maptool.set_flag(x, y, maptool.OPAQUE_FLAG, cells.is_opaque(cell))
    self.maptool.set_flag(x, y, maptool.WALKABLE_FLAG, cells.is_walkable(cell))

  def cell_gfx(self, x, y):
    return cells.gfx(self.cells_map[y][x])

  ################################################################################
  # Field of vision (FOV) and pc distance map                                    #
  ################################################################################

  def iter_seen_monsters(self, x_range=None, y_range=None):
    (x0, x1), (y0, y1) = x_range, y_range
    for mon in self.seen_monsters:
      x, y = self.get_monster_pos(mon)
      if x < x0 or y < y0 or x >= x1 or y >= y1: continue
      yield x, y, mon

  def calculate_fov(self, x, y, radius):
    self.maptool.calculate_fov(x, y, radius)
    self.seen_monsters = []

    monsters_map = self.monsters_map
    is_visible = lambda x, y: self.maptool.get_flag(x, y, maptool.VISIBLE_FLAG)

    for y in range(self.height):
      cells_row = self.cells_map[y]
      explored_row = self.explored_map[y]
      for x in range(self.width):
        if is_visible(x, y):
          explored_row[x] = cells.gfx(cells_row[x])
          mon = monsters_map[y][x]
          if mon and mon.is_alive: self.seen_monsters.append(mon)

  def calculate_distance_map(self, points):
    self.maptool.calculate_distance_map(points)

  ################################################################################
  # Monsters                                                                     #
  ################################################################################

  def add_monster(self, mon, x, y):
    assert not mon.location
    assert not self.monsters_map[y][x]
    mon.location = monster.Location(self, x, y)
    self.monsters.append(mon)
    self.monsters_map[y][x] = mon

  def remove_monster(self, mon):
    loc = mon.location
    assert loc.level == self
    self.monsters.remove(mon)
    self.monsters_map[loc.y][loc.x] = None
    mon.location = None
    # Gotcha: Also remove from seen_monsters list!
    if mon in self.seen_monsters: self.seen_monsters.remove(mon)

  def remove_dead_monsters(self):
    dead_monsters = filter(operator.attrgetter("is_dead"), self.monsters)
    for mon in dead_monsters:
      self.remove_monster(mon)

  def move_monster(self, mon, x, y):
    loc = mon.location
    assert loc.level == self
    assert not self.monsters_map[y][x]
    self.monsters_map[loc.y][loc.x] = None
    loc.x, loc.y = x, y
    self.monsters_map[loc.y][loc.x] = mon

  def nudge_monster_at(self, x, y):
    """Make sure that any monster at (x,y) is moved onto another cell."""
    mon = self.get_monster_at(x, y)
    if mon:
      # TODO: Prefer adjacent free cells...
      x0, y0 = self.find_empty_cell()
      self.move_monster(mon, x0, y0)

  def get_monster_pos(self, mon):
    loc = mon.location
    assert loc.level == self
    return loc.x, loc.y

  def next_monster(self):
    assert len(self.monsters) > 0
    while True:
      mon = max(self.monsters, key=lambda mon: mon.location.move_pts)
      if mon.location.move_pts > 0:
        mon.location.move_pts -= 100
        return mon
      else:
        for mon in self.monsters:
          mon.location.move_pts += mon.speed

  def iter_monsters(self, x_range=None, y_range=None):
    if not x_range and not y_range:
      for mon in self.monsters:
        yield mon.location.x, mon.location.y, mon
    else:
      (x0, x1), (y0, y1) = x_range, y_range
      for x, y, mon in self.iter_monsters():
        if x < x0 or y < y0 or x >= x1 or y >= y1: continue
        yield x, y, mon

  def get_monster_at(self, x, y):
    return self.monsters_map[y][x]

  @property
  def num_monsters(self):
    return len(self.monsters)


def connect(lev1, pos1, lev2, pos2):
  """E.g. connect_levels(lev1, cells.StairsUp, lev2, cells.StairsDown)"""

  def find_unique_cell_by_class(lev, cell_cls):
    pos = None
    for x, y, cell in lev.iter_cells():
      if isinstance(cell, cell_cls):
        if pos is not None: return None # two found -> not unique
        pos = (x,y)
    return pos

  if issubclass(pos1, cells.AbstractPortal): pos1 = find_unique_cell_by_class(lev1, pos1)
  if issubclass(pos2, cells.AbstractPortal): pos2 = find_unique_cell_by_class(lev2, pos2)
  assert pos1 and pos2

  portal1, portal2 = lev1.get_cell(*pos1), lev2.get_cell(*pos2)
  portal1.connection = lev2, pos2[0], pos2[1]
  portal2.connection = lev1, pos1[0], pos1[1]
