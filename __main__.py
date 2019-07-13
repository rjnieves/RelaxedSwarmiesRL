"""Entry point for the RelaxedSwarmiesRL application.
"""

import random
import sys
from functools import partial
import numpy as np
from world import Arena, Swarmie
from control import SearchAction, CollectAction
from events import EventEmitter
from agent import StateRepository, DqnAgent, RewardCenter
from agent.policy import EpsilonGreedyPolicy

CUBE_COUNT = 64
ARENA_DIMS = (60, 60,)
NEST_DIMS = (20, 20,)
NEST_AT = (20, 20,)
ACHILLES_IDX = 1
AENEAS_IDX = 2
AJAX_IDX = 3
ACHILLES_START = (2, 2,)
AENEAS_START = (2, 58,)
AJAX_START = (58, 58,)
EPSILON_START = 0.1
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.99
MINIBATCH_SIZE = 32
Q1_TOP_LEFT = (0, 0)
Q1_BOTTOM_RIGHT = (39, 19)
Q2_TOP_LEFT = (40, 0)
Q2_BOTTOM_RIGHT = (59, 39)
Q3_TOP_LEFT = (19, 39)
Q3_BOTTOM_RIGHT = (59, 59)
Q4_TOP_LEFT = (0, 19)
Q4_BOTTOM_RIGHT = (19, 59)
SEARCH_ACTION = 0
COLLECT_ACTION = 1
ACTION_COUNT = 2
MAX_STEPS = int((30 * 60) / 5)
MAX_EPISODES = 100
STATE_COLLECTED_IDX = 3


class SwarmieBundle(object):
  def __init__(self, swarmie_id, start_pos, arena, emitter, state_size, action_size):
    super(SwarmieBundle, self).__init__()
    self.swarmie_id = swarmie_id
    self.start_pos = start_pos
    self.emitter = emitter
    self.entity = Swarmie(swarmie_id, start_pos, arena, emitter)
    self.policy = EpsilonGreedyPolicy(EPSILON_START, EPSILON_MIN, EPSILON_DECAY)
    self.agent = DqnAgent(self.policy, state_size, action_size, MINIBATCH_SIZE)
    self.action_id = None
    self.action_object = None
    self.post_action = None
  
  def clear_action(self, action_done):
    if self.post_action is not None:
      self.post_action()
      self.post_action = None
    if self.action_object is not None:
      if not action_done:
        self.action_object.abandon()
      self.action_object = None
    self.action_id = None
  
  def episode_reset(self, arena):
    self.entity = Swarmie(self.swarmie_id, self.start_pos, arena, self.emitter)
    self.policy = EpsilonGreedyPolicy(EPSILON_START, EPSILON_MIN, EPSILON_DECAY)
    self.agent.policy = self.policy
    self.agent.update_target_model()
    self.clear_action(True)

class SearchActionFactory(object):
  def __init__(self):
    self.quad_collection = [
      SearchAction(None, Q1_TOP_LEFT, Q1_BOTTOM_RIGHT),
      SearchAction(None, Q2_TOP_LEFT, Q2_BOTTOM_RIGHT),
      SearchAction(None, Q3_TOP_LEFT, Q3_BOTTOM_RIGHT),
      SearchAction(None, Q4_TOP_LEFT, Q4_BOTTOM_RIGHT),
    ]
  
  def check_out(self, for_swarmie):
    if not self.quad_collection:
      raise RuntimeError('Ran out of search actions??')
    quad_idx = random.randrange(len(self.quad_collection))
    quad_action = self.quad_collection[quad_idx]
    quad_action.bound_swarmie = for_swarmie
    del self.quad_collection[quad_idx]
    return quad_action, partial(self.check_in, quad_action)

  def check_in(self, the_action):
    the_action.bound_swarmie = None
    self.quad_collection.append(the_action)

def populate_arena(arena):
  for _ in range(CUBE_COUNT):
    placed_cube = False
    while not placed_cube:
      cube_coord = (
        np.random.randint(0, ARENA_DIMS[0]),
        np.random.randint(0, ARENA_DIMS[1])
      )
      if not arena.cell_in_nest(cube_coord):
        arena.drop_april_cube(cube_coord)
        placed_cube = True

def __main__():
  my_emitter = EventEmitter()

  my_arena = Arena(ARENA_DIMS, NEST_DIMS, NEST_AT)

  reward_center = RewardCenter(
    [ACHILLES_IDX, AENEAS_IDX, AJAX_IDX,],
    my_emitter
  )

  state_rep = StateRepository(
    [ACHILLES_IDX, AENEAS_IDX, AJAX_IDX,],
    CUBE_COUNT,
    ARENA_DIMS,
    my_emitter
  )

  search_factory = SearchActionFactory()

  achilles = SwarmieBundle(
    ACHILLES_IDX,
    ACHILLES_START,
    my_arena,
    my_emitter,
    state_rep.state_size,
    ACTION_COUNT
  )

  aeneas = SwarmieBundle(
    AENEAS_IDX,
    AENEAS_START,
    my_arena,
    my_emitter,
    state_rep.state_size,
    ACTION_COUNT
  )

  ajax = SwarmieBundle(
    AJAX_IDX,
    AJAX_START,
    my_arena,
    my_emitter,
    state_rep.state_size,
    ACTION_COUNT
  )

  populate_arena(my_arena)

  episode_idx = 0
  while episode_idx < MAX_EPISODES:
    steps_left = MAX_STEPS
    current_state = state_rep.make_state_vector()
    while steps_left > 0:
      steps_left -= 1
      for a_swarmie in [achilles, aeneas, ajax,]:
        action = a_swarmie.agent.act(current_state)
        if action != a_swarmie.action_id:
          a_swarmie.clear_action(False)
        if a_swarmie.action_id is None:
          a_swarmie.action_id = action
          if action == SEARCH_ACTION:
            a_swarmie.action_object, a_swarmie.post_action = search_factory.check_out(a_swarmie.entity)
          elif action == COLLECT_ACTION:
            a_swarmie.action_object = CollectAction(a_swarmie.entity, state_rep.nearest_cube[a_swarmie.entity.id_number])
            a_swarmie.post_action = None
        if a_swarmie.action_object.update():
          a_swarmie.clear_action(True)
        next_state = state_rep.make_state_vector()
        reward = reward_center.reward_for(a_swarmie.swarmie_id)
        done = (steps_left == 0) or (next_state[STATE_COLLECTED_IDX] >= 1.)
        a_swarmie.agent.remember(current_state, action, reward, next_state, done)
        a_swarmie.agent.learn()
        current_state = next_state
      sys.stdout.write(
        '{:4d}:{:3d}{:3d}{:3d}{:3d}\r'.format(
          steps_left,
          int(current_state[0] * CUBE_COUNT),
          int(current_state[1] * CUBE_COUNT),
          int(current_state[2] * CUBE_COUNT),
          int(current_state[3] * CUBE_COUNT)
        )
      )
      sys.stdout.flush()
      reward_center.reset()
    print '\n{},{},{}'.format(episode_idx + 1, (MAX_STEPS - steps_left), current_state[STATE_COLLECTED_IDX] * CUBE_COUNT)
    my_arena = Arena(ARENA_DIMS, NEST_DIMS, NEST_AT)
    populate_arena(my_arena)
    for a_swarmie in [achilles, aeneas, ajax,]:
      a_swarmie.episode_reset(my_arena)
    state_rep.episode_reset([ACHILLES_IDX, AENEAS_IDX, AJAX_IDX,])
    episode_idx += 1

if __name__ == '__main__':
  __main__()

# vim: set ts=2 sw=2 expandtab:
