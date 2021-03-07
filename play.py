from libs.othellogame import *


def play_match(p1, p2):
    ''' plays a match between the two given models and returns the amount of 
        pieces remaining for each player at the end of the game '''
    # setup game
    board = init_board()
    curr_turn = BLACK
    color2player = [0, p2, p1]
    # start game
    while True:
        moves = legalmoves(board, curr_turn)
        if moves == []:
           return board.count(BLACK), board.count(WHITE)
        # get the best move
        move = color2player[curr_turn].choosemove(board, moves, curr_turn)
        # make that move
        makemove(board, move, curr_turn)
        # pass turn
        curr_turn = -curr_turn

def play2matches(p1, p2):
    b_pieces, w_pieces = play_match(p1, p2)
    round1 = b_pieces - w_pieces
    b_pieces, w_pieces = play_match(p2, p1)
    round2 = w_pieces - b_pieces
    return round1, round2

from players import *
from research import state2img
ab3 = AlphaBetaPlayer(legalmoves, makemove, 3)
ab5 = AlphaBetaPlayer(legalmoves, makemove, 5)
ab7 = AlphaBetaMPIPlayer(legalmoves, makemove, 7)
ab2player = { 'ab3': ab3, 'ab5': ab5, 'ab7': ab7 }
rand_player = RandomPlayer()
standard_players = [ 
    ModelPlayer(model, makemove, state2img) 
    for model in load_standard_models()
]

from libs.util import ProgressBar
def assess_top(top_model):
    """ Assesses this model against alpha-beta players whom looks 3, 5 and 7
        moves ahead respectively as well as the average performance against 10
        players that perform random moves and 10 unseen, untrained models
    
    Args:
        top_model: keras.Model
            the model to assess
    
    Returns:
        list containing the performance against ab3, ab5, ab7, r10, n10 
        respectively in the order as described above.
    """
    model_player = ModelPlayer(top_model, makemove, state2img)
    performance = []
    # play against alphabeta players
    print(f"Assessing Performance...")
    bar = ProgressBar(3 + 10 + 10)
    for ab_num, ab_player in ab2player.items():
        performance.append(sum(play2matches(model_player, ab_player)))
        bar.update()
    # play against random moves
    r10 = 0
    for _ in range(10):
        r10 += sum(play2matches(model_player, rand_player))
        bar.update()
    performance.append(r10 / 10)
    # play against new models
    n10 = 0
    for standard_player in standard_players:
        n10 += sum(play2matches(model_player, standard_player))
        bar.update()
    performance.append(n10 / 10)
    # send back performance data
    return performance

