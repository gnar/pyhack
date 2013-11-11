from random import randint

def clamp(x, x_min=None, x_max=None):
  if x_min != None and x < x_min: x = x_min
  if x_max != None and x > x_max: x = x_max
  return x

class Roll(object):
  def __init__(self, n, f, a=0):
    self.spec = n, f, a

  def roll(self):
    n, f, a = self.spec
    return clamp(sum(randint(1, f) for _ in range(n)) + a, 0)

  def check(self, threshold):
    return self.roll() >= threshold

  __call__ = roll

  def __str__(self):
    n, f, a = self.spec
    if a  < 0: return "%sd%s-%s" % (n, f, -a)
    if a  > 0: return "%sd%s+%s" % (n, f,  a)
    if a == 0: return "%sd%s" % (n, f)

  def __repr__(self):
    return 'D("%s")' % str(self)

def roll_from_string(spec):
  # also accept a constant int spec.
  try:
    return Roll(0, 0, int(spec))
  except:
    pass

  i0 = spec.find("d")
  if i0 == -1: i0 = spec.find("D")
  if i0 == -1: raise ValueError("invalid dice roll spec: %s" % spec)

  i1, sign = spec.find("+"), +1
  if i1 == -1: i1, sign = spec.find("-"), -1
  if i1 == -1: i1, sign = len(spec), None

  # n: number of rolls
  # f: number of faces
  # a: modifer
  try:
    n = int(spec[0:i0])
    f = int(spec[i0+1:i1])
    if sign:
      a = sign * int(spec[i1+1:])
    else:
      a = 0
  except:
    raise ValueError("invalid dice roll spec: %s" % spec)

  return Roll(n, f, a)

def D(*args):
  if len(args) == 1:
    if isinstance(args[0], str): return roll_from_string(args[0])
    if isinstance(args[0], int): return Roll(0, 0, args[0])
    if isinstance(args[0], Roll): return args[0]
  elif len(args) in (2,3):
    return Roll(*args)
  raise ValueError("invalid dice roll spec: %s" % (args,))


def chance(percent):
  return randint(1, 100) <= percent
