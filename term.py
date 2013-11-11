#!/usr/bin/python
import curses as c

ESCAPE = chr(27)
LEFT  = c.KEY_LEFT
RIGHT = c.KEY_RIGHT
UP    = c.KEY_UP
DOWN  = c.KEY_DOWN

BLACK = 0
BLUE = 1
GREEN = 2
CYAN = 3
RED = 4
MAGENTA = 5
BROWN = 6
LIGHTGRAY = 7

DARKGRAY = 8
LIGHTBLUE = 9
LIGHTGREEN = 10
LIGHTCYAN = 11
LIGHTRED = 12
LIGHTMAGENTA = 13
YELLOW = 14
WHITE = 15

LIGHTGREY = 7
DARKGREY = 8

def init():
  import os
  os.environ["ESCDELAY"] = "25"

  global wnd
  wnd = c.initscr()

  c.noecho()
  c.nocbreak()
  c.raw()
  c.curs_set(False)

  wnd.keypad(True)

  c.start_color()
  #c.init_pair(0, c.COLOR_BLACK, c.COLOR_BLACK)
  c.init_pair(1, c.COLOR_BLUE, c.COLOR_BLACK)
  c.init_pair(2, c.COLOR_GREEN, c.COLOR_BLACK)
  c.init_pair(3, c.COLOR_CYAN, c.COLOR_BLACK)
  c.init_pair(4, c.COLOR_RED, c.COLOR_BLACK)
  c.init_pair(5, c.COLOR_MAGENTA, c.COLOR_BLACK)
  c.init_pair(6, c.COLOR_YELLOW, c.COLOR_BLACK)
  c.init_pair(7, c.COLOR_WHITE, c.COLOR_BLACK)

  c.init_pair(8, c.COLOR_BLACK, c.COLOR_BLACK)
  c.init_pair(9, c.COLOR_BLUE, c.COLOR_BLACK)
  c.init_pair(10, c.COLOR_GREEN, c.COLOR_BLACK)
  c.init_pair(11, c.COLOR_CYAN, c.COLOR_BLACK)
  c.init_pair(12, c.COLOR_RED, c.COLOR_BLACK)
  c.init_pair(13, c.COLOR_MAGENTA, c.COLOR_BLACK)
  c.init_pair(14, c.COLOR_YELLOW, c.COLOR_BLACK)
  c.init_pair(15, c.COLOR_WHITE, c.COLOR_BLACK)

def deinit():
  c.endwin();

def flush():
  wnd.refresh();

def put(s):
  wnd.addstr(s)

def go(x, y):
  wnd.move(y, x)

def getch():
  ch = wnd.getch()
  if 32 <= ch < 256:
    return chr(ch)
  else:
    return ch

def kbhit():
  wnd.nodelay(1)
  ch = wnd.getch()
  wnd.nodelay(0)
  if ch == -1:
    wnd.ungetch(ch)
    return True
  else:
    return False

def color(col, bgcol=0):
  if col > 7:
    wnd.attrset(c.A_BOLD | c.color_pair(col))
  else:
    wnd.attrset(           c.color_pair(col))

def clrscr():
  wnd.clear()

def cursor(yes):
  c.curs_set(yes)

if __name__ == "__main__":
  init()
  for fg in range(16):
    color(7, 0)
    put("%2s " % fg)
    for bg in range(16):
      color(fg, bg)
      put("###")
      color(7, 0)
      put(' ')
    put("\n")
  getch()
  deinit()
