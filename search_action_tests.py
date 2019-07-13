import time
import numpy as np
from world import Arena, Swarmie
from control import SearchAction
from events import EventEmitter

def swarmie_loc_update(swarmie_id, swarmie_loc):
  print 'search_action_tests: Swarmie ({:d}) at {}'.format(swarmie_id, swarmie_loc)

def cube_spotted(cube_loc):
  print 'search_action_tests: Cube spotted at {}'.format(cube_loc)

def cube_picked_up_by(cube_loc, swarmie_id):
  print 'search_action_tests: Cube picked up at {} by {}'.format(cube_loc, swarmie_id)

def cube_dropped_by(swarmie_id):
  print 'search_action_tests: Cube dropped by {}'.format(swarmie_id)

def cube_collected(swarmie_id):
  print 'search_action_tests: Cube collected by {}!'.format(swarmie_id)

my_emitter = EventEmitter()
my_emitter.on_swarmie_loc(swarmie_loc_update)
my_emitter.on_cube_spotted(cube_spotted)
my_emitter.on_cube_picked_up(cube_picked_up_by)
my_emitter.on_cube_dropped(cube_dropped_by)
my_emitter.on_cube_collected(cube_collected)
my_arena = Arena((60, 60), (10, 10), (20, 20))
achilles = Swarmie(1, (2, 2), my_arena, my_emitter)

for _ in range(32):
  placed_cube = False
  while not placed_cube:
    cube_coord = (
      np.random.randint(0, 60),
      np.random.randint(0, 60)
    )
    if not my_arena.cell_in_nest(cube_coord):
      my_arena.drop_april_cube(cube_coord)
      placed_cube = True

achilles_search = SearchAction(achilles, (0, 0), (59, 19))

step_count = 240
while step_count > 0:
  achilles_search.update()
  time.sleep(0.1)
  step_count -= 1
