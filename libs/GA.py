import random
import math

def evolve_perfection(seed,
                      cost,
                      mutate,
                      reproduce,
                      mutation_rate=0.8,
                      pop_size=10,
                      top_k=3,
                      max_repeat=100,
                      max_iter=16):
    """ Performs General Classical Genetic Algorithm, until either max_iter is
        reached, the lowest cost in the generation becomes 0 or the lowest cost
        has remained unchanged for 100 generations

    Args:
        seed: Agent(Any)
            the original agent that will be mutated to create the rest of the 
            poulation
        cost: lambda Agent: Agent
            method that receives an agent and returns the cost of the agent
        mutate: lambda Agent: Agent
            method that receives an agent and reutrns a mutation of that agent
        reproduce: lambda Agent, Agent: Agent
            method that receives a father and mother agent and returns a child,
            which is a combination of the parents
        mutation_rate: float
            directly after reproduction, this is the probability that the child
            will be mutated
        pop_size: int
            the size of the population throughout the algorithm
        top_k: int
            this represents what number of the lowest cost agents will be
            kept and used to create the next generation.
        max_repeat: int
            if the lowest cost has remained the same for this number of 
            iterations, then the training is brought to a halt.
        max_iter: int
            the maximum number of iterations before the training is brought to
            a halt.

    Returns:
        agent2cost: dict<Agent, float>
            mapping between each agent in the final population and their costs
        iterations: int
            the nunber of iterations it took to complete the algorithm
    """
    # create initial population
    population = [
        mutate(seed)
        for _ in range(pop_size)
    ]
    all_time_best = math.inf
    repeat = 0 # the amount of times all_time_best has remained unchanged
    top_k = max(top_k, 2)
    iterations = 0
    # run simulation
    while True:
        # sort population by cost
        agent2cost = { agent: cost(agent) for agent in population }
        population = sorted(agent2cost, key=agent2cost.get)
        
        lowest_cost = population[0]

        # check if lowest_cost has improved
        if lowest_cost < all_time_best:
            all_time_best = lowest_cost
            repeat = 0
        else:
            # halt if lowest_cost is 0 or has been low for max_repeat
            repeat += 1
            if lowest_cost == 0 or repeat >= max_repeat:
                return agent2cost, iterations
        # halt if reached max_iter
        iterations += 1
        if iterations >= max_iter:
            return agent2cost, iterations
        # cull population
        population = population[:top_k]
        # create the rest of the population from the top_k
        top_agents = population.copy()
        for _ in range(top_k, pop_size):
            mother, father = random.sample(top_agents, 2)
            # create child
            child = reproduce(mother, father)
            # mutate with 80% probability
            if random.random() < mutation_rate:
                child = mutate(child)
            population.append(child)


def evolve(population,
           cost,
           mutate,
           reproduce,
           mutation_rate=0.8,
           reverse=False,
           population_cost=False,
           pop_size=None,
           top_k=3,
           generations=16):
    """ Performs General Classical Genetic Algorithm, evolving for a certain
        number of generations

    Note that this method can be called using the keys() of the return type.
    Thus, one can continuously call this method and see the improvement in the
    population.

    Args:
        population: list<Agent(Any)>
            the population to evolve.
        cost: lambda Agent: Agent
            method that receives an agent and returns the cost of the agent
        mutate: lambda Agent: Agent
            method that receives an agent and reutrns a mutation of that agent
        reproduce: lambda Agent, Agent: Agent
            method that receives a father and mother agent and returns a child,
            which is a combination of the parents
        mutation_rate: float
            directly after reproduction, this is the probability that the child
            will be mutated
        reverse: bool,
            Optional; if True, then the cost function becomes a fitness
            function, meaning that the algorithm will attempt to maximize the
            returned value instead of minimizing it. Defaults to False
        population_cost: bool
            Optional; if True, then the population will be fed to the cost
            function to retrieve the total cost of the population instead of 
            each individual agent in the population
        pop_size: int
            Optional; if given, then the size population will be made to match
            pop_size. 
            If the given pop_size is greater than the size of the given 
            population, then the population will be filled up with mutations of 
            the original members of the population until the size of the 
            population matches pop_size.
            If the given pop_size is less than the size of the population, then
            a sample of original population (equal to the given pop_size) will
            be kept while the others are cast aside
        top_k: int
            this represents what number of the lowest cost agents will be
            kept and used to create the next generation.
        generations: int
            the number of iterations to evolve the given population before
            returning the new population

    Returns:
        agent2cost: dict<Agent, float>
            mapping between each agent in the final population and their costs
    """
    if pop_size == None:
        pop_size = len(population)
    else:
        while pop_size > len(population):
            mutated = mutate(random.choice(population))
            population.append(mutated)
        if pop_size < len(population):
            population = population[:pop_size]
    top_k = max(top_k, 2)
    generation = 0
    # run simulation
    while True:
        print("generation =", generation)
        # sort population by cost
        if population_cost:
            agent2cost = cost(population)
        else:
            agent2cost = { agent: cost(agent) for agent in population }
        population = sorted(agent2cost, key=agent2cost.get, reverse=reverse)
        # return if generation exceeds
        generation += 1
        if generation > generations:
            return agent2cost
        # cull population
        population = population[:top_k]
        # create the rest of the population from the top_k
        top_agents = population.copy()
        for _ in range(top_k, pop_size):
            mother, father = random.sample(top_agents, 2)
            # create child
            child = reproduce(mother, father)
            # mutate with 80% probability
            if random.random() < mutation_rate:
                child = mutate(child)
            population.append(child)
