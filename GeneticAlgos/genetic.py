import numpy as np

# https://towardsdatascience.com/genetic-algorithm-implementation-in-python-5ab67bb124a6
# not pretty but works

def fitness(array):
    return array.sum(axis=1)

num_generations = 1000
size = 2
pool_size = 8
# Initialization
#gen0 = np.array([0,-1,0,0,0,1,0,1,-1,0])
gen0 = np.array([1,-1])
mutation = np.random.uniform(-1, 1, (pool_size, size))
gen1 = mutation + gen0


for generation in range(num_generations):
    print('----------------------')
    print('     GENERATION {}'.format(generation))
    print('----------------------')
    # Evaluation
    print('Evaluating fitness...')
    fit = fitness(gen1)
    print(fit)

    print('Creating mating pool...')
    num_parents = 4
    # Mating pool
    parents = np.empty((num_parents, size))
    for parent_num in range(num_parents):
        max_fitness_idx = np.where(fit == np.max(fit))
        max_fitness_idx = max_fitness_idx[0][0]
        parents[parent_num, :] = gen1[max_fitness_idx, :]
        fit[max_fitness_idx] = -99999999999
    print(parents)
    
    # Mating (crossover);
    # in this variant the parents are carried over to the next generation
    print('Mating...')
    offspring_size = (pool_size-num_parents, size)
    offspring = np.empty(offspring_size)
    crossover_point = np.uint8(size/2)

    for k in range(pool_size-num_parents):
        # Index of the first parent to mate.
        parent1_idx = k%parents.shape[0]
        # Index of the second parent to mate.
        parent2_idx = (k+1)%parents.shape[0]
        # The new offspring will have its first half of its genes taken from the first parent.
        offspring[k, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
        # The new offspring will have its second half of its genes taken from the second parent.
        offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]
    print(offspring)

    # Mutation
    print('Mutating offspring...')
    mutation = np.random.uniform(-0.5, 0.5, (pool_size-num_parents,size))
    offspring = offspring + mutation
    print(offspring)
        
    
    # Creating the new population based on the parents and offspring.
    print('Creating new population...')
    gen1[0:num_parents, :] = parents
    gen1[num_parents:, :] = offspring
    print(gen1)


print('Final winner:')
fit = fitness(gen1)
max_fitness_idx = np.where(fit == np.max(fit))
max_fitness_idx = max_fitness_idx[0][0]
print(gen1[max_fitness_idx])










