import term
import random

dirs = [
  (0,-1),(0,1),(-1,0),(1,0),
  (-1,-1),(1,-1),(-1,1),(1,1),
  (0,0)
]

N, S, W, E, NW, NE, SW, SE, CENTER = dirs

_char2dir = {
  '1': SW,
  '2': S,
  '3': SE,
  '4': W,
  '5': CENTER,
  '6': E,
  '7': NW,
  '8': N,
  '9': NE,
  term.UP: N,
  term.DOWN: S,
  term.LEFT: W,
  term.RIGHT: E,
}

def char2dir(ch):
  return _char2dir.get(ch, None)

def str2sym(s):
  return "_".join(s.lower().split(" "))

def randir():
  return dirs[random.randint(0, 7)]

def clamp(x, x_min, x_max):
  if x < x_min: x = x_min
  if x > x_max: x = x_max
  return x
