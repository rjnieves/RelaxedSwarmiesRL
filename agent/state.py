"""Definition of the StateRepository class.
"""

import math
import numpy as np
from scipy.spatial import distance

class StateRepository(object):
  def __init__(self, swarmie_id_list, cube_count, arena_dims, emitter):
    self.cube_count = cube_count
    self.arena_dims = arena_dims
    self.episode_reset(swarmie_id_list)
    self.emitter = emitter
    self.emitter.on_swarmie_loc(self.swarmie_loc_update)
    self.emitter.on_cube_spotted(self.cube_spotted)
    self.emitter.on_cube_picked_up(self.cube_picked_up_by)
    self.emitter.on_cube_collected(self.cube_collected)
    self.emitter.on_cube_dropped(self.cube_dropped_by)

  @property
  def state_size(self):
    return len(self.cube_counts) + (len(self.swarmie_pos) * 2)

  def episode_reset(self, swarmie_id_list):
    self.spotted_cubes = set()
    self.swarmie_state = dict(zip(swarmie_id_list, [False,] * len(swarmie_id_list)))
    self.cube_counts = {
      'at-large': self.cube_count,
      'located': 0,
      'in-transit': 0,
      'collected': 0
    }
    self.swarmie_pos = dict(zip(swarmie_id_list, [None, ] * len(swarmie_id_list)))
    self.dist_meas = dict(zip(swarmie_id_list, [-1., ] * len(swarmie_id_list)))
    self.nearest_cube = dict(zip(swarmie_id_list, [None, ] * len(swarmie_id_list)))

  def _reeval_block_counts(self):
    at_large_total = self.cube_count
    self.cube_counts['in-transit'] = self.swarmie_state.values().count(True)
    at_large_total -= self.cube_counts['in-transit']
    self.cube_counts['located'] = len(self.spotted_cubes)
    at_large_total -= self.cube_counts['located']
    at_large_total -= self.cube_counts['collected']
    self.cube_counts['at-large'] = at_large_total

  def _reeval_distances(self):
    for a_swarmie_id in self.swarmie_pos.keys():
      closest = float('+inf')
      cube = None
      swarmie_pos = self.swarmie_pos[a_swarmie_id]
      if swarmie_pos is not None:
        for a_cube_loc in self.spotted_cubes:
          new_dist = distance.cityblock(
            np.array(a_cube_loc, dtype=int),
            np.array(swarmie_pos, dtype=int)
          )
          if new_dist < closest:
            closest = new_dist
            cube = a_cube_loc
      self.dist_meas[a_swarmie_id] = closest if not math.isinf(closest) else -1.
      self.nearest_cube[a_swarmie_id] = cube

  def make_state_vector(self):
    result = np.zeros(self.state_size)
    self._reeval_block_counts()
    self._reeval_distances()
    idx = 0
    for a_cube_cat in ['at-large', 'located', 'in-transit', 'collected', ]:
      result[idx] = float(self.cube_counts[a_cube_cat]) / float(self.cube_count)
      idx += 1
    for a_swarmie_id in sorted(self.swarmie_state.keys()):
      result[idx] = 1. if self.swarmie_state[a_swarmie_id] else 0.
      idx += 1
    for a_swarmie_id in sorted(self.dist_meas.keys()):
      result[idx] = float(self.dist_meas[a_swarmie_id]) / float(np.sum(self.arena_dims))
      idx += 1
    return result

  def swarmie_loc_update(self, swarmie_id, swarmie_loc):
    self.swarmie_pos[swarmie_id] = tuple(swarmie_loc)
  
  def swarmie_is_carrying(self, swarmie_id):
    return self.swarmie_state[swarmie_id]

  def cube_spotted(self, cube_loc, swarmie_id):
    cube_loc = tuple(cube_loc)
    if cube_loc not in self.spotted_cubes:
      self.emitter.emit_new_cube_spotted(cube_loc, swarmie_id)
    self.spotted_cubes.add(cube_loc)
  
  def cube_picked_up_by(self, cube_loc, swarmie_id):
    self.spotted_cubes.remove(tuple(cube_loc))
    self.swarmie_state[swarmie_id] = True

  def cube_dropped_by(self, swarmie_id):
    self.swarmie_state[swarmie_id] = False

  def cube_collected(self, swarmie_id):
    self.swarmie_state[swarmie_id] = False
    self.cube_counts['collected'] += 1

# vim: set ts=2 sw=2 expandtab:
