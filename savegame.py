import pickle
import gzip

import level_template
import monster_template

PROTOCOL = pickle.HIGHEST_PROTOCOL

def get_persistent_objects():
  pers_classes = (level_template.LevelTemplate, monster_template.MonsterTemplate)
  pers = {}
  pers.update(level_template.db)
  pers.update(monster_template.db)
  return pers, pers_classes

def read(fd):
  pers, pers_classes = get_persistent_objects()
  def persistent_load(id):
    try:
      return pers.get(id)
    except:
      raise pickle.UnpicklingError('Invalid persistent id')

  p = pickle.Unpickler(fd)
  p.persistent_load = persistent_load
  return p.load()

def write(game, fd):
  pers, pers_classes = get_persistent_objects()
  pers = {v: k for k, v in pers.items()}
  def persistent_id(o):
    if isinstance(o, pers_classes):
      return pers.get(o)

  p = pickle.Pickler(fd, protocol=PROTOCOL)
  p.persistent_id = persistent_id
  p.dump(game)


def save(game, filename="savegame.dat"):
  with gzip.open(filename, "wb+") as fd:
    write(game, fd)

def load(filename="savegame.dat"):
  with gzip.open(filename, "rb") as fd:
    return read(fd)
