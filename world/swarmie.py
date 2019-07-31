"""Definition of the Swarmie class.
"""

import sys
import numpy as np
from . import IllegalMoveError

class Swarmie(object):
  NORTH = 'N'
  SOUTH = 'S'
  EAST = 'E'
  WEST = 'W'
  RIGHT_OF = {
    NORTH: EAST,
    EAST: SOUTH,
    SOUTH: WEST,
    WEST: NORTH
  }
  def __init__(self, id_number, start_pos, arena, emitter):
    self.id_number = id_number
    self.arena = arena
    self.position = np.array(start_pos, dtype=np.int16)
    self.arena.swarmie_enters(tuple(self.position))
    self.carrying = False
    self.emitter = emitter
    self.emitter.emit_swarmie_loc(self.id_number, self.position)
  
  def move(self, direction):
    new_pos = None
    while new_pos is None:
      new_pos = np.copy(self.position)
      if direction == Swarmie.NORTH:
        new_pos[1] -= 1
      elif direction == Swarmie.SOUTH:
        new_pos[1] += 1
      elif direction == Swarmie.EAST:
        new_pos[0] += 1
      elif direction == Swarmie.WEST:
        new_pos[0] -= 1
      else:
        raise RuntimeError(
          'Unknown direction for Swarmie ({:d}): {}'.format(
            self.id_number,
            direction
          )
        )
      try:
        self.arena.swarmie_enters(tuple(new_pos))
        self.arena.swarmie_leaves(tuple(self.position))
      except IllegalMoveError:
        # De-conflict by always attempting to turn right
        direction = Swarmie.RIGHT_OF[direction]
        new_pos = None
    self.position = new_pos
    self.emitter.emit_swarmie_loc(self.id_number, self.position)
    pos_tuple = tuple(self.position)
    if self.arena.april_cube_at(pos_tuple) and not self.arena.cell_in_nest(pos_tuple):
      self.emitter.emit_cube_spotted(pos_tuple, self.id_number)


  def pick_up_cube(self):
    if self.carrying:
      return
    if self.arena.april_cube_at(tuple(self.position)):
      self.arena.pick_up_april_cube(tuple(self.position))
      self.carrying = True
      self.emitter.emit_cube_picked_up(self.position, self.id_number)
  
  def drop_off_cube(self):
    if not self.carrying:
      return
    self.arena.drop_april_cube(tuple(self.position))
    self.carrying = False
    if not self.arena.cell_in_nest(tuple(self.position)):
      self.emitter.emit_cube_dropped(self.id_number)
      self.emitter.emit_cube_spotted(self.position, self.id_number)
    else:
      self.emitter.emit_cube_collected(self.id_number)

  def futile_collect_attempt(self):
    self.emitter.emit_futile_collect_attempt(self.id_number)

# vim: set ts=2 sw=2 expandtab:
