"""Defines the SearchAction class.
"""

import numpy as np
from .action import Action
from world import Swarmie

class SearchAction(Action):
  def __init__(self, swarmie, zone_tl, zone_br):
    super(SearchAction, self).__init__(swarmie)
    self.axis_dir = np.array([1, 1])
    self.zone_tl = zone_tl
    self.zone_br = zone_br
  
  def update(self):
    swarmie_pos = self.bound_swarmie.position
    direction = None
    if not self._position_in_zone(swarmie_pos):
      if swarmie_pos[0] < self.zone_tl[0]:
        direction = Swarmie.EAST
      elif swarmie_pos[0] > self.zone_tl[0]:
        direction = Swarmie.WEST
      elif swarmie_pos[1] < self.zone_tl[1]:
        direction = Swarmie.SOUTH
      elif swarmie_pos[1] > self.zone_tl[1]:
        direction = Swarmie.NORTH
    else:
      candidate_pos = np.copy(swarmie_pos)
      candidate_pos[0] += self.axis_dir[0]
      if self._position_in_zone(candidate_pos):
        direction = Swarmie.EAST if self.axis_dir[0] > 0 else Swarmie.WEST
      else:
        self.axis_dir[0] *= -1
        candidate_pos = np.copy(swarmie_pos)
        candidate_pos[1] += self.axis_dir[1]
        if self._position_in_zone(candidate_pos):
          direction = Swarmie.SOUTH if self.axis_dir[1] > 0 else Swarmie.NORTH
        else:
          self.axis_dir[1] *= -1
    if direction is not None:
      self.bound_swarmie.move(direction)

  def abandon(self):
    pass
  
  def _position_in_zone(self, the_pos):
    return (
      the_pos[0] >= self.zone_tl[0] and
      the_pos[0] <= self.zone_br[0] and
      the_pos[1] >= self.zone_tl[1] and
      the_pos[1] <= self.zone_br[1]
    )

# vim: set ts=2 sw=2 expandtab:
