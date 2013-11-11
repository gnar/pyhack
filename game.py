import cells
import level
import level_template
import monster

class Game(object):
  def __init__(self):
    # Create player character
    self.pc = monster.PC()

    # Create levels...
    self.lev_cave_outside = level.Level("cave_outside")
    self.lev_cave1 = level.Level("cave1")
    self.lev_cave2 = level.Level("cave2")
    self.lev_cave3 = level.Level("cave3")
    level.connect(self.lev_cave_outside, cells.Tunnel, self.lev_cave1, cells.StairsUp)
    level.connect(self.lev_cave1, cells.StairsDown, self.lev_cave2, cells.StairsUp)
    level.connect(self.lev_cave2, cells.StairsDown, self.lev_cave3, cells.StairsUp)

    start = self.lev_cave_outside
    start.nudge_monster_at(8, 5)
    start.add_monster(self.pc, 8, 5)
