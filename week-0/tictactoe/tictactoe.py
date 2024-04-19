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
    X = 'X'  # Assuming 'X' and 'O' are not defined elsewhere
    O = 'O'
    x_count = 0  # Number of 'X's on the board
    o_count = 0  # Number of 'O's on the board

    for row in board:
        x_count += row.count(X)
        o_count += row.count(O)

    # 'X' plays next if there are fewer or equal 'X's than 'O's on the board
    return X if x_count <= o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell is None:  # Explicitly compare to None for clarity
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
    # Define possible players
    X, O = 'X', 'O'
    for player in (X, O):
        # Check horizontal rows for a win
        for row in board:
            if row == [player] * 3:
                return player

        # Check vertical columns for a win
        for col in range(3):
            if [board[row][col] for row in range(3)] == [player] * 3:
                return player

        # Check diagonals for a win
        if [board[i][i] for i in range(3)] == [player] * 3:
            return player
        if [board[i][2-i] for i in range(3)] == [player] * 3:
            return player

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError
