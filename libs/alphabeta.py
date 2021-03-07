import math
import time
import random

class AlphaBeta(object):
    """ Class used to get the best move looking at a given depth """
    def __init__(self,
                 legalmoves,
                 makemove,
                 evaluate,
                 time_limit=5):
        """ Initializes this class with the set values so that get_move() can be 
            called, giving only the curretn boardstate and the depth at which it 
            must be expored.

        Args:
            legalmoves: function(board, player)
                Function that takes in a board and a player and spits out a list
                of moves that can be fed to makemove() to perform a move
            makemove: function(board, move, player)
                Function that performs a given move on the given board by the 
                given player.
                The function must edit the given board to the new state after 
                the move has been made
            player: any
                an object that is identified as the player who is trying to 
                maximize its reward
            opp: any
                Like player, but is identified as the opponent of the player. 
                This player will try to minimize our reward
            time_limit: float
                Optional; if given, then get_move will return back up the tree 
                as soon as this time_limit has been exceeded.
        """
        self.legalmoves = legalmoves
        self.makemove = makemove
        self.evaluate = evaluate
        self.time_limit = time_limit
    
    def get_move(self, board: list, player, opp, max_depth: int):
        """ uses mini-max and alpha-beta pruning to get the best move """
        self.player = player
        self.opponent = lambda turn: opp if turn == player else player
        self.time_stop = time.time() + self.time_limit
        moves = self.legalmoves(board, self.player)
        if moves == []:
            return -1
        max_move = -1
        max_v = -math.inf
        for move in moves:
            if time.time() > self.time_stop:
                print(f"OUT OF TIME")
                if max_move == -1:
                    return random.choice(moves)
                return max_move
            # make the move on the board
            alt = board.copy()
            self.makemove(alt, move, self.player);
            # get the min value for the opponent
            v = self._min_value(
                alt, self.opponent(self.player), -math.inf, math.inf, max_depth)
            # get max count and max move
            if v > max_v:
                max_v = v
                max_move = move
        return max_move
    
    def _max_value(self, 
                   board: any,
                   curr_turn: any, 
                   alpha: int, 
                   beta: int, 
                   depth: int):
        """ Implementation of max-value part of minimax pruning """
        if depth <= 0 or time.time() > self.time_stop:
            return self.evaluate(board, self.player)
        # if no moves available, return current count
        moves = self.legalmoves(board, curr_turn)
        if moves == []:
            return self.evaluate(board, self.player)
        # make a backup of the board
        v = -math.inf
        for move in moves:
            # make the move on the board
            alt = board.copy()
            self.makemove(alt, move, curr_turn);
            alt_v = self._min_value(
                alt, self.opponent(curr_turn), alpha, beta, depth-1)
            # if alt v is better than current, set current since we are maximizing
            if alt_v > v:
                v = alt_v
            # if alt v is better than beta, we have nothing to explore. return curr v
            if alt_v >= beta:
                return v
            # if alt v is better than alpha, overwrite alpha
            if alt_v > alpha:
                alpha = alt_v
        return v

    def _min_value(self,
                   board: any,
                   curr_turn: any, 
                   alpha: int, 
                   beta: int, 
                   depth: int):
        """ Implementation of min-value part of minimax pruning """
        if depth <= 0 or time.time() > self.time_stop:
            return self.evaluate(board, self.player)
        # if no moves available, return current count
        moves = self.legalmoves(board, curr_turn)
        if moves == []:
            return self.evaluate(board, self.player)
        # make a backup of the board
        backup = board.copy()
        v = math.inf
        for move in moves:
            # make the move on the board
            alt = board.copy()
            self.makemove(board, move, curr_turn);
            alt_v = self._max_value(
                alt, self.opponent(curr_turn), alpha, beta, depth-1)
            # if alt v is worst than current, set current since we are minimizing
            if alt_v < v:
                v = alt_v
            # if alt v is worst than alpha, we have nothing to explore. return curr v
            if alt_v <= alpha:
                return v
            # if alt v is worst than beta, overwrite beta
            if alt_v < beta:
                beta = alt_v
        return v
