import random

class MonsterTemplate(object):
  defaults = {
    'name': "<no-name>",
    'gfx': ('@', 15),
    'max_hp': 8,
    'max_mp': 8,
    'speed': 100,
    'is_undead': False,
    'is_invisible': False,
    'is_humanoid': False,
    'danger_level': -1,   # -1: Cannot spawn randomly.
    'is_pc': False,
  }

  def __init__(self, **kwargs):
    self.__dict__.update(MonsterTemplate.defaults)
    self.__dict__.update(kwargs)

T = MonsterTemplate

db = {
  'pc':                     T(gfx=('@',15), name="player", is_humanoid=True, is_pc=True),

  'rat':                    T(gfx=('r', 6), danger_level=1,  max_hp=4,   speed=120, name="rat"),
  'large_bat':              T(gfx=('B', 6), danger_level=1,  max_hp=6,   speed=100, name="large bat"),

  'goblin':                 T(gfx=('g',10), danger_level=2,  max_hp=8,   speed=100, name="goblin", is_humanoid=True),
  'hobgoblin':              T(gfx=('g', 9), danger_level=2,  max_hp=12,  speed=100, name="hobgoblin", is_humanoid=True),

  'kobold':                 T(gfx=('k',10), danger_level=2,  max_hp=6,   speed=100, name="kobold", is_humanoid=True),
  'kobold_mage':            T(gfx=('k',11), danger_level=3,  max_hp=6,   speed=100, name="kobold mage", is_humanoid=True),
  'kobold_chief':           T(gfx=('k', 2), danger_level=3,  max_hp=12,  speed=100, name="kobold chief", is_humanoid=True),

  'orc':                    T(gfx=('o',10), danger_level=1,  max_hp=8,   speed=100, name="orc", is_humanoid=True),
  'orc_chieftain':          T(gfx=('o', 2), danger_level=3,  max_hp=14,  speed=100, name="orc chieftain", is_humanoid=True),
  'ogre':                   T(gfx=('O',10), danger_level=3,  max_hp=14,  speed=100, name="ogre", is_humanoid=True),
  'ogre_magus':             T(gfx=('O',11), danger_level=6,  max_hp=20,  speed=100, name="ogre magus", is_humanoid=True),

  # undeads
  'ghost bat':              T(gfx=('B',15), danger_level=2,  max_hp=6,   speed=120, name="ghost bat", is_undead=True),
  'skeleton':               T(gfx=('z',15), danger_level=3,  max_hp=10,  speed=100, name="skeleton", is_humanoid=True, is_undead=True),
  'skeleton_warrior':       T(gfx=('Z', 7), danger_level=6,  max_hp=18,  speed=100, name="skeleton warrior", is_humanoid=True, is_undead=True),
  #'skeleton_champion':      T(gfx=('s',15), danger_level=12, max_hp=36,  speed=100, name="skeleton champion", is_humanoid=True, is_undead=True),
  #'skeleton_king':          T(gfx=('K',15), danger_level=30, max_hp=100, speed=100, name="skeleton king", is_humanoid=True, is_undead=True),
  'ghost':                  T(gfx=('G',15), danger_level=3,  max_hp=10,  speed=100, name="ghost", is_humanoid=True, is_undead=True),
  'spectre':                T(gfx=('G', 7), danger_level=6,  max_hp=20,  speed=100, name="spectre", is_humanoid=True, is_undead=True),
  'zombie':                 T(gfx=('z', 7), danger_level=5,  max_hp=12,  speed= 80, name="zombie", is_humanoid=True, is_undead=True),
  'ghul':                   T(gfx=('z', 7), danger_level=5,  max_hp=14,  speed= 90, name="ghul", is_humanoid=True, is_undead=True),
  'vampire':                T(gfx=('Z',13), danger_level=10, max_hp=24,  speed=110, name="vampire", is_humanoid=True, is_undead=True),
}
db_ids = list(db.keys())

for id, mon in db.items(): mon.db_id = id

del T

def random_select(dangerlevel_min=1, dangerlevel_max=100):
  while True:
    i = random.randint(0, len(db)-1)
    tmpl = db[db_ids[i]]
    if dangerlevel_min <= tmpl.danger_level <= dangerlevel_max:
      return tmpl
