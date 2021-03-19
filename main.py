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

    p = []
    if board.ply() >= 12:
        points += 100 * 1.5
    p.append(points)

    if len(lstPieces.values()) <= 30:
        points += 100 * 1.5
    p.append(points)

    if len(re.findall("(n|r|b)", fen[0])) + len(re.findall("(N|R|B)", fen[7])) < 7:
        points += 100 * 1.5
    p.append(points)

    if points > 300:
        phase = 1
        if board.ply() >= 36:
            points += 100
    
        if len(lstPieces.values()) <= 16:
            points += 100 * 1.4
    
        if len(re.findall("(q|Q)", board.board_fen())) == 0:
            points += 100 * 1.7
    
        if len(re.findall("(q|Q)", board.board_fen())) == 1 and len(re.findall("(n|r|b|N|R|B)", board.board_fen())) < 3:
            points += 100 * 2.4
    
        if board.promoted != 0:
            points += 100 * 3
    
        match = 0
        for pieceType in ["n", "r", "b", "N", "R", "B"]:
            if len(re.findall(f"(pieceType)", board.board_fen())) > 1:
                match += 1
    
        if match < 2:
            points += 100 * 1.7
            
        if points > 1150:
            return 2

    return phase
# All Phases

def captureEvaluate(board): 
    value = 0
    move = board.pop()
    if board.is_capture(move):
        value = pieceValues[board.piece_type_at(move.to_square)]
    board.push(move)

    return value

def boardValueEvaluate(board, playerColor):
    vWhite = 0
    vBlack = 0
    
    for piece in board.piece_map().values():
        if piece.color == chess.BLACK:
            vBlack += pieceValues[piece.piece_type]
        else:
            vWhite += pieceValues[piece.piece_type]

    if playerColor != chess.BLACK:
        return vBlack - vWhite
    else:
        return vWhite - vBlack

def assertPieceType(board, move, validPieces):
    pieceType = board.piece_type_at(move.to_square)
    if pieceType in validPieces:
        return True
    return False

def getSquareValue(board, move):
    pieceType = board.piece_type_at(move.to_square)
    values = pieceSquareValue[pieceType][::-1] if board.turn == chess.BLACK else pieceSquareValue[pieceType]
    return values[move.to_square]

# Phase 0 (earlyGame)
def devMinorsEvaluate(board):
    move1 = board.pop()
    move2 = board.pop()
    relevantMove = board.peek()
    board.push(move2)
    board.push(move1)
    if not assertPieceType(board, relevantMove, {chess.KNIGHT, chess.BISHOP}): return 0
    return getSquareValue(board, relevantMove)

def rookEvaluate(board):
    move1 = board.pop()
    move2 = board.pop()
    relevantMove = board.peek()
    board.push(move2)
    board.push(move1)
    if not assertPieceType(board, relevantMove, {chess.ROOK}): return 0
    return 200 if board.is_castling(relevantMove) else getSquareValue(board, relevantMove)

def devPawnsEvaluate(board):
    move1 = board.pop()
    move2 = board.pop()
    relevantMove = board.peek()
    board.push(move2)
    board.push(move1)
    if not assertPieceType(board, relevantMove, {chess.PAWN}): return 0
    return getSquareValue(board, relevantMove)

def suicideCaptureEvaluate(board, playerColor):
    move1 = board.pop()
    move2 = board.pop()
    value = 0
    relevantMove = board.peek()
    if len(board.attackers(playerColor, relevantMove.to_square)) > 0:
        value = -(pieceValues[board.piece_type_at(relevantMove.to_square)])
    board.push(move2)
    board.push(move1)

    return value

def checkEvaluate(board, playerColor):
    isCheckmate = board.is_checkmate()
    if isCheckmate:
        if board.turn == playerColor:
            return float('inf')
        return float('-inf')
    return 0

def promoteEvaluate(board, playerColor):
    move = board.peek()
    if not assertPieceType(board, move, {chess.PAWN}): return 0
    row = move.to_square
    row += 8
    while row <= 63 and row >= 0:
        if board.piece_type_at(row) != None:
            return 0
        row += 8 * (-1 if playerColor == chess.BLACK else 1)
    return 900

# Evaluate
def evaluate(board, playerColor, weight):
    value = 0

    value += captureEvaluate(board) * weight["capture"]
    value += boardValueEvaluate(board, playerColor) * weight["boardValue"]
    value += devMinorsEvaluate(board) * weight["devMinors"]
    value += rookEvaluate(board) * weight["rook"]
    value += devPawnsEvaluate(board) * weight["devPawns"]
    value += suicideCaptureEvaluate(board, playerColor)  * weight["suicide"]
    value += checkEvaluate(board, playerColor)

    if weight["promote"] != 0:
        value += promoteEvaluate(board, playerColor) * weight["promote"]

    return value

def minimax(board, depth, maximizing, playerColor, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 or board.is_game_over():
        weight = [
            {"capture": 1.3, "boardValue": 1.1, "devMinors" : 1.45, "rook" : 1.2, "devPawns" : 1.45, "suicide" : 1.3, "promote" : 0},
            {"capture": 1.4, "boardValue": 1, "devMinors" : 1.6, "rook" : 1, "devPawns" : 1.3, "suicide" : 1.4, "promote" : 0.2},
            {"capture": 1.6, "boardValue": 1.4, "devMinors" : 1.7, "rook" : 1, "devPawns" : 1, "suicide" : 1.4, "promote" : 3}
        ]

        score = evaluate(board, playerColor, weight[measureGamePhases(board)])
        return score, board.peek()
        
    score = float('-inf') if maximizing else float('inf')
    bestMove = None
    for legalMove in board.legal_moves:

        if maximizing:
            board.push(legalMove)
            maxDepthStateScore, maxDepthBestMove = minimax(board, depth -1, False, playerColor, alpha, beta)  
            board.pop()
            score = max(score, maxDepthStateScore)
            bestMove = legalMove
            alpha = max(alpha, score)
            
        else:
            board.push(legalMove)
            maxDepthStateScore, maxDepthBestMove = minimax(board, depth -1, True, playerColor, alpha, beta)  
            board.pop()
            score = min(score, maxDepthStateScore)
            bestMove = legalMove
            beta = min(beta, score)
        
        if beta <= alpha:
            break

    return score, bestMove    

# Play
def move(board, playerColor, player):
    chosenMove = None
    turn = "Branco" if board.turn == chess.WHITE else "Preto"
    if not player:
        globalScore = float('-inf') if board.turn != playerColor else float('inf')

        scores = []
        for legalMove in board.legal_moves:
            board.push(legalMove)
            maxDepthStateScore, maxDepthBestMove = minimax(board, 2, False, playerColor)
            scores.append((str(legalMove), maxDepthStateScore))
            board.pop()

            if globalScore < maxDepthStateScore:
                globalScore = maxDepthStateScore
                chosenMove = legalMove

        # print(f"Movimento escolhido: {chosenMove}")
        # print(f"Movimentos: {scores}")
        # print(f"Pontuação máxima: {globalScore}")
        # print(f"Jogador: {turn}")

    else:
        while chosenMove == None:
            print(f"Jogadas possíveis: {board.legal_moves}")
            print("Qual sua jogada?")
            try:
                receivedMove = board.parse_san(input())
                if receivedMove in board.legal_moves:
                    chosenMove = receivedMove   
            except ValueError:
                print("Jogada invalida.")
                print()

    print()
    print(f"Jogada da IA ({turn}): {chosenMove}") if not player else print(f"Sua Jogada: {chosenMove}")
    board.push(chosenMove)

def play():
    board = chess.Board()
    while True:
        print("Qual cor você será? (0 - Branco, 1 - Preto)")
        try:
            option = int(input())
            playerColor = chess.BLACK if option == 1 else chess.WHITE
            break
        except IndexError:
            print("Opção inválida.")
        except TypeError:
            print("Opção inválida.")

    print(f'\n Que comecem os jogos \n')
    
    print(f'{board if playerColor == chess.WHITE else board.transform(chess.flip_vertical)} \n')
    while not board.is_game_over():
        if(board.turn == playerColor):
            move(board, playerColor, True)
        else:
            move(board, playerColor, False)
        print(f'{board if playerColor == chess.WHITE else board.transform(chess.flip_vertical)} \n')
    
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

# Contra o thiago
# "r1bqk1nr/pppp3p/5pp1/3Pp3/1b1nP3/2P5/PP3PPP/RNBQKBNR w KQkq - 0 1"