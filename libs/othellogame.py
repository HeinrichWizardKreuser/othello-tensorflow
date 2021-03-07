BLACK = -1
EMPTY = 0
WHITE = 1
OUTER = 3
ALLDIRECTIONS = [-11, -10, -9, -1, 1, 9, 10, 11]

def init_board():
    ''' initializes a starting board '''
    board = [0] * 100
    for i in range(0, 10):
        board[i] = OUTER;
    for i in range(10, 90):
        if 1 <= i%10 <= 8:
            board[i] = EMPTY
        else:
            board[i] = OUTER;
    for i in range(90, 100):
        board[i] = OUTER
    board[44] = WHITE
    board[45] = BLACK
    board[54] = BLACK
    board[55] = WHITE
    class BoardList(list):
        def __repr__(self):
            return to_str(self)
    return BoardList(board)

def legalmoves(board: list, player: int):
    ''' gets a list of all of the legal moves for this player '''
    moves = []
    for row in range(10, 90, 10):
        for move in range(row+1, row+9):
            if _is_legal_move(board, move, player):
                moves.append(move)
    return moves

def makemove(board: list, move: int, player:int):
    ''' makes the given move for the given player '''
    board[move] = player
    for dir in ALLDIRECTIONS:
        _make_flips(board, move, dir, player)
    
def _make_flips(board: list, move: int, dir: int, player: int):
    ''' performs the flips between players '''
    would_flip = _would_flip(board, move, dir, player)
    if would_flip:
        c = move + dir
        while c != would_flip:
            board[c] = player
            c += dir

def _is_legal_move(board: list, move: int, player: int):
    ''' checks whether the given move is legal for the given player '''
    if not _is_valid_move(board, move):
        return False
    if board[move] == EMPTY:
        for dir in ALLDIRECTIONS:
            if _would_flip(board, move, dir, player):
                return True
    return False

def _is_valid_move(board: list, move: int):
    ''' checks whether the move is in the format 11 - 88 '''
    return (11 <= move <= 88) and (1 <= move%10 <= 8)

def _would_flip(board: list, move: int, dir: int, player: int):
    ''' checks if move would result in a flipping '''
    c = move + dir
    if board[c] == -player:
        return _find_bracketing_piece(board, c+dir, dir, player)
    return False;

def _find_bracketing_piece(board: list, square: int, dir: int, player: int):
    ''' find the piece on the other side '''
    while board[square] == -player:
        square = square + dir
    if board[square] == player:
        return square
    return False

def get_winner(board: list):
    ''' gets the winner of the match (the player with the mos discs. '''
    whitepieces = board.count(WHITE)
    blackpieces = board.count(BLACK)
    if whitepieces > blackpieces:
        return WHITE
    elif whitepieces < blackpieces:
        return BLACK
    return EMPTY

def _name_of(player):
    return '.■□'[player]

def to_str(board):
    ''' converts the board to a string representation '''
    s = '  ' + ' '.join(map(str, range(1, 9))) + '\n'
    for row in range(1, 9):
        s += f'{row} ' + ' '.join([
            _name_of(board[col + 10*row])
            for col in range(1, 9)
        ]) + '\n'
    return s
