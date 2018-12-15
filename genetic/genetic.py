import numpy as np

class Genetic:
    """
    A class that takes care of the generation of new genetically encoded generations.
    Each generations is a numpy array of two dimensions.
    First dimension: each gene in the generation
    Second dimension: internal component of each gene
    (it should be clear by now that my understanding of genes is lousy at best)
    """
    def __init__(self, start_array, pool_size=10, mutation=0.1, mating_pool_size=4):
        self.start_array = start_array
        self.length = start_array.shape[0]
        self.pool_size = pool_size
        self.mating_pool_size = mating_pool_size
        self.mutation = mutation
        self.generations = []
        self.fitness = []
    
    def set_fitness(self, index, value):
        """ Set the fitness of a gene in the current generation. """
        
        self.fitness[-1][index] = value
    
    def next_gen(self):
        """ Generate the next generation and return it. """
        if not self.generations:
            gen = self._generate_start_pool()
        else:
            gen = self._generate_next_gen()
        
        self.generations.append(gen)
        self.fitness.append(np.zeros(self.pool_size))
        return self.generations[-1]
    
    def fittest(self):
        if not self.generations:
            return None
        fit = self.fitness[-1]
        max_fitness_idx = np.where(fit == np.max(fit))
        max_fitness_idx = max_fitness_idx[0][0]
        return self.generations[-1][max_fitness_idx]
    
    def cur_gen(self):
        """
        Returns all generations, oldest generations first.
        """
        
        return self.generations[-1]
    
    def all_gens(self):
        """
        Returns all generations, oldest generations first.
        """
        
        return self.generations
    
    def _generate_start_pool(self):
        dimensions = (self.pool_size, self.length)
        mutation   = np.random.uniform(-self.mutation, self.mutation, dimensions)
        return mutation + self.start_array
    
    def _generate_next_gen(self):
        """
        Generate the next generation by performing the genetic evolution steps:
        1. Selection
        2. Mating
        3. Mutation
        """
        
        parents           = self._generate_mating_pool()
        offspring         = self._generate_offspring(parents)
        mutated_offspring = self._mutate(offspring)
        
        gen = np.zeros((self.pool_size, self.length))
        gen[0:self.mating_pool_size, :] = parents
        gen[self.mating_pool_size:, :]       = mutated_offspring
        return gen
    
    def _generate_mating_pool(self):
        """
        Generates the mating pool by selecting the parents with highest fitness.
        """
        print("Generating mating pool...")
        fit = self.fitness[-1]
        cur_gen = self.generations[-1]
        
        parents = np.empty((self.mating_pool_size, self.length))
        for parent_num in range(self.mating_pool_size):
            max_fitness_idx = np.where(fit == np.max(fit))
            max_fitness_idx = max_fitness_idx[0][0]
            parents[parent_num, :] = cur_gen[max_fitness_idx, :]
            fit[max_fitness_idx] = -99999999999 # destroy the fitness of this specific parent so it is not selected again
            
        return parents
    
    def _generate_offspring(self, parents):
        """
        In this variant the parents are carried over to the next generation
        """
        print('Mating...')
        n_offspring = self.pool_size - self.mating_pool_size
        offspring = np.empty((n_offspring, self.length))
        crossover_point = np.uint8(self.length/2)
    
        for k in range(n_offspring):
            # Index of the first parent to mate.
            parent1_idx = k%self.mating_pool_size
            # Index of the second parent to mate.
            parent2_idx = (k+1)%self.mating_pool_size
            # The new offspring will have its first half of its genes taken from the first parent.
            offspring[k, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
            # The new offspring will have its second half of its genes taken from the second parent.
            offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]
            
        return offspring
    
    @staticmethod
    def _mutate(offspring):
        """
        Mutates the offspring by adding a randomly calculated value to each component.
        """
        
        print('Mutating offspring...')
        mutation = np.random.uniform(-0.5, 0.5, offspring.shape)
        return offspring + mutation
