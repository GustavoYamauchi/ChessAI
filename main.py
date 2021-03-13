
import chess
import random
import numpy as np



# arvorezada 
tree = {}

# peças
pieces = {
    chess.PAWN: 100,
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}


def evaluate():
    


    #StartGame -> Logica de Inicio

    #MidGame -> Preço das peças
        
    #FinalGame -> Algoritmos de Vitoria
    return 0

def populateTree(fen, depth):
    if depth == 0:
        return

    legalMoves = list(board.legal_moves)
    tree[fen] = legalMoves
    for move in legalMoves:
        board.push(move)
        populateTree(board.fen(), depth - 1)
        board.pop()

board = chess.Board()
populateTree(board.fen(), 3)
print(tree)
# def minimax(board, depth, maximizing_player):
#     if depth == 0 or board.is_game_over():
#         return evaluate(board)
#     if maximizing_player:
#         value = -float('inf')
#         for move in board.legal_moves:
#             board.push(move)
#             value = max(value, minimax(board, depth - 1, False))
#             board.pop()
#         return value
#     else:
#         value = float('inf')
#         for move in board.legal_moves:
#             board.push(move)
#             value = min(value, minimax(board, depth - 1, True))
#             board.pop()
#         return value


# def jogar():
#     while (not board.is_game_over()):
#         if(board.turn == chess.WHITE):
#             legalMoves = list(board.legal_moves)
#             board.push(random.choice(legalMoves))
#         else:
#             legalMoves = list(board.legal_moves)
#             board.push(random.choice(legalMoves))

#     if board.is_stalemate():
#         return 0
#     if board.is_checkmate():
#         return 1
#     if board.is_insufficient_material():
#         return 2
#     if board.is_seventyfive_moves():
#         return 3
#     if board.is_fivefold_repetition():
#         return 4


# board = chess.Board()
# vitoria = [0, 0, 0, 0, 0]


# for jogos in range(1000):
#     print(jogos)
#     board.reset()
#     vitoria[jogar()] += 1

# print(vitoria)
