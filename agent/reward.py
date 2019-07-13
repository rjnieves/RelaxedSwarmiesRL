"""Definition of the RewardCenter class.
"""

import numpy as np

# class RewardCenter(object):
#   AT_LARGE_IDX = 0
#   LOCATED_IDX = 1
#   COLLECTED_IDX = 3
#   def __init__(self, at_large_penalty=-1., located_penalty=-0.1):
#     super(RewardCenter, self).__init__()
#     self.penalty_factor = np.array([at_large_penalty, located_penalty, 1.])
  
#   def calculate(self, state_sample):
#     distilled_state = np.array([
#       state_sample[RewardCenter.AT_LARGE_IDX],
#       state_sample[RewardCenter.LOCATED_IDX],
#       state_sample[RewardCenter.COLLECTED_IDX]
#     ])
#     return np.sum(distilled_state * self.penalty_factor)

class RewardCenter(object):
  def __init__(self, swarmie_id_list, emitter, spotting_bonus=0.1, collect_bonus=1.0):
    super(RewardCenter, self).__init__()
    self.spotting_bonus = spotting_bonus
    self.collect_bonus = collect_bonus
    self.swarmie_id_list = swarmie_id_list
    self.reward_map = self._new_reward_map(swarmie_id_list)
    emitter.on_new_cube_spotted(self.new_cube_spotted_by)
    emitter.on_cube_collected(self.cube_collected_by)

  def _new_reward_map(self, swarmie_id_list):
    return dict(zip(swarmie_id_list, [0.,] * len(swarmie_id_list)))
  
  def new_cube_spotted_by(self, cube_loc, swarmie_id):
    self.reward_map[swarmie_id] += self.spotting_bonus
  
  def cube_collected_by(self, swarmie_id):
    self.reward_map[swarmie_id] += self.collect_bonus
  
  def reward_for(self, swarmie_id):
    return self.reward_map[swarmie_id]

  def reset(self):
    self.reward_map = self._new_reward_map(self.swarmie_id_list)

# vim: set ts=2 sw=2 expandtab:
