import ctypes

OPAQUE_FLAG   = (1<<0)
WALKABLE_FLAG = (1<<1)
MONSTER_FLAG  = (1<<2)
ITEM_FLAG     = (1<<3)
VISIBLE_FLAG  = (1<<16)
EXPLORED_FLAG = (1<<17)

class MapTool(object):

  def __init__(self, width, height):
    self.mt = lib.maptool_new(width, height)

    self.i0 =               (ctypes.c_int)(0)
    self.p0 = ctypes.POINTER(ctypes.c_int)(self.i0)
    self.i1 =               (ctypes.c_int)(0)
    self.p1 = ctypes.POINTER(ctypes.c_int)(self.i1)

  def __del__(self):
    lib.maptool_delete(self.mt)

  @property
  def width(self):
    return self.mt.contents.width

  @property
  def height(self):
    return self.mt.contents.height

  def set_flag(self, x, y, flag_mask, flag):
    lib.maptool_set_flag(self.mt, x, y, flag_mask, 1 if flag else 0)

  def get_flag(self, x, y, flag_mask):
    return lib.maptool_get_flag(self.mt, x, y, flag_mask) != 0

  def calculate_fov(self, x, y, radius):
    lib.maptool_calculate_fov(self.mt, x, y, radius)

  def calculate_distance_map(self, points):
    num_points = len(points)
    int_array_t = ctypes.c_int * num_points

    xs, ys = int_array_t(), int_array_t()
    for i, (x, y) in enumerate(points):
      xs[i], ys[i] = x, y

    lib.maptool_calculate_distance_map(self.mt, xs, ys, num_points)

    width = self.width
    dist_map = []
    for y in range(self.height):
      offs = y*width
      row = self.mt[0].distance_map[offs:offs+width]
      dist_map.append(row)
    return dist_map

  def get_distance_map(self, x, y):
    return lib.maptool_get_distance_map(self.mt, x, y)

  def get_distance_map_dir(self, x, y):
    lib.maptool_get_distance_map_dir(self.mt, x, y, self.p0, self.p1)
    return self.i0.value, self.i1.value

def load_dll(dll_file="./libmaptool.so"):
  global lib
  c = ctypes

  class MapTool_t(c.Structure):
    _fields_ = (
       ("width", c.c_int),
       ("height", c.c_int),
       ("flags", c.POINTER(c.c_uint)),
       ("distance_map", c.POINTER(c.c_int)),
       ("expa_size", c.c_int),
       ("expa_capa", c.c_int),
       ("expa_x", c.POINTER(c.c_int)),
       ("expa_y", c.POINTER(c.c_int)),
       ("expa_dist", c.POINTER(c.c_int)),
    )
  MapTool_ptr = c.POINTER(MapTool_t)

  lib = c.cdll.LoadLibrary(dll_file)

  lib.maptool_new.restype = MapTool_ptr
  lib.maptool_new.argtypes = (c.c_int, c.c_int)

  lib.maptool_delete.restype = None
  lib.maptool_delete.argtypes = (MapTool_ptr,)

  lib.maptool_set_flag.restype = None
  lib.maptool_set_flag.argtypes = (MapTool_ptr, c.c_int, c.c_int, c.c_uint, c.c_int)

  lib.maptool_get_flag.restype = c.c_int
  lib.maptool_get_flag.argtypes = (MapTool_ptr, c.c_int, c.c_int, c.c_uint)

  lib.maptool_calculate_fov.restype = None
  lib.maptool_calculate_fov.argtypes = (MapTool_ptr, c.c_int, c.c_int, c.c_int)

  lib.maptool_calculate_distance_map.restype = None
  lib.maptool_calculate_distance_map.argtypes = (MapTool_ptr, c.POINTER(c.c_int), c.POINTER(c.c_int), c.c_int)

  lib.maptool_get_distance_map.restype = c.c_int
  lib.maptool_get_distance_map.argtypes = (MapTool_ptr, c.c_int, c.c_int)

  lib.maptool_get_distance_map_dir.restype = None
  lib.maptool_get_distance_map_dir.argtypes = (MapTool_ptr, c.c_int, c.c_int, c.POINTER(c.c_int), c.POINTER(c.c_int))

  return lib

lib = load_dll()
