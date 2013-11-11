import misc
import cells
import monster

def do_walk_or_attack(level, mon, dir):
  x, y = level.get_monster_pos(mon)
  dx, dy = dir

  target = level.get_monster_at(x+dx, y+dy)
  if target:
    if target.is_pc:
      mon.attack(target)
  else:
    cell = level.get_cell(x+dx, y+dy)
    cells.walk(level, mon, cell, x+dx, y+dy)

def turn(level, mon):
  x, y = level.get_monster_pos(mon)
  dx, dy = level.maptool.get_distance_map_dir(x, y)
  if (dx,dy) == (0,0): dx, dy = misc.randir()
  do_walk_or_attack(level, mon, (dx, dy))
