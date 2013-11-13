class ItemTemplate(object):
  defaults = {
    'name': "<no-name>",
    'danger_level': 1,
    'weight': 10,
    'item_class': 'misc'
  }

  def __init__(self, **kwargs):
    self.__dict__.update(ItemTemplate.defaults)
    self.__dict__.update(kwargs)
