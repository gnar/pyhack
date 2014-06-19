import ctypes

class Map(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height

    self._flags_t = (ctypes.c_uint * width) * height
    self._flags = self._flags_t()

    self._dist_map_t = (ctypes.c_int * width) * height
    self._dist_map = self._dist_map_t()

  def get(self, x, y, mask):
    return self._flags[y][x] | mask

  def set(self, x, y, mask, bit):
    row = self._flags[y]
    if bit:
      row[x] = row[x] | mask
    else:
      row[x] = ~(~row[x] & mask)

  def to_list(self, mask=~0):
    return [self._flags[y][:] for y in range(self.height)]

  def calculate_distance_map(self, goals, flag, mask=~0):
    c_int    = ctypes.c_int
    c_int_p  = ctypes.POINTER(c_int)
    c_uint   = ctypes.c_uint
    c_uint_p = ctypes.POINTER(c_uint)

    n = len(goals)
    int_arr_t = c_int * n
    xs, ys = int_arr_t(), int_arr_t()
    for i, (x, y) in enumerate(goals): xs[i], ys[i] = x, y

    global lib
    lib.calculate_distance_map(self.width, self.height, ctypes.cast(self._flags, c_uint_p), flag, mask, xs, ys, n, ctypes.cast(self._dist_map, c_int_p))

    return [self._dist_map[y][:] for y in range(self.height)]

  def calculate_fov(self, x, y, radius, flag, mask=~0):
    c_int    = ctypes.c_int
    c_int_p  = ctypes.POINTER(c_int)
    c_uint   = ctypes.c_uint
    c_uint_p = ctypes.POINTER(c_uint)

    n_max = self.width*self.height
    int_arr_t = c_int * n_max
    xs, ys = int_arr_t(), int_arr_t()

    global lib
    n = lib.calculate_fov(self.width, self.height, ctypes.cast(self._flags, c_uint_p), flag, mask, x, y, radius, xs, ys)

    return list(zip(xs[:n], ys[:n]))

#############################
## Load the DLL / .so FILE ##
#############################

def load_dll(dll_file="./libcmap.so"):
  c_int     = ctypes.c_int
  c_int_p   = ctypes.POINTER(c_int)
  c_int_pp  = ctypes.POINTER(ctypes.POINTER(c_int))
  c_uint    = ctypes.c_uint
  c_uint_p  = ctypes.POINTER(c_uint)

  lib = ctypes.cdll.LoadLibrary(dll_file)

  # void calculate_distance_map(
  #   int width, int height, unsigned int *flags, unsigned int flag, unsigned mask,
  #   int *xs, int *ys, int n, 
  #   int *dist_map
  # );
  lib.calculate_distance_map.restype = None
  lib.calculate_distance_map.argtypes = (c_int, c_int, c_uint_p, c_uint, c_uint, c_int_p, c_int_p, c_int, c_int_p)

  # int calculate_fov(
  #   /* input */
  #   int width, int height, unsigned int *flags, unsigned int flag, unsigned int mask,
  #   int x, int y, int radius,
  #   
  #   /* result */
  #   int *xs, int *ys
  # );
  lib.calculate_fov.restype = c_int
  lib.calculate_fov.argtypes = (c_int, c_int, c_uint_p, c_uint, c_uint, c_int, c_int, c_int, c_int_p, c_int_p)

  return lib

lib = load_dll()
