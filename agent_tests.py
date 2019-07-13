import time
import numpy as np
from world import Arena, Swarmie
from control import SearchAction
from events import EventEmitter
from agent import StateRepository

BLOCK_COUNT = 64
ARENA_DIMS = (60, 60,)

my_emitter = EventEmitter()
my_arena = Arena(ARENA_DIMS, (10, 10), (20, 20))
achilles = Swarmie(1, (2, 2), my_arena, my_emitter)
aeneas = Swarmie(2, (2, 58), my_arena, my_emitter)
ajax = Swarmie(3, (58, 58), my_arena, my_emitter)
state_rep = StateRepository([1, 2, 3,], BLOCK_COUNT, ARENA_DIMS, my_emitter)

for _ in range(BLOCK_COUNT):
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
aeneas_search = SearchAction(aeneas, (0, 20), (19, 59))
ajax_search = SearchAction(ajax, (30, 20), (59, 59))

step_count = (20 * 60)
while step_count > 0:
  achilles_search.update()
  aeneas_search.update()
  ajax_search.update()
  time.sleep(0.1)
  step_count -= 1
