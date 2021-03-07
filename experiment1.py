'''
EXPERIMENT 1:
hypothesis: tournament style should show better improvement over freeforall
training type: learn from moves of winners

tournament style vs freeforall with 870 vs 9900
across all generations, not just every 10th
as well as average performance
'''

from libs.othellogame import *
from play import *

def record_match(p1, p2):
    '''plays a match between the two given models and returns the recording'''
    # setup game
    board = init_board()
    curr_turn = BLACK
    color2player = [0, p2, p1]
    recording = []
    # start game
    while True:
        moves = legalmoves(board, curr_turn)
        if moves == []:
            return recording, board.count(BLACK), board.count(WHITE)
        # get the best move
        move = color2player[curr_turn].choosemove(board, moves, curr_turn)
        # make that move
        makemove(board, move, curr_turn)
        # add img to recording
        recording.append(state2img(board, curr_turn))
        # pass turn
        curr_turn = -curr_turn

from itertools import combinations
from research import *
from libs.util import *

def freeforall(population):
    '''plays a free-for-all tournament amongst all players'''
    agent2score = { agent: 0 for agent in population }
    agent2imgs = { agent: [] for agent in population }
    img_sets = 0
    pop_size = len(population)
    cnt = freeforall_pop2cnt(pop_size)
    print(f"Starting freeforall with {pop_size} players ({cnt} matches)...")
    bar = ProgressBar(cnt)
    agent2modelplayer = { 
        agent: ModelPlayer(agent, makemove, state2img) 
        for agent in population 
    }
    for p1, p2 in combinations(population, 2):
        # play match for each from both sides
        p1m, p2m = agent2modelplayer[p1], agent2modelplayer[p2]
        for bp, wp, bpm, wpm in [ [p1, p2, p1m, p2m], [p2, p1, p2m, p1m] ]:
            # BLACK VS WHITE
            recording, b_pieces, w_pieces = record_match(bpm, wpm)                
            diff = b_pieces - w_pieces
            agent2score[bp] += diff
            agent2score[wp] -= diff
            # now save states chosen by each agent
            black_imgs = []
            white_imgs = []
            for i, img in enumerate(recording):
                if i%2 == 0:
                    black_imgs.append(img)
                else:
                    white_imgs.append(img)
            agent2imgs[bp] += black_imgs
            agent2imgs[wp] += white_imgs
            img_sets += 1
            # update progress
            bar.update()
    info = {'img_sets': img_sets }
    return agent2score, agent2imgs, info


def tournament(population):
    agent2score = { agent: 0 for agent in population }
    agent2imgs = { agent: [] for agent in population }
    img_sets = 0
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
                recording, b_pieces, w_pieces = record_match(bpm, wpm)                
                diff = b_pieces - w_pieces
                agent2score[bp] += diff
                agent2score[wp] -= diff
                # now save states chosen by each agent
                black_imgs = []
                white_imgs = []
                for i, img in enumerate(recording):
                    if i%2 == 0:
                        black_imgs.append(img)
                    else:
                        white_imgs.append(img)
                agent2imgs[bp] += black_imgs
                agent2imgs[wp] += white_imgs
                img_sets += 1
                # update progress
                bar.update()
        # sort based on wins
        ranked = sorted(agent2score, key=agent2score.get, reverse=True)
        # hat becomes top half
        hat = ranked[:len(hat)//2]
    info = {'img_sets': img_sets }
    return agent2score, agent2imgs, info

''' CALCULATE DATA VS POPULATION RATIOS '''
def freeforall_pop2cnt(pop_size):
    return int(pop_size*(pop_size-1))

def tournament_pop2cnt(pop_size):
    img_sets = 0
    while pop_size > 1:
        pop_size //= 2
        img_sets += pop_size
    return img_sets * 2

f_pop2cnt, f_cnt2pop = {}, {}
t_pop2cnt, t_cnt2pop = {}, {}
for pop_size in range(1, 10000):
    f_cnt = freeforall_pop2cnt(pop_size)
    f_pop2cnt[pop_size] = f_cnt
    f_cnt2pop[f_cnt] = pop_size
    t_cnt = tournament_pop2cnt(pop_size)
    t_pop2cnt[pop_size] = t_cnt
    t_cnt2pop[t_cnt] = pop_size

def freeforall_cnt2pop(count):
    pop_size = (1 + (1+4*count)**0.5)/2
    if pop_size != int(pop_size):
        raise ArithmeticError(f"Illegal count for freeforall: {count}")
    return int(pop_size)

def tournament_cnt2pop(count):
    pop_size = t_cnt2pop.get(count)
    if pop_size == None:
        raise ArithmeticError(f"Illegal count for tournament: {count}")
    return pop_size

import math
''' CREATE TRAINING DATA FROM ROUND '''
def create_training_data(population, agent2score, agent2imgs):
    """ From the return data tournament() or freeforall(), generate training
        data such as train_images and train_labels """
    # construct list of all imgs with parallel list of all labels
    train_images = []
    train_labels = []
    pop_size = len(population)
    for agent in population:
        # add imgs to all images
        val = math.tanh(agent2score[agent]/200) * 0.5 - 0.5
        for img in agent2imgs[agent]:
            train_images.append(img)
            train_labels.append(val)
    return train_images, train_labels

import os
def run_experiment(experiment_name, play_func, pop_size):
    exp_path = f'experiments/{experiment_name}'
    # define standard procedure to save a population
    def save_population(population, generation_num):
        pickle_dump(data=serialize_pop(population),
            filename=f'{exp_path}/models/{generation_num:0>3}.pkl')
    # check if experiment already exists
    if not os.path.isdir(exp_path):
        # create relevant folders
        os.mkdir(f'{exp_path}/')
        os.mkdir(f'{exp_path}/misc/')
        os.mkdir(f'{exp_path}/models/')
        os.mkdir(f'{exp_path}/training_data/')
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

    def assess(population):
        # get stats from playing match
        agent2score, agent2imgs, info = play_func(population)
        # get performance of best player
        top_model = max(agent2score, key=agent2score.get)
        performance = assess_top(top_model)
        # build training images etc
        train_images, train_labels = create_training_data(population, 
            agent2score, agent2imgs)
        return agent2score, performance, train_images, train_labels

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

    def save_training_data(train_images, train_labels):
        pickle_dump(data=[train_images, train_labels],
            filename=f'{exp_path}/training_data/{generation_num:0>3}.pkl')

    tle = TimeLeftEstimator(generation_num, 100)

    # start the training
    while True:
        print(f"--------------------------------------------------------------")
        now = datetime.datetime.today().strftime('%Y-%m-%d %X.%f') 
        print(f"{now}: GENERATION {generation_num}")

        print(f"\n[1/3] ASSESSMENT [ SAFE TO KILL ]")
        agent2score, performance, train_images, train_labels = assess(population)

        print(f"\n[2/3] TRAINING [ SAFE TO KILL ]")
        population = sorted(agent2score, key=agent2score.get, reverse=True)
        top_k = calc_top_k(population, agent2score, p=0.2)
        print(f"top contributing 20%: {top_k}/{pop_size}")
        bar = ProgressBar(top_k)
        for agent in population[:top_k]:
            agent.fit(train_images, train_labels, epochs=5, verbose=0)
            bar.update()
        filler_pop = generate_population(pop_size - top_k)
        for i in range(top_k, pop_size):
            population[i] = filler_pop[i - top_k]

        print(f"\n[3/3] SAVE DATA [ NOT SAFE TO KILL ]")
        bar = ProgressBar(4)
        save_training_data(train_images, train_labels)
        bar.update()
        save_performance(performance)
        bar.update()
        save_scores(agent2score)
        bar.update()
        generation_num += 1
        save_population(population, generation_num)
        bar.update()

        tle.update()
'''
# data_count = 6
data_count = 870
# experiment with tournament 870
freeforall_pop_size = freeforall_cnt2pop(data_count)
tournament_pop_size = tournament_cnt2pop(data_count)
# run_experiment(f'freeforall{data_count}', freeforall, freeforall_pop_size, 
#     freeforall_pop_size)

# experiment with freeforall 870
run_experiment(f'tournament{data_count}', tournament, tournament_pop_size, 
    freeforall_pop_size)
'''

# data_count = 6
data_count = 870
# experiment with tournament 870
# pop_size = freeforall_cnt2pop(data_count)
# run_experiment(f'freeforall{data_count}', freeforall, pop_size)

# experiment with freeforall 870
pop_size = tournament_cnt2pop(data_count)
run_experiment(f'tournament{data_count}', tournament, pop_size)



'''
print(" cnt | fpop | tpop")
for data_count in range(1, 100000):
    try:
        t_pop_size = tournament_cnt2pop(data_count)
        f_pop_size = freeforall_cnt2pop(data_count)
    except:
        continue
    print(f"{data_count:>4} | {f_pop_size:>4} | {t_pop_size:>4}")

valid data_count for both play styles and their resulting population size
  cnt | fpop | tpop
    2 |    2 |    3
    6 |    3 |    5
   20 |    5 |   13
   30 |    6 |   17
  132 |   12 |   69
  156 |   13 |   81
  210 |   15 |  111
  240 |   16 |  127
  306 |   18 |  159
  380 |   20 |  193
  462 |   22 |  237
  650 |   26 |  329
  870 |   30 |  441
 1122 |   34 |  567
 1260 |   36 |  637
 1640 |   41 |  827
 1722 |   42 |  867
 1806 |   43 |  909
 1892 |   44 |  953
 1980 |   45 |  997
 2256 |   48 | 1135
 2352 |   49 | 1183
 2862 |   54 | 1439
 3306 |   58 | 1661
 3422 |   59 | 1719
 3540 |   60 | 1777
 3660 |   61 | 1837
 3782 |   62 | 1899
 4290 |   66 | 2151
 4556 |   68 | 2285
 4830 |   70 | 2423
 4970 |   71 | 2493
 5256 |   73 | 2633
 5402 |   74 | 2707
 5852 |   77 | 2935
 6006 |   78 | 3009
 6162 |   79 | 3087
 6806 |   83 | 3409
 6972 |   84 | 3493
 7310 |   86 | 3663
 7656 |   88 | 3839
 8010 |   90 | 4015
 8190 |   91 | 4097
 8556 |   93 | 4285
 9312 |   97 | 4663
 9900 |  100 | 4959
10506 |  103 | 5259
11342 |  107 | 5679
11556 |  108 | 5785
12210 |  111 | 6113
12432 |  112 | 6223
13110 |  115 | 6561
14042 |  119 | 7031
14280 |  120 | 7151
14520 |  121 | 7267
14762 |  122 | 7391
15252 |  124 | 7635
15500 |  125 | 7759
16002 |  127 | 8009
16256 |  128 | 8137
16770 |  130 | 8391
17292 |  132 | 8653
17822 |  134 | 8919
18090 |  135 | 9053
18632 |  137 | 9323
18906 |  138 | 9461
19740 |  141 | 9877

'''
