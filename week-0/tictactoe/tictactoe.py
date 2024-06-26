"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    X = 'X'
    O = 'O'
    x_count = 0
    o_count = 0

    for row in board:
        x_count += row.count(X)
        o_count += row.count(O)

    return X if x_count <= o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell is None:
                possible_moves.add((i, j))

    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    player_move = player(board)

    new_board = [row[:] for row in board]
    i, j = action

    if board[i][j] is not None:
        raise ValueError("Invalid move: Position already occupied")
    else:
        new_board[i][j] = player_move

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    X, O = 'X', 'O'
    for player in (X, O):
        for row in board:
            if row == [player] * 3:
                return player

        for col in range(3):
            if [board[row][col] for row in range(3)] == [player] * 3:
                return player

        if [board[i][i] for i in range(3)] == [player] * 3:
            return player
        if [board[i][2-i] for i in range(3)] == [player] * 3:
            return player

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    for row in board:
        if None in row:
            return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win_player = winner(board)
    X, O = 'X', 'O'

    if win_player == X:
        return 1
    elif win_player == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    def max_value(board):
        optimal_move = ()
        if terminal(board):
            return utility(board), optimal_move
        else:
            v = -5
            for action in actions(board):
                minval = min_value(result(board, action))[0]
                if minval > v:
                    v = minval
                    optimal_move = action
            return v, optimal_move

    def min_value(board):
        optimal_move = ()
        if terminal(board):
            return utility(board), optimal_move
        else:
            v = 5
            for action in actions(board):
                maxval = max_value(result(board, action))[0]
                if maxval < v:
                    v = maxval
                    optimal_move = action
            return v, optimal_move

    curr_player = player(board)

    if terminal(board):
        return None

    current_player = player(board)
    X, O = 'X', 'O'  # Define player symbols

    # Decide which function to use based on the current player
    if current_player == X:
        _, action = max_value(board)
    else:
        _, action = min_value(board)

    return action
