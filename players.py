import numpy as np
class ModelPlayer():
    ''' Represents a player that makes decisions based on a nueral network '''
    def __init__(self, model, makemove, state2img):
        self.model = model
        self.makemove = makemove
        self.state2img = state2img

    def choosemove(self, board, moves, player):
        imgs = []
        for move in moves:
            alt = board.copy()
            self.makemove(alt, move, player)
            imgs.append(self.state2img(alt, player))
        move_index = np.argmax(self.model.predict(imgs))
        return moves[move_index]


import random
class RandomPlayer():
    '''player that plays random moves given options. Used to test legitimacy
       of player skills'''
    def choosemove(self, board, moves, player):
        return random.choice(moves)


from libs.alphabeta import AlphaBeta
class AlphaBetaPlayer():
    '''Interface to play against the AlphaBetaPlayer'''
    def __init__(self, legalmoves, makemove, depth):
        self.depth = depth
        def evaluate(board, player):
            return board.count(player)
        self.alphabeta = AlphaBeta(
            legalmoves, 
            makemove, 
            evaluate, 
            time_limit=5)
    def choosemove(self, board, moves, player):
        return self.alphabeta.get_move(board, player, -player, self.depth)

from libs.alphabeta_mpi import AlphaBetaMPI
class AlphaBetaMPIPlayer():
    '''Interface to play against the AlphaBetaPlayer'''
    def __init__(self, legalmoves, makemove, depth):
        self.depth = depth
        def evaluate(board, player):
            return board.count(player)
        self.alphabeta = AlphaBetaMPI(
            legalmoves, 
            makemove, 
            evaluate, 
            time_limit=5)
    def choosemove(self, board, moves, player):
        return self.alphabeta.get_move(board, player, -player, self.depth)

from libs.util import pickle_load
from research import deserialize_pop
def load_standard_models():
    # create the standard assessment players
    return deserialize_pop(pickle_load('archive/standard_players.pkl'))

