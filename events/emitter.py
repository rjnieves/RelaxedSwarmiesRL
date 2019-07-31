"""Definition of the EventEmitter class.
"""

class EventEmitter(object):
  def __init__(self):
    self.cube_added_calls = []
    self.swarmie_loc_calls = []
    self.cube_spotted_calls = []
    self.new_cube_spotted_calls = []
    self.cube_picked_up_calls = []
    self.cube_dropped_calls = []
    self.cube_collected_calls = []
    self.futile_collect_calls = []
    self.activity_log = None
    self.time_keeper = None

  def log_activity(self, activity_log_path, time_keeper):
    self.activity_log = open(activity_log_path, 'w', 1)
    self.time_keeper = time_keeper

  def close_log(self):
    self.activity_log.close()
    self.activity_log = None
    self.time_keeper = None

  def on_cube_added(self, callback):
    if callback not in self.cube_added_calls:
      self.cube_added_calls.append(callback)

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

  def emit_cube_added(self, cube_loc):
    for a_callback in self.cube_added_calls:
      a_callback(cube_loc)
    if self.activity_log:
      self.activity_log.write(
        '{:d},{:d},CUBE,-,{:d},{:d}\n'.format(
          self.time_keeper.episode,
          self.time_keeper.step,
          cube_loc[0],
          cube_loc[1]
        )
      )

  def emit_swarmie_loc(self, swarmie_id, swarmie_loc):
    for a_callback in self.swarmie_loc_calls:
      a_callback(swarmie_id, swarmie_loc)
    if self.activity_log:
      self.activity_log.write(
        '{:d},{:d},POS,{:d},{:d},{:d}\n'.format(
          self.time_keeper.episode,
          self.time_keeper.step,
          swarmie_id,
          swarmie_loc[0],
          swarmie_loc[1]
        )
      )
  
  def emit_cube_spotted(self, cube_loc, swarmie_id):
    for a_callback in self.cube_spotted_calls:
      a_callback(cube_loc, swarmie_id)
    if self.activity_log:
      self.activity_log.write(
        '{:d},{:d},CUBESPOT,{:d},{:d},{:d}\n'.format(
          self.time_keeper.episode,
          self.time_keeper.step,
          swarmie_id,
          cube_loc[0],
          cube_loc[1]
        )
      )
  
  def emit_new_cube_spotted(self, cube_loc, swarmie_id):
    for a_callback in self.new_cube_spotted_calls:
      a_callback(cube_loc, swarmie_id)
    if self.activity_log:
      self.activity_log.write(
        '{:d},{:d},NEWCUBESPOT,{:d},{:d},{:d}\n'.format(
          self.time_keeper.episode,
          self.time_keeper.step,
          swarmie_id,
          cube_loc[0],
          cube_loc[1]
        )
      )

  def emit_cube_picked_up(self, cube_loc, swarmie_id):
    for a_callback in self.cube_picked_up_calls:
      a_callback(cube_loc, swarmie_id)
    if self.activity_log:
      self.activity_log.write(
        '{:d},{:d},PICKUP,{:d},{:d},{:d}\n'.format(
          self.time_keeper.episode,
          self.time_keeper.step,
          swarmie_id,
          cube_loc[0],
          cube_loc[1]
        )
      )

  def emit_cube_dropped(self, swarmie_id):
    for a_callback in self.cube_dropped_calls:
      a_callback(swarmie_id)
    if self.activity_log:
      self.activity_log.write(
        '{:d},{:d},DROP,{:d},-,-\n'.format(
          self.time_keeper.episode,
          self.time_keeper.step,
          swarmie_id
        )
      )

  def emit_cube_collected(self, swarmie_id):
    for a_callback in self.cube_collected_calls:
      a_callback(swarmie_id)
    if self.activity_log:
      self.activity_log.write(
        '{:d},{:d},COLLECT,{:d},-,-\n'.format(
          self.time_keeper.episode,
          self.time_keeper.step,
          swarmie_id  
        )
      )

  def emit_futile_collect_attempt(self, swarmie_id):
    for a_callback in self.futile_collect_calls:
      a_callback(swarmie_id)
    if self.activity_log:
      self.activity_log.write(
        '{:d},{:d},FUTILE,{:d},-,-\n'.format(
          self.time_keeper.episode,
          self.time_keeper.step,
          swarmie_id
        )
      )

# vim: set ts=2 sw=2 expandtab:
