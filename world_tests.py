import numpy as np
from world import Arena, Swarmie
from events import EventEmitter

my_emitter = EventEmitter()
my_arena = Arena((60, 60), (10, 10), (20, 20))
achilles = Swarmie(1, (2, 2), my_arena, my_emitter)
aeneas = Swarmie(2, (58, 2), my_arena, my_emitter)

my_arena.drop_april_cube((3, 2))

achilles.move(Swarmie.EAST)
achilles.pick_up_cube()
achilles.move(Swarmie.EAST)
achilles.move(Swarmie.EAST)
achilles.drop_off_cube()
achilles.pick_up_cube()
for _ in range(17):
  achilles.move(Swarmie.EAST)
for _ in range(20):
  achilles.move(Swarmie.SOUTH)
achilles.drop_off_cube()
