from research import *
from libs.util import *

MUTATION_RATE = 0.8
CULL_RATE = 0.2
# pop_size = 256
# population = generate_population(pop_size)

def tournament_pop2cnt(pop_size):
    img_sets = 0
    while pop_size > 1:
        pop_size //= 2
        img_sets += pop_size
    return img_sets * 2

def tournament(population):
    agent2score = { agent: 0 for agent in population }
    hat = population.copy()
    cnt = tournament_pop2cnt(pop_size)
    print(f"Starting tournament with {pop_size} players ({cnt} matches)...")
    bar = ProgressBar(cnt)
    agent2modelplayer = { 
        agent: ModelPlayer(agent, makemove, state2img) 
        for agent in population 
    }
    while len(hat) > 1:
        for p1, p2 in zip(hat[::2], hat[1::2]):
            p1m, p2m = agent2modelplayer[p1], agent2modelplayer[p2]
            for bp, wp, bpm, wpm in [ [p1, p2, p1m, p2m], [p2, p1, p2m, p1m] ]:
                # BLACK VS WHITE
                b_pieces, w_pieces = play_match(bpm, wpm)                
                diff = b_pieces - w_pieces
                agent2score[bp] += diff
                agent2score[wp] -= diff
                # update progress
                bar.update()
        # sort based on wins
        ranked = sorted(agent2score, key=agent2score.get, reverse=True)
        # hat becomes top half
        hat = ranked[:len(hat)//2]
    return agent2score

def randsample(n):
    return random.sample(list(range(n)), random.randint(1, n-1))

def mutate(model):
    weights = model.get_weights()
    layer1, _, layer2, _ = weights
    for randint in randsample(128*16 + 16):
        row = randint // 16
        col = randint % 16
        if row < 128:
            layer1[row][col] = random.random() * 2 - 1
        else:
            layer2[col] = random.random() * 2 - 1
    model.set_weights(weights)
    return model


def reproduce(mother, father):
    child = generate_model()
    child.set_weights(mother.get_weights())
    c_weights = child.get_weights()
    c_layer1, _, c_layer2, _ = c_weights
    f_layer1, _, f_layer2, _ = father.get_weights()
    for i in range(128):
        for j in random.sample(range(16), random.randint(0, 15)):
            c_layer1[i][j] = f_layer1[i][j]
    for i in random.sample(range(16), random.randint(0, 15)):
        c_layer2[i] = f_layer2[i]
    child.set_weights(c_weights)
    return child

from play import *

import os
def run_experiment(experiment_name, pop_size):
    exp_path = f'experiments/{experiment_name}'

    def save_performance(performance):
        file = open(f'{exp_path}/misc/performance.csv', 'a')
        file.write(f'{generation_num}\t' + '\t'.join(map(str, performance)) + \
            '\n')
        file.close()
    def save_scores(agent2score):
        file = open(f'{exp_path}/misc/data.csv', 'a')
        ranked = list(sorted(agent2score.values(), reverse=True))
        file.write(f'{generation_num}\t' + '\t'.join(map(str, ranked)) + '\n')
        file.close()
    def save_population(population, generation_num):
        pickle_dump(data=serialize_pop(population),
            filename=f'{exp_path}/models/{generation_num:0>3}.pkl')

    def assess(population):
        agent2score = tournament(population)
        top_model = max(agent2score, key=agent2score.get)
        performance = assess_top(top_model)
        return agent2score, performance


    # check if experiment already exists
    if not os.path.isdir(exp_path):
        # create relevant folders
        os.mkdir(f'{exp_path}/')
        os.mkdir(f'{exp_path}/misc/')
        os.mkdir(f'{exp_path}/models/')
        # os.mkdir(f'{exp_path}/scores/')
        # create a population
        generation_num = 0
        population = generate_population(pop_size)
        save_population(population, generation_num)
        # create performance CSV
        file = open(f'{exp_path}/misc/performance.csv', 'w')
        file.write(f'Generation\tab3\tab5\tab7\tr10\tn10\n')
        file.close()
        # create data CSV
        file = open(f'{exp_path}/misc/data.csv', 'w')
        file.write(f'Generation\t' + '\t'.join(map(str, range(pop_size))) + \
            '\n')
        file.close()
    else: # pick up where we left off
        # find out what the latest models set is
        generation_num = int(max(os.listdir(f'{exp_path}/models/'))[:3])
        # load population
        serialized_pop = pickle_load(
            f'{exp_path}/models/{generation_num:0>3}.pkl')
        population = deserialize_pop(serialized_pop)

    tle = TimeLeftEstimator(generation_num, 200)

    # start the training
    while True:
        print(f"--------------------------------------------------------------")
        now = datetime.datetime.today().strftime('%Y-%m-%d %X.%f')
        print(f"{now}: GENERATION {generation_num}")


        print(f"\n[1/3] ASSESSMENT [ SAFE TO KILL ]")
        agent2score, performance = assess(population)


        print(f"\n[2/3] REPRODUCTION [ SAFE TO KILL ]")
        population = sorted(agent2score, key=agent2score.get, reverse=True)
        # calculate the top contributing members
        top_k = calc_top_k(p=CULL_RATE)
        # now we will use the top top_k
        fitness = ordered_costs[:top_k]
        mn = min(fitness)
        mx = max(fitness)
        if mx != mn:
            fitness = [ f-mn for f in fitness ]
            sm = sum(fitness)
        else:
            sm = top_k
        fitness = [ f/sm for f in fitness ]
        running_fitness = 0
        for i in range(top_k):
            running_fitness += fitness[i]
            fitness[i] = running_fitness
        # cull population
        population = population[:top_k]
        top_agents = population.copy()
        def select_parent():
            r = random.random()
            for i in range(top_k):
                if r < fitness[i]:
                    return population[i]
        # fill up rest of population
        for _ in range(top_k, pop_size):
            # choose mother and father
            mother, father = select_parent(), select_parent()
            # create child
            child = reproduce(mother, father)
            # mutate with 80% probability
            if random.random() < MUTATION_RATE:
                child = mutate(child)
            population.append(child)
        generation_num += 1


        print(f"\n[3/3] SAVE DATA [ NOT SAFE TO KILL ]")
        bar = ProgressBar(3)
        save_performance(performance)
        bar.update()
        save_scores(agent2score)
        bar.update()
        save_population(population, generation_num)
        bar.update()

        tle.update()


pop_size = 256
run_experiment(f'GA{pop_size}', pop_size)

