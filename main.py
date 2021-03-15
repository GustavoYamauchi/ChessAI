import chess
import random
import re
import numpy as np
from pieceSquareValueTables import pieceSquareValue

# Pieces
pieces = {
    chess.PAWN: 100,
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}


piecesToInitialPositions = {
    chess.KNIGHT = [chess.B1, chess.G1, chess.B8, chess.G8]
    chess.BISHOP = [chess.C1, chess.F1, chess.C8, chess.F8]
    chess.ROOK = [chess.A1, chess.H1, chess.A8, chess.H8]
}

# Define PHASE
def measureGamePhases(board, move):
    fen = board.board_fen().split("/")

    lstPieces = board.piece_map()
    points = 0
    phase = 0

    # Transitions earlyGame => midGame
    # Proporção
    # 1 -> 1
    # 2 -> 1.5
    # 3 -> 3.0
    # 4 -> 3.0
    # 5 -> 1.6

    if board.ply() >= 12:
        points += 100

    if len(lstPieces.values()) <= 30:
        points += 100 * 1.5

    if not board.has_castling_rights(chess.WHITE):
        points += 100 * 3

    if not board.has_castling_rights(chess.BLACK):
        points += 100 * 3

    if len(re.findall("(n|r|b)", fen[0])) + len(re.findall("(N|R|B)", fen[7])) < 7:
        points += 100 * 1.6

    # Transitions mid => late

    if points > 300:
        phase += 1

    return phase

# All Phases
def captureEvaluate(board, move):
    captures = []
    piece = board.piece_at(move.to_square)
    if piece:
        captures.append(pieces[piece.piece_type])

    return max(captures)


def boardValueEvaluate(board):
    vWhite = 0
    vBlack = 0
    for piece in board.piece_map().values():
        if piece.color == chess.BLACK:
            vBlack += pieces[piece.piece_type]
        else:
            vWhite += pieces[piece.piece_type]

    return vWhite - vBlack


# Phase 0 (earlyGame)
def devMinorsEvaluate(board, move):
    pieceType = board.piece_at(move.from_square).piece_type
    validPieces = {chess.KNIGHT, chess.BISHOP}
    if not pieceType in validPieces:
        return 0
    if (board.turn == chess.BLACK):
        positions = pieceSquareValue[pieceType][::-1]
        return positions[move.to_square]
    return pieceSquareValue[pieceType][move.to_square]


def rookEvaluate(board, move):
    if (board.piece_type_at(move.to_square) != chess.ROOK):
        return 0

    positionsRooks = [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0]

    if (board.turn == chess.BLACK):
        positions = positions[::-1]

    return 70 if is_castling(move) else positions[move.to_square]


def devPawnsEvaluate(board, move):
    if board.piece_type_at(move.to_square()) != chess.PAWN:
        return 0

    positionsPawns = [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5, -10,  0,  0, -10, -5,  5,
        5, 10, 10, -20, -20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]

    if board.turn == chess.BLACK:
        positionsPawns = positionsPawns[::-1]

    return positionsPawns[move.to_square()]

# Evaluate
def evaluate(board, move):
    weight = [
        {"capture": 1, "boardValue": 2},
        {"capture": 1, "boardValue": 2},
        {"capture": 1, "boardValue": 2}
    ]
    value = 0
    phase = measureGamePhases(board)

    value += captureEvaluate(board, move) * weight[phase]["capture"]
    value += boardValueEvaluate(board) * weight[phase]["boardValue"]
    devPawnsEvaluate(board, move)

    return value

# Minimax
def minimax(board, depth, maximizing_player, alfa=float("-inf"), beta=float("inf"), move=None):
    if depth == 0 or board.is_game_over():
        return evaluate(board, move), board.peek()

    if maximizing_player:
        lastMove = None
        for move in board.legal_moves:
            board.push(move)
            valueAux = minimax(board, depth - 1, False, alfa, beta, move)
            if beta <= alfa:
                board.pop()
                break
            if alfa > valueAux[0]:
                board.pop()
            else:
                alfa = valueAux[0]
                lastMove = board.pop()
        return alfa, lastMove

    else:
        lastMove = None
        for move in board.legal_moves:
            board.push(move)
            valueAux = minimax(board, depth - 1, True, alfa, beta, move)
            if beta <= alfa:
                board.pop()
                break
            if beta < valueAux[0]:
                board.pop()
            else:
                beta = valueAux[0]
                lastMove = board.pop()
        return beta, lastMove

# Play
def play():
    while (not board.is_game_over()):
        if(board.turn == chess.WHITE):
            legalMoves = list(board.legal_moves)
            board.push(minimax(board, 3, True)[1])
            print("WHITE")
        else:
            legalMoves = list(board.legal_moves)
            board.push(minimax(board, 3, True)[1])
            print("BLACK")

        print(f'{board} \n')

    if board.is_stalemate():
        return "Stalemate"
    if board.is_checkmate():
        return "Checkmate"
    if board.is_insufficient_material():
        return "Insufficiente Material"
    if board.is_seventyfive_moves():
        return "SeventyFive"
    if board.is_fivefold_repetition():
        return "FiveFold"


board = chess.Board()

# print(board.pieces(chess.PAWN, chess.WHITE))
board.push_san("e4")
board.push_san("e5")
board.push_san("Qh5")
board.push_san("Nc6")
# board.push_san("Bc4")
# board.push_san("Nf6")


print(f'\n\n Que comecem os jogos \n\n')
jogada = play()
print(f'F I N A L - {jogada}')
print(f'{board} \n')
