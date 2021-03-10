import chess
import random
import numpy as np
import time
import threading


def jogar():
    while (not board.is_game_over()):
        if(board.turn == chess.WHITE):
            legalMoves = []
            for move in board.legal_moves:
                legalMoves.append(move)
            board.push(random.choice(legalMoves))
        else:
            legalMoves = []
            for move in board.legal_moves:
                legalMoves.append(move)
            board.push(random.choice(legalMoves))

    if board.is_stalemate():
        return 0
    if board.is_checkmate():
        return 1
    if board.is_insufficient_material():
        return 2
    if board.is_seventyfive_moves():
        return 3 
    if board.is_fivefold_repetition():
        return 4

def funcao(parametro):
    print(parametro)

board = chess.Board()
vitoria = [0,0,0,0,0]
try: threading._start_new_thread(funcao, ("tela",))
except: print("F")

# for jogos in range(1000):
#     print(jogos)
#     board.reset()
#     vitoria[jogar()] += 1

print(vitoria)

