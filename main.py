import chess
import random
import re
import numpy as np
from pieceSquareValueTables import pieceSquareValue

# Pieces
pieces = {
    None: 0,
    chess.PAWN: 100,
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}

piecesToInitialPositions = {
    chess.KNIGHT : [chess.B1, chess.G1, chess.B8, chess.G8],
    chess.BISHOP : [chess.C1, chess.F1, chess.C8, chess.F8],
    chess.ROOK : [chess.A1, chess.H1, chess.A8, chess.H8]
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
def captureEvaluate(board, capture):
    value = 0
    # piece = board.piece_at(move.to_square)
    # if piece:
    #     captures.append(pieces[piece.piece_type])
    value = pieces[capture]

    return value


def boardValueEvaluate(board):
    vWhite = 0
    vBlack = 0
    for piece in board.piece_map().values():
        if piece.color == chess.BLACK:
            vBlack += pieces[piece.piece_type]
        else:
            vWhite += pieces[piece.piece_type]

    if board.turn == chess.BLACK:
        return vBlack - vWhite
    else:
        return vWhite - vBlack


# Phase 0 (earlyGame)
def devMinorsEvaluate(board, move):
    pieceType = board.piece_type_at(move.to_square)
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

    positions = pieceSquareValue[chess.ROOK]
    if (board.turn == chess.BLACK):
        positions = pieceSquareValue[chess.ROOK][::-1]

    return 70 if board.is_castling(move) else positions[move.to_square]

def devPawnsEvaluate(board, move):
    if board.piece_type_at(move.to_square) != chess.PAWN:
        return 0

    if board.turn == chess.BLACK:
        positionsPawns = pieceSquareValue[chess.PAWN][::-1]
        return positionsPawns[move.to_square]

    return pieceSquareValue[chess.PAWN][move.to_square]

# Evaluate
def evaluate(board, move, capture):
    weight = [
        {"capture": 1.3, "boardValue": 1.4, "devMinors" : 1.45, "rook" : 1.0, "devPawns" : 1.7},
        {"capture": 1.6, "boardValue": 1.4, "devMinors" : 1.45, "rook" : 1.0, "devPawns" : 1.7},
        {"capture": 1.3, "boardValue": 1.4, "devMinors" : 1.45, "rook" : 1.0, "devPawns" : 1.7}
    ]
    value = 0
    phase = measureGamePhases(board, move)

    value += captureEvaluate(board, capture) * weight[phase]["capture"]
    # print(move, value)
    value += boardValueEvaluate(board) * weight[phase]["boardValue"]
    # print(move, value)
    value += devMinorsEvaluate(board, move) * weight[phase]["devMinors"]
    # print(move, value)
    value += rookEvaluate(board, move) * weight[phase]["rook"]
    # print(move, value)
    value += devPawnsEvaluate(board, move) * weight[phase]["devPawns"]
    # print(move, value)

    return value

# Minimax
def minimax(board, depth, maximizing_player, alfa=float("-inf"), beta=float("inf"), move=None, capture=None):
    if depth == 0 or board.is_game_over():
        return evaluate(board, move, capture), board.peek()

    if maximizing_player:
        lastMove = None
        print("MAX")
        for legalMove in board.legal_moves:
            control = False
            oldAlfa = alfa
            oldMove = lastMove
            if board.is_capture(legalMove):
                capture = board.piece_type_at(legalMove.to_square)
            board.push(legalMove)
            print("max")
            valueAux = minimax(board, depth - 1, False, alfa, beta, legalMove, capture)
            print(f"alfa: {alfa}, value: {valueAux}, max")
            input()
            if alfa > valueAux[0]:
                board.pop()
            else:
                alfa = valueAux[0]
                lastMove = board.pop()
                # print(f"mudou o lastMove, move: {lastMove} ,valor: {alfa}")
            if beta <= alfa:
                print(f"beta: {beta}, alfa: {alfa}, lastMove: {lastMove}, oldAlfa: {oldAlfa}, oldMove: {oldMove}, max")               
                control = True
                break
        return alfa if not control else oldAlfa, lastMove if not control else oldMove

    else:
        lastMove = None
        print("MIN")
        for legalMove in board.legal_moves:
            control = False
            oldBeta = beta
            oldMove = lastMove
            if board.is_capture(legalMove):
                capture = board.piece_type_at(legalMove.to_square)
            board.push(legalMove)
            print("min")
            valueAux = minimax(board, depth - 1, True, alfa, beta, legalMove, capture)
            print(f"{valueAux}, min")
            input()
            if beta < valueAux[0]:
                board.pop()
            else:
                beta = valueAux[0]
                lastMove = board.pop()
            if beta <= alfa:
                print(f"beta: {beta}, alfa: {alfa}, lastMove: {lastMove}, oldBeta: {oldBeta}, oldMove: {oldMove}, min")               
                control = True
                break
        return beta if not control else oldBeta, lastMove if not control else oldMove

# def minimax(board, depth, maximizing_player, move=None, capture=None):
#     if depth == 0 or board.is_game_over():
#         return evaluate(board, move, capture), board.peek()

#     if maximizing_player:
#         lastMove = None
#         value = float("-inf")
#         for legalMove in board.legal_moves:
#             if board.is_capture(legalMove):
#                 capture = board.piece_type_at(legalMove.to_square)
#             board.push(legalMove)
#             valueAux = minimax(board, depth - 1, False, legalMove, capture)
#             if value > valueAux[0]:
#                 board.pop()
#             else:
#                 value = valueAux[0]
#                 lastMove = board.pop()
#         return value, lastMove

#     else:
#         lastMove = None
#         value = float("inf")
#         for legalMove in board.legal_moves:
#             if board.is_capture(legalMove):
#                 capture = board.piece_type_at(legalMove.to_square)
#             board.push(legalMove)
#             valueAux = minimax(board, depth - 1, True, legalMove, capture)
#             if value < valueAux[0]:
#                 board.pop()
#             else:
#                 value = valueAux[0]
#                 lastMove = board.pop()
#         return value, lastMove

# Play
def play():
    while (not board.is_game_over()):
        if(board.turn == chess.WHITE):
            board.push(minimax(board, 2, True)[1])
            print("WHITE")
        else:
            # board.push(minimax(board, 6, True)[1])
            # board.push(jogadas.pop())
            # print(board.legal_moves)

            jogada = input()
            board.push_san(jogada)

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

jogadas = [chess.Move(chess.E2, chess.D1), chess.Move(chess.H6, chess.E2), chess.Move(chess.F8, chess.H6), chess.Move(chess.G7, chess.G6)]

board = chess.Board(fen="rnbqkbnr/pp2pppp/2p5/3p4/4N3/8/PPPPPPPP/R1BQKBNR w KQkq d6 0 3")

# print(board.pieces(chess.PAWN, chess.WHITE))
# board.push_san("e4")
# board.push_san("e5")
# board.push_san("Qh5")
# board.push_san("Nc6")
# board.push_san("Bc4")
# board.push_san("Nf6")

print(f'\n\n Que comecem os jogos \n\n')
jogada = play()
print(f'F I N A L - {jogada}')
print(f'{board} \n')
