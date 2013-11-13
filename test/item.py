import item_template

class Item(object):

  class LocationOnGround(object):
    def __init__(self, level, x, y):
      self.level = level
      self.x = x
      self.y = y

  class LocationInInventory(object):
    def __init__(self, mon):
      self.monster = mon

  def __init__(self, template):
    self.template = template
    self.location = None

  def __getattr__(self, name):
    t = self.template
    if t:
      return getattr(t, name)
    else:
      raise AttributeError(name)
