import chess
import random
import re
import numpy as np
from chessUtils import pieceSquareValue
from chessUtils import pieceValues
from chessUtils import piecesToInitialPositions

# Define PHASE
def measureGamePhases(board):
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

def captureEvaluate(board): 
    value = 0
    move = board.pop()
    if board.is_capture(move):
        value = pieceValues[board.piece_type_at(move.to_square)]
    board.push(move)

    return value

def boardValueEvaluate(board):
    vWhite = 0
    vBlack = 0
    for piece in board.piece_map().values():
        if piece.color == chess.BLACK:
            vBlack += pieceValues[piece.piece_type]
        else:
            vWhite += pieceValues[piece.piece_type]

    if board.turn != chess.BLACK:
        return vBlack - vWhite
    else:
        return vWhite - vBlack

def genericPieceEvaluate(board, move, validPieces):
    pieceType = board.piece_type_at(move.to_square)
    if not pieceType in validPieces:
        return False

# Phase 0 (earlyGame)
def devMinorsEvaluate(board):
    move = board.peek()
    if genericPieceEvaluate(board, move, {chess.KNIGHT, chess.BISHOP}): return 0
    
    pieceType = board.piece_type_at(move.to_square)
    if (board.turn == chess.BLACK):
        positions = pieceSquareValue[pieceType][::-1]
        return positions[move.to_square]
    return pieceSquareValue[pieceType][move.to_square]

def rookEvaluate(board):
    move = board.peek()
    # if (board.piece_type_at(move.to_square) != chess.ROOK):
        # return 0
    if genericPieceEvaluate(board, move, {chess.ROOK}): return 0

    positions = pieceSquareValue[chess.ROOK]
    if (board.turn == chess.BLACK):
        positions = pieceSquareValue[chess.ROOK][::-1]

    return 70 if board.is_castling(move) else positions[move.to_square]

def devPawnsEvaluate(board):
    move = board.peek()
    # if board.piece_type_at(move.to_square) != chess.PAWN:
        # return 0
    if genericPieceEvaluate(board, move, {chess.PAWN}): return 0
    if board.turn == chess.BLACK:
        positionsPawns = pieceSquareValue[chess.PAWN][::-1]
        return positionsPawns[move.to_square]

    return pieceSquareValue[chess.PAWN][move.to_square]


def suicideCaptureEvaluate(board):
    move = board.pop()
    value = 0

    turn = chess.WHITE if board.turn == chess.BLACK else chess.BLACK
    if len(board.attackers(turn, move.to_square)) > 0:
        value = -pieceValues[board.piece_type_at(move.from_square)]
    
    board.push(move)
    return value

# Evaluate de checkmate
# Evaluate de check não garantido

# Evaluate
def evaluate(board):
    value = 0
    phase = measureGamePhases(board)
    weight = [
        {"capture": 1.3, "boardValue": 1.4, "devMinors" : 1.45, "rook" : 1.0, "devPawns" : 1.7, "suicide" : 1.0},
        {"capture": 1.6, "boardValue": 1.4, "devMinors" : 1.45, "rook" : 1.0, "devPawns" : 1.7, "suicide" : 1.0},
        {"capture": 1.3, "boardValue": 1.4, "devMinors" : 1.45, "rook" : 1.0, "devPawns" : 1.7, "suicide" : 1.0}
    ]

    value += captureEvaluate(board) * weight[phase]["capture"]
    value += boardValueEvaluate(board) * weight[phase]["boardValue"]
    value += devMinorsEvaluate(board) * weight[phase]["devMinors"]
    value += rookEvaluate(board) * weight[phase]["rook"]
    value += devPawnsEvaluate(board) * weight[phase]["devPawns"]
    value += suicideCaptureEvaluate(board)  * weight[phase]["suicide"]
    
    move = board.peek()
    positions = pieceSquareValue[board.piece_type_at(move.to_square)]

    if board.turn == chess.BLACK:
        positions = positions[::-1]
    
    return value + positions[move.to_square]

def minimax(board, depth, maximizing, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 or board.is_game_over():
        score = evaluate(board)
        return score, board.peek()
        
    bestScore = float('-inf') if maximizing else float('inf')
    bestMove = None
    for legalMove in board.legal_moves:
        board.push(legalMove)
        maxDepthStateScore, maxDepthBestMove = minimax(board, depth -1, not maximizing, alpha, beta)  
        board.pop()

        if maximizing:
            bestScore = max(bestScore, maxDepthStateScore)
            bestMove = legalMove
            alpha = max(alpha, bestScore)

            
        else:
            bestScore = min(bestScore, maxDepthStateScore)
            bestMove = legalMove
            beta = min(beta, bestScore)
        
        if beta <= alpha:
            break

    return bestScore, bestMove

# Play
def move(board, isWhite, player):
    
    choosedMove = None
    turn = "Branco" if isWhite else "Preto"
    if not player:
        globalScore = float('-inf') if isWhite else float('inf')

        scores = []
        for legalMove in board.legal_moves:
            board.push(legalMove)
            maxDepthStateScore, maxDepthBestMove = minimax(board, 2, not isWhite)
            scores.append((str(legalMove), maxDepthStateScore))
            board.pop()

            if isWhite and globalScore < maxDepthStateScore:
                globalScore = maxDepthStateScore
                choosedMove = legalMove

                
            elif not isWhite and globalScore > maxDepthStateScore:
                globalScore = maxDepthStateScore
                choosedMove = legalMove

        # print(f"Movimento escolhido: {choosedMove}")
        # print(f"Movimentos: {scores}")
        # print(f"Pontuação máxima: {globalScore}")
        # print(f"Jogador: {turn}")

    else:
        while choosedMove == None:
            print(f"Jogadas possíveis: {board.legal_moves}")
            print("Qual sua jogada?")
            try:
                receivedMove = board.parse_san(input())
                if receivedMove in board.legal_moves:
                    choosedMove = receivedMove   
            except ValueError:
                print("Jogada invalida.")
                print()

    print()
    print(f"Jogada da IA ({turn}): {choosedMove}") if not player else print(f"Sua Jogada: {choosedMove}")
    board.push(choosedMove)

def play():
    board = chess.Board()
    controlePlayer = [False, False]
    while True:
        print("Qual cor você será? (0 - Branco, 1 - Preto, 2 - Nenhum)")
        try:
            option = int(input())
            if not option == 2:
                controlePlayer[option] = True
            break
        except IndexError:
            print("Opção inválida.")
        except TypeError:
            print("Opção inválida.")

    print(f'\n Que comecem os jogos \n')
    
    while not board.is_game_over():
        if(board.turn == chess.WHITE):
            move(board, True, controlePlayer[0])
        else:
            move(board, False, controlePlayer[1])
    
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
    return "Unkown Victory"

jogada = play()
print(jogada)