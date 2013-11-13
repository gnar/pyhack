#!/usr/bin/python
import random
import itertools

def mkmap(width, height, default_entry=None):
  return [[default_entry for x in range(width)] for y in range(height)]

def prmap(m):
  for y in range(len(m)):
    print "".join(m[y])

def inside(m, x, y):
  if x<0 or y<0: return False
  if y >= len(m): return False
  if x>len(m[0]): return False
  return True

def rand_in_circle(r):
  R = r*r
  while True:
    dx = random.randint(-r, r)
    dy = random.randint(-r, r)
    if dx*dx+dy*dy <= R: return dx, dy

def dig(m, x, y, radius=1):
  for dx in range(-radius,radius+1):
    for dy in range(-radius,radius+1):
      if dx*dx + dy*dy <= radius*radius and inside(m, x+dx, y+dy):
        m[dy+y][dx+x] = '.'

def gencave2(m, w, h):
  r = 5
  dig(m, w/2, h/2, r)

  sx = random.uniform(-1,1)
  sy = random.uniform(-1,1)
  x = w/2
  y = h/2
  while r > 0:
    x += sx
    y += sy
    X, Y = map(int,(x,y))
    if not inside(m, X, X): break
    dig(m, X, X, r)
    r = r-1

m = mkmap(80, 40, '#')
gencave2(m, 80, 40)
prmap(m)



#def gencave_rec(m, x, y, r):
#  dig(m, x, y, r)
#  if r < 4: return
#  for t in range(4):
#    dx, dy = rand_in_circle(r-2)
#    gencave_rec(m, x+dx, y+dy, 3*r/4)
#
#def gencave(m, w, h):
#  gencave_rec(m, x=w/2, y=h/2, r=14)

