"""Definition of the CollectAction class.
"""

import numpy as np
from .action import Action
from world import Swarmie

class AbortSequence(Exception):
  def __init__(self, reason):
    super(AbortSequence, self).__init__(
      'Collect sequence aborted: {:s}'.format(reason)
    )

class BaseCollectStep(object):
  def __init__(self, swarmie, block_pos):
    super(BaseCollectStep, self).__init__()
    self.bound_swarmie = swarmie
    self.block_pos = block_pos
  
  def step(self):
    raise NotImplementedError("BaseCollectStep.step()")
  
  def _progress_toward(self, target_pos):
    swarmie_pos = self.bound_swarmie.position
    ew_movement = None
    ns_movement = None
    if swarmie_pos[0] != target_pos[0]:
      ew_movement = Swarmie.EAST if swarmie_pos[0] < target_pos[0] else Swarmie.WEST
    if swarmie_pos[1] != target_pos[1]:
      ns_movement = Swarmie.SOUTH if swarmie_pos[1] < target_pos[1] else Swarmie.NORTH
    
    if ew_movement is not None:
      # Attempt move E-W and, if not possible, attempt N-S
      try:
        self.bound_swarmie.move(ew_movement)
      except:
        self.bound_swarmie.move(ns_movement)
    elif ns_movement is not None:
      # Attempt move N-S and, if not possible, wait
      self.bound_swarmie.move(ns_movement)

class NavigateToBlockStep(BaseCollectStep):
  def __init__(self, swarmie, block_pos):
    super(NavigateToBlockStep, self).__init__(swarmie, block_pos)

  def step(self):
    if self.block_pos is None:
      raise AbortSequence(
        'Cannot navigate to non-existent block'
      )
    self._progress_toward(self.block_pos)
    return tuple(self.bound_swarmie.position) == self.block_pos

class PickUpBlockStep(BaseCollectStep):
  def __init__(self, swarmie, block_pos):
    super(PickUpBlockStep, self).__init__(swarmie, block_pos)

  def step(self):
    self.bound_swarmie.pick_up_cube()
    if not self.bound_swarmie.carrying:
      raise AbortSequence(
        'Could not pick up April Cube at {}'.format(
          self.bound_swarmie.position
        )
      )
    return True

class NavigateToNestStep(BaseCollectStep):
  def __init__(self, swarmie, block_pos):
    super(NavigateToNestStep, self).__init__(swarmie, block_pos)
    self.nest_center = np.array(swarmie.arena.nest_at, dtype=np.int16)
    self.nest_center += np.array(swarmie.arena.nest_dim, dtype=np.int16) / 2

  def step(self):
    self._progress_toward(self.nest_center)
    return self.bound_swarmie.arena.cell_in_nest(
      tuple(self.bound_swarmie.position)
    )

class DropOffBlockStep(BaseCollectStep):
  def __init__(self, swarmie, block_pos):
    super(DropOffBlockStep, self).__init__(swarmie, block_pos)

  def step(self):
    self.bound_swarmie.drop_off_cube()
    return True

class CollectAction(Action):
  def __init__(self, swarmie, block_coord):
    super(CollectAction, self).__init__(swarmie)
    self.steps = [
      NavigateToBlockStep(swarmie, block_coord),
      PickUpBlockStep(swarmie, block_coord),
      NavigateToNestStep(swarmie, block_coord),
      DropOffBlockStep(swarmie, block_coord)
    ]
    self.step_idx = 0 if not swarmie.carrying else 2
  
  def update(self):
    result = False
    try:
      if self.steps[self.step_idx].step():
        self.step_idx += 1
      result = self.step_idx >= len(self.steps)
    except AbortSequence:
      result = True
    return result

  def abandon(self):
    self.bound_swarmie.drop_off_cube()

# vim: set ts=2 sw=2 expandtab:
