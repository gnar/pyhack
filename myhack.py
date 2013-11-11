#!/usr/bin/python
from __future__ import print_function
import ui
import game
import term
import savegame

import sys, traceback

if __name__ == "__main__":
  try:
    __builtins__.game = savegame.load()
  except:
    __builtins__.game = game.Game()

  term.init()
  try:
    ui.mainloop()
  except Exception as e:
    term.go(0, 0)
    term.deinit()
    traceback.print_tb(sys.exc_traceback)
    print("%s: %s" % (type(e), e.message))
  finally:
    term.deinit()
