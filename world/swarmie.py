"""Definition of the Swarmie class.
"""

import numpy as np

class Swarmie(object):
  NORTH = 'N'
  SOUTH = 'S'
  EAST = 'E'
  WEST = 'W'
  def __init__(self, id_number, start_pos, arena, emitter):
    self.id_number = id_number
    self.arena = arena
    self.position = np.array(start_pos, dtype=np.uint8)
    self.arena.swarmie_enters(tuple(self.position))
    self.carrying = False
    self.emitter = emitter
    self.emitter.emit_swarmie_loc(self.id_number, self.position)
  
  def move(self, direction):
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
    except Exception as ex:
      print 'Could not move Swarmie ({:d}) to {}: {}'.format(
        self.id_number,
        new_pos,
        ex.message
      )
      return
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
    self.emitter.emit_cube_dropped(self.id_number)
    if not self.arena.cell_in_nest(tuple(self.position)):
      self.emitter.emit_cube_spotted(self.position, self.id_number)
    else:
      self.emitter.emit_cube_collected(self.id_number)

# vim: set ts=2 sw=2 expandtab:
