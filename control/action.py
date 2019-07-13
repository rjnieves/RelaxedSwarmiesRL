"""Defines the abstract Action class.
"""

class Action(object):
  def __init__(self, swarmie):
    self.bound_swarmie = swarmie
  
  def update(self):
    raise NotImplementedError("Action.update()")

  def abandon(self):
    raise NotImplementedError("Action.abandon()")

# vim: set ts=2 sw=2 expandtab:
