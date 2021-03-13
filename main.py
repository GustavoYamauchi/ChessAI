
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


def evaluate(board):
    
    vWhite = 0
    vBlack = 0
    for piece in board.piece_map().values():
        if piece.color == chess.BLACK:
            vBlack += pieces[piece.piece_type]
        else:
            vWhite += pieces[piece.piece_type]

    # print(f'White = {vWhite} - Black = {vBlack} \n')
    #StartGame -> Logica de Inicio

    #MidGame -> Preço das peças
        
    #FinalGame -> Algoritmos de Vitoria
    return vWhite - vBlack

def populateTree(fen, depth):
    if depth == 0:
        return evaluate()

    legalMoves = list(board.legal_moves)
    tree[fen] = legalMoves
    for move in legalMoves:
        board.push(move)
        populateTree(board.fen(), depth - 1)
        board.pop()

def minimax(board, depth, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate(board), board.peek()

    if maximizing_player:
        value = -float('inf')
        lastMove = None
        for move in board.legal_moves:
            board.push(move)
            valueAux = minimax(board, depth - 1, False)
            if value > valueAux[0]:
                board.pop()
            else:
                value = valueAux[0]
                lastMove = board.pop()
        return value, lastMove

    else:
        value = float('inf')
        lastMove = None
        for move in board.legal_moves:
            board.push(move)
            valueAux = minimax(board, depth - 1, True)
            if value < valueAux[0]:
                board.pop()
            else:
                value = valueAux[0]
                lastMove = board.pop()
        return value, lastMove


def jogar():
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
        return "Stalmate"
    if board.is_checkmate():
        return "Checkmate"
    if board.is_insufficient_material():
        return "Insufficiente Material"
    if board.is_seventyfive_moves():
        return "SeventyFive"
    if board.is_fivefold_repetition():
        return "FiveFold"


board = chess.Board()
board.push_san("e4")
board.push_san("e5")
board.push_san("Qh5")
board.push_san("Nc6")
print(f'\n\n Que comecem os jogos \n\n')
jogada = jogar()
print(f'F I N A L - {jogada}')
print(f'{board} \n')

# populateTree(board.fen(), 1)
# print(tree)


