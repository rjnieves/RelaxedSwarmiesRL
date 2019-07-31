"""Definition of the EventEmitter class.
"""

class EventEmitter(object):
  def __init__(self):
    self.swarmie_loc_calls = []
    self.cube_spotted_calls = []
    self.new_cube_spotted_calls = []
    self.cube_picked_up_calls = []
    self.cube_dropped_calls = []
    self.cube_collected_calls = []
    self.futile_collect_calls = []
  
  def on_swarmie_loc(self, callback):
    if callback not in self.swarmie_loc_calls:
      self.swarmie_loc_calls.append(callback)
  
  def on_cube_spotted(self, callback):
    if callback not in self.cube_spotted_calls:
      self.cube_spotted_calls.append(callback)
  
  def on_new_cube_spotted(self, callback):
    if callback not in self.new_cube_spotted_calls:
      self.new_cube_spotted_calls.append(callback)

  def on_cube_picked_up(self, callback):
    if callback not in self.cube_picked_up_calls:
      self.cube_picked_up_calls.append(callback)

  def on_cube_dropped(self, callback):
    if callback not in self.cube_dropped_calls:
      self.cube_dropped_calls.append(callback)

  def on_cube_collected(self, callback):
    if callback not in self.cube_collected_calls:
      self.cube_collected_calls.append(callback)
  
  def on_futile_collect_attempt(self, callback):
    if callback not in self.futile_collect_calls:
      self.futile_collect_calls.append(callback)

  def emit_swarmie_loc(self, swarmie_id, swarmie_loc):
    for a_callback in self.swarmie_loc_calls:
      a_callback(swarmie_id, swarmie_loc)
  
  def emit_cube_spotted(self, cube_loc, swarmie_id):
    for a_callback in self.cube_spotted_calls:
      a_callback(cube_loc, swarmie_id)
  
  def emit_new_cube_spotted(self, cube_loc, swarmie_id):
    for a_callback in self.new_cube_spotted_calls:
      a_callback(cube_loc, swarmie_id)

  def emit_cube_picked_up(self, cube_loc, swarmie_id):
    for a_callback in self.cube_picked_up_calls:
      a_callback(cube_loc, swarmie_id)

  def emit_cube_dropped(self, swarmie_id):
    for a_callback in self.cube_dropped_calls:
      a_callback(swarmie_id)

  def emit_cube_collected(self, swarmie_id):
    for a_callback in self.cube_collected_calls:
      a_callback(swarmie_id)

  def emit_futile_collect_attempt(self, swarmie_id):
    for a_callback in self.futile_collect_calls:
      a_callback(swarmie_id)

# vim: set ts=2 sw=2 expandtab:
