from libs.othellogame import WHITE, BLACK
def state2img(board, player):
    ''' create an image from the given board, from the given player's 
        persepctive '''
    good = [1, 0]
    bad = [0, 1]
    neutral = [0, 0]

    if player == WHITE:
        piece2vector = [
            neutral, # EMPTY 0
            good, # WHITE 1
            bad, # BLACK -1
        ]
    else:
        piece2vector = [
            neutral, # EMPTY 0
            bad, # WHITE 1
            good, # BLACK -1
        ]
    img = []
    for row in range(10, 90, 10):
        for piece in board[row+1:row+9]:
            img.append(piece2vector[piece])
    return img

import tensorflow as tf
from tensorflow import keras

def generate_model():
    '''generate the standard model used for this othello game'''
    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(8*8, 2)),
        keras.layers.Dense(16),
        keras.layers.Dense(1, activation='linear'),
    ])
    model.compile(
        optimizer='adam',
        loss='mean_squared_error',
        metrics=['mean_squared_error']
    )
    return model

from libs.util import ProgressBar

def generate_population(pop_size=16):
    '''Generate a population of models of size pop_size'''
    print(f"generating population with size {pop_size}...")
    bar = ProgressBar(pop_size)
    population = []
    for _ in range(pop_size):
        population.append(generate_model())
        bar.update()
    return population


''' SERIALIZATION OF DATA '''
def serialize_pop(population):
    """ Serializes the given population along with each of their scores """
    return [ agent.get_weights() for agent in population ]

def deserialize_pop(serialized_pop):
    pop_size = len(serialized_pop)
    population = generate_population(pop_size)
    print(f"Deserializing pop data...")
    bar = ProgressBar(pop_size)
    for agent, weights in zip(population, serialized_pop):
        agent.set_weights(weights)
        bar.update()
    return population


def calc_top_k(population, agent2score, p=0.2):
    """ calculates the top p% of the population that contribute to the total 
        score """
    running_total = 0
    ordered_costs = [ agent2score[agent] for agent in population ]
    limit = p * sum(map(abs, ordered_costs))
    for top_cut, agent in enumerate(population, start=1):
        running_total += agent2score[agent]
        if running_total > limit:
            return top_cut
