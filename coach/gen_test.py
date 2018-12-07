import numpy as np
import random
from genetic.genetic import Genetic

start_array = np.array([-1,1])
pool_size = 10
gen = Genetic(start_array, pool_size=10)

for i in range(10):
    for index in range(pool_size):
        fitness = random.uniform(0, 10)
        gen.set_fitness(index, fitness)
    next = gen.next_gen()
    print("Generation {}".format(i+1))
    print(next)

print("Winner:")
print(gen.fittest())