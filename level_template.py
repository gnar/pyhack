from __future__ import print_function
import yaml

class LevelTemplate(object):
  defaults = {
    'name': "<no-name>",
    'danger_level': 1,
    'width': 80,
    'height': 22,
    'max_spawn_monsters': 12,
    'onetime_message': None,

    # Flags
    'is_outdoors': False,    # level is outside
    'is_visited': False,     # was visited by the pc?
  }

  def __init__(self, **kwargs):
    self.__dict__.update(LevelTemplate.defaults)
    self.__dict__.update(kwargs)

def load(level_id, **kwargs):
  print("Loading", level_id)
  filename = "data/level_template/%s.yaml" % level_id
  with open(filename, "r") as fd:
    data = yaml.load(fd)
  data.update(kwargs)
  return LevelTemplate(**data)

db = {
  'cave_outside': load('cave_outside'),
  'cave1': load('cave1'),
  'cave2': load('cave2'),
  'cave3': load('cave3'),
  'prison': load('prison'),
}
db_ids = list(db.keys())

for id, mon in db.items(): mon.db_id = id
