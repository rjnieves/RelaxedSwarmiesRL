"""Definition of the Arena class.
"""

import numpy as np

class Arena(object):
  def __init__(self, arena_dim, nest_dim, nest_at):
    self.arena_cube_locs = np.zeros(arena_dim, dtype=np.uint8)
    self.arena_swarmie_locs = np.zeros(arena_dim, dtype=np.uint8)
    self.nest_dim = nest_dim
    self.nest_at = nest_at
  
  def swarmie_enters(self, arena_coord):
    if self.arena_swarmie_locs[arena_coord] != 0:
      raise RuntimeError("Swarmie already at that location")
    else:
      self.arena_swarmie_locs[arena_coord] = 1

  def swarmie_leaves(self, arena_coord):
    self.arena_swarmie_locs[arena_coord] = 0

  def cell_in_nest(self, arena_coord):
    nest_br = self.nest_at + np.array(self.nest_dim)
    return (
      (arena_coord[0] >= self.nest_at[0]) and
      (arena_coord[0] <= nest_br[0]) and
      (arena_coord[1] >= self.nest_at[1]) and
      (arena_coord[1] <= nest_br[1])
    )

  def april_cube_at(self, arena_coord):
    return self.arena_cube_locs[arena_coord] >= 1

  def drop_april_cube(self, arena_coord):
    self.arena_cube_locs[arena_coord] += 1

  def pick_up_april_cube(self, arena_coord):
    if self.april_cube_at(arena_coord):
      self.arena_cube_locs[arena_coord] -= 1

# vim: set ts=2 sw=2 expandtab:
