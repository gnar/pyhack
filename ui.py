import term
import misc
import cells
import ai
import savegame

debug_show_distances = False

class Pager(object):
  more_txt = "(more)"
  more_len = len(more_txt)+1

  def __init__(self, x=0, y=0, width=80, height=2):
    self.x, self.y, self.width, self.height = x, y, width, height

  def clear(self):
    spaces = " " * self.width
    for y in range(self.y, self.y + self.height):
      term.go(self.x, y)
      term.put(spaces)
    self.cur_x, self.cur_y = 0, 0

  def put_word(self, word):
    term.go(self.x + self.cur_x, self.y + self.cur_y)
    term.put(word)
    self.cur_x += len(word) + 1

  def put_more_prompt(self):
    self.put_word(Pager.more_txt)
    term.getch()

  def carriage_return(self):
    self.cur_x = 0
    self.cur_y += 1

  def put_words(self, words):
    term.color(0)
    num_words = len(words)
    w = 0 # word index, e.g. words[w]

    # word loop
    while w < num_words:
      is_last_row = (self.cur_y == self.height-1)

      word = words[w] # select next word to print
      word_len = len(word)

      if is_last_row:
        word_fits = (self.cur_x + word_len + Pager.more_len <= self.width) # for the last row, also reserve space for a potential "(more)" prompt.
      else:
        word_fits = (self.cur_x + word_len <= self.width)

      if word_fits:
        self.put_word(word)
        w += 1 # advance to next word
      else:
        if not is_last_row:
          self.carriage_return()
        else:
          self.put_more_prompt()
          self.clear()

  def put(self, fmt, *args):
    words = (fmt % args).split()
    self.put_words(words)

  def choice(self, valid_choices, fmt, *args, **kwargs):
    assert isinstance(valid_choices, str)
    self.clear()
    question = (fmt % args)
    if not kwargs.pop("hide_valid_choices", False): question += " [%s]" % valid_choices
    self.put(question)
    ch = 'invalid'
    term.cursor(True)
    while ch not in valid_choices:
      ch = term.getch()
      if not isinstance(ch, str): ch = 'invalid'
    term.cursor(False)
    self.clear()
    return ch

  def yes_no(self, fmt, *args):
    return self.choice("yn", fmt, *args) == 'y'

  def ask_dir(self, fmt, *args):
    ch = self.choice("12346789", fmt, *args, hide_valid_choices=True)
    return misc.char2dir(ch)

class StatusBar(object):
  def __init__(self, x, y, width, height):
    self.x, self.y, self.width, self.height = x, y, width, height

  def draw(self, who):
    x, y = self.x, self.y

    term.color(7); term.go(x, y)
    term.put(who.name)

    term.go(x+13, y); term.color(9)
    term.put("%s/%s" % (who.hp, who.max_hp))

    term.go(x+21, y); term.color(12)
    term.put("%s/%s" % (who.mp, who.max_mp))

class Camera(object):
  def __init__(self, x, y, width, height):
    self.x, self.y, self.width, self.height = x, y, width, height
    self.top_x = 0
    self.top_y = 0

  def scroll(self, level, focus_x, focus_y):
    """Adjust (self.top_x, self.top_y) so that (focus_x, focus_y) is centered."""
    new_top_x = misc.clamp(focus_x - self.width//2, 0, level.width - self.width)
    new_top_y = misc.clamp(focus_y - self.height//2, 0, level.height - self.height)
    needed_adjustment = (self.top_x != new_top_x or self.top_y != new_top_y)
    self.top_x, self.top_y = new_top_x, new_top_y
    return needed_adjustment

  def draw(self, level, who, full_refresh=False):
    gfx, color, go, put = cells.gfx, term.color, term.go, term.put

    X, Y = level.get_monster_pos(who)

    needed_adjustment = self.scroll(level, X, Y)

    # Cell index range to draw.
    x_range = (misc.clamp(self.top_x, 0, level.width), misc.clamp(self.top_x + self.width, 0, level.width))
    y_range = (misc.clamp(self.top_y, 0, level.height), misc.clamp(self.top_y + self.height, 0, level.height))

    # (x,y) -> (x+dx,y+dx) is the mapping from cell index to screen column/row index.
    dx = self.x - self.top_x
    dy = self.y - self.top_y

    # Draw cells
    for x, y, cell in level.iter_cells(x_range, y_range):
      ch, col = level.explored_map[y][x]
      if debug_show_distances:
        d = level.maptool.get_distance_map(x, y)
        if d > 0: ch = str(d%10)[0]
      go(x+dx, y+dy)
      color(col)
      put(ch)

    # Draw seen monsters
    for x, y, mon in level.iter_seen_monsters(x_range, y_range):
      ch, col = mon.gfx
      go(x+dx, y+dy)
      color(col)
      put(ch)

class UserInterface(object):
  WIDTH = 80
  HEIGHT = 25

  def __init__(self):
    self.pager = Pager(0, 0, 80, 2)
    self.statusbar = StatusBar(0, 24, 80, 1)
    self.camera = Camera(0, 2, 80, 22)
    self.level = None # currently displayed level (must contain pc)


def put(fmt, *args):
  ui.pager.put(fmt, *args)

def ifpc(who, fmt, *args):
  if who.is_pc:
    ui.pager.put(fmt, *args)

def ask(choices, fmt, *args):
  return ui.pager.ask(choices, fmt, *args)

def yes_no(fmt, *args):
  return ui.pager.yes_no(fmt, *args)

def ask_dir(fmt, *args):
  return ui.pager.ask_dir(fmt, *args)

def ask_dir(fmt, *args):
  return ui.pager.ask_dir(fmt, *args)

################################################################################
# C O M M A N D S                                                              #
################################################################################

def scan_for_unique_adjacent_cell(level, x, y, cell_class):
  found_dir = None
  for dir in misc.dirs:
    dx, dy = dir
    if level.get_cell(x+dx, y+dy).__class__ == cell_class:
      if found_dir is not None: return None # found more than one? not unique, so return None.
      found_dir = dir
  return found_dir

def do_walk_or_attack(dir):
  x, y   = level.get_monster_pos(pc)
  dx, dy = dir

  target = level.get_monster_at(x+dx, y+dy)
  if target:
    pc.attack(target)
  else:
    cell = level.get_cell(x+dx, y+dy)
    cells.walk(level, pc, cell, x+dx, y+dy)

def do_kick():
  dir = ask_dir("Kick in which direction?")
  x, y = level.get_monster_pos(pc)
  dx, dy = dir
  cell = level.get_cell(x+dx, y+dy)
  cells.kick(level, pc, cell, x+dx, y+dy)

def do_pray():
  put("You pray.")
  put("You feel comfortable.")

def do_search():
  pass

def do_open():
  x, y = level.get_monster_pos(pc)
  dir = scan_for_unique_adjacent_cell(level, x, y, cells.Door)
  if not dir:
    dir = ask_dir("Open direction?")
  dx, dy = dir
  cell = level.get_cell(x+dx, y+dy)
  cells.open(level, pc, cell, x+dx, y+dy)

def do_close():
  x, y = level.get_monster_pos(pc)
  dir = scan_for_unique_adjacent_cell(level, x, y, cells.Door)
  if not dir:
    dir = ask_dir("Open direction?")
  dx, dy = dir
  cell = level.get_cell(x+dx, y+dy)
  cells.close(level, pc, cell, x+dx, y+dy)

def do_handle():
  put("You don't see any specific to handle.")

def do_chat():
  put("You don't see anyone to chat with.")

def do_enter():
  x, y = level.get_monster_pos(pc)
  cell = level.get_cell(x, y)
  cells.enter(level, pc, cell, x, y)

################################################################################
# M A I N L O O P                                                              #
################################################################################

def do_player():
  ch = term.getch()
  ui.pager.clear()

  walk_dir = misc.char2dir(ch)
  if walk_dir is not None:
    do_walk_or_attack(walk_dir)
  elif ch == 'k':
    do_kick()
  elif ch == 'o':
    do_open()
  elif ch == 'c':
    do_close()
  elif ch == '_':
    do_pray()
  elif ch == 'h':
    do_handle()
  elif ch == 'C':
    do_chat()
  elif ch == 's':
    put("You wait.")
  elif ch in ('<', '>'):
    do_enter()
  elif ch == 'Q':
    quit = yes_no("Do you want to quit?")
    if quit: return "quit"
  elif ch == 'x':
    global debug_show_distances
    debug_show_distances = not debug_show_distances
  elif ch == '?':
    put("pos=(%s,%s)", pc.location.x, pc.location.y)
  else:
    put("Unknown command. keycode=%s", ch)

def mainloop():
  term.clrscr()

  global ui
  ui = UserInterface()
  ui.pager.clear()

  global pc
  pc = game.pc

  global level
  level = game.pc.location.level

  level.calculate_fov(pc.location.x, pc.location.y, pc.fov)
  level.calculate_distance_map([(pc.location.x, pc.location.y)])

  done = False
  while not done:
    mon = None
    while mon != pc:
      mon = level.next_monster() # get next monster
      if not mon.is_pc:
        ai.turn(level, mon)
        if pc.is_dead:
          done = True
          break
      else:
        level.calculate_fov(pc.location.x, pc.location.y, pc.fov)
        level.calculate_distance_map([(pc.location.x, pc.location.y)])
        ui.camera.draw(level, pc)
        ui.statusbar.draw(pc)

        result = do_player()
        done = (result == "quit")

        # Check if player changed levels
        if pc.location.level != level:
          # TODO: Think..
          term.clrscr()
          ui.pager.clear()
          level = pc.location.level
          level.calculate_fov(pc.location.x, pc.location.y, pc.fov)
          level.calculate_distance_map([(pc.location.x, pc.location.y)])
          ui.camera.draw(level, pc)

          if not level.is_visited and level.onetime_message:
            put(level.onetime_message)
          level.is_visited = True

      level.turn()

  savegame.save(game)
