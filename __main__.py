"""Entry point for the RelaxedSwarmiesRL application.
"""

import random
import sys
import os
from functools import partial
import numpy as np
from world import Arena, Swarmie
from control import SearchAction, CollectAction
from events import EventEmitter
from agent import StateRepository, DqnAgent, RewardCenter
from agent.policy import EpsilonGreedyPolicy

CUBE_COUNT = 64
ARENA_DIMS = (30, 30,)
NEST_DIMS = (2, 2,)
NEST_TL = (13, 13,)
NEST_BR = (NEST_TL[0] + NEST_DIMS[0], NEST_TL[1] + NEST_DIMS[1])
ACHILLES_IDX = 0
AENEAS_IDX = 1
AJAX_IDX = 2
ACHILLES_START = (11, 15,)
AENEAS_START = (15, 18,)
AJAX_START = (18, 15,)
EPSILON_START = 0.1
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.99
MINIBATCH_SIZE = 32
Q1_TOP_LEFT = (0, 0)
Q1_BOTTOM_RIGHT = (NEST_BR[0], NEST_TL[0] - 1)
Q2_TOP_LEFT = (NEST_BR[0] + 1, 0)
Q2_BOTTOM_RIGHT = (ARENA_DIMS[0] - 1, NEST_BR[1])
Q3_TOP_LEFT = (NEST_TL[0], NEST_BR[1] + 1)
Q3_BOTTOM_RIGHT = (ARENA_DIMS[0] - 1, ARENA_DIMS[1] - 1)
Q4_TOP_LEFT = (0, NEST_TL[1])
Q4_BOTTOM_RIGHT = (NEST_TL[0] - 1, ARENA_DIMS[1] - 1)
SEARCH_ACTION = 0
COLLECT_ACTION = 1
ACTION_STRINGS = [
  'SEARCH',
  'COLLECT',
]
ACTION_COUNT = 2
MAX_STEPS = int((30 * 60) / 2)
MAX_EPISODES = 100
STATE_COLLECTED_IDX = 3


class SwarmieBundle(object):
  SWARMIE_NAMES = {
    ACHILLES_IDX: 'achilles',
    AENEAS_IDX: 'aeneas',
    AJAX_IDX: 'ajax',
  }

  def __init__(self, swarmie_id, start_pos, arena, emitter, state_size, action_size):
    super(SwarmieBundle, self).__init__()
    self.swarmie_id = swarmie_id
    self.start_pos = start_pos
    self.emitter = emitter
    self.entity = Swarmie(swarmie_id, start_pos, arena, emitter)
    self.policy = EpsilonGreedyPolicy(EPSILON_START, EPSILON_MIN, EPSILON_DECAY)
    self.agent = DqnAgent(
      self.policy,
      state_size,
      action_size,
      MINIBATCH_SIZE,
      os.path.join(
        os.getcwd(),
        '{}_model.h5'.format(SwarmieBundle.SWARMIE_NAMES[self.swarmie_id])
      )
    )
    self.action_id = None
    self.action_object = None
    self.post_action = None
  
  @property
  def swarmie_name(self):
    return SwarmieBundle.SWARMIE_NAMES[self.swarmie_id]

  @property
  def action_string(self):
    if self.action_id is not None:
      return ACTION_STRINGS[self.action_id]
    else:
      return 'None'

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

def populate_arena(arena, emitter):
  for _ in range(CUBE_COUNT):
    placed_cube = False
    while not placed_cube:
      cube_coord = (
        np.random.randint(0, ARENA_DIMS[0]),
        np.random.randint(0, ARENA_DIMS[1])
      )
      if not arena.cell_in_nest(cube_coord):
        arena.drop_april_cube(cube_coord)
        emitter.emit_cube_added(cube_coord)
        placed_cube = True

class TimeKeeper(object):
  def __init__(self, steps_per_episode):
    self.steps_per_episode = steps_per_episode
    self.episode = 0
    self.step = 0
  
  @property
  def episode_time_exhausted(self):
    return self.step == (self.steps_per_episode - 1)

def __main__():
  my_emitter = EventEmitter()
  time_keeper = TimeKeeper(steps_per_episode=MAX_STEPS)
  my_emitter.log_activity('./activity_log.csv', time_keeper)

  my_arena = Arena(ARENA_DIMS, NEST_DIMS, NEST_TL)

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

  populate_arena(my_arena, my_emitter)

  while time_keeper.episode < MAX_EPISODES:
    current_state = state_rep.make_state_vector()
    while time_keeper.step < MAX_STEPS:
      sys.stderr.write(
        '{:4d}:{:3d}{:3d}{:3d}{:3d} {:8s}{:8s}{:8s}     \r'.format(
          MAX_STEPS - time_keeper.step,
          int(current_state[0] * CUBE_COUNT),
          int(current_state[1] * CUBE_COUNT),
          int(current_state[2] * CUBE_COUNT),
          int(current_state[3] * CUBE_COUNT),
          achilles.action_string,
          aeneas.action_string,
          ajax.action_string
        )
      )
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
          else:
            raise RuntimeError('{} agent yielded unknown action {}'.format(a_swarmie.swarmie_name, action))
        if a_swarmie.action_object.update():
          a_swarmie.clear_action(True)
        next_state = state_rep.make_state_vector()
        if action == SEARCH_ACTION and state_rep.swarmie_is_carrying(a_swarmie.swarmie_id):
          raise RuntimeError('{} is searching AND carrying??? NO'.format(a_swarmie.swarmie_name))
        reward = reward_center.reward_for(a_swarmie.swarmie_id)
        done = time_keeper.episode_time_exhausted or (next_state[STATE_COLLECTED_IDX] >= 1.)
        a_swarmie.agent.remember(current_state, action, reward, next_state, done)
        a_swarmie.agent.learn()
        current_state = next_state
      time_keeper.step += 1
      sys.stderr.flush()
      reward_center.reset()
    sys.stderr.write('\n')
    sys.stdout.write(
      '{},{},{}\n'.format(
        time_keeper.episode,
        time_keeper.step,
        int(current_state[STATE_COLLECTED_IDX] * CUBE_COUNT)
      )
    )
    sys.stdout.flush()
    my_arena = Arena(ARENA_DIMS, NEST_DIMS, NEST_TL)
    time_keeper.episode += 1
    time_keeper.step = 0
    populate_arena(my_arena, my_emitter)
    for a_swarmie in [achilles, aeneas, ajax,]:
      a_swarmie.episode_reset(my_arena)
    state_rep.episode_reset([ACHILLES_IDX, AENEAS_IDX, AJAX_IDX,])
  my_emitter.close_log()

if __name__ == '__main__':
  __main__()

# vim: set ts=2 sw=2 expandtab:
