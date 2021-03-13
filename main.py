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

def minimax_alfabeta(jogo, turno_max, jogador, profundidade_maxima = 8, alfa = float("-inf"), beta = float("inf")):
  # se o jogo acabou ou se a profundidade é máxima
  if jogo.venceu() or jogo.empate() or profundidade_maxima == 0:
    return jogo.calcular_utilidadex(jogador)

  if turno_max: # turno do MAX
    for proximo_jogo in jogo.jogos_validos():
      utilidade = minimax_alfabeta(jogo.jogar(proximo_jogo), False, jogador, profundidade_maxima - 1, alfa, beta)
      alfa = max(utilidade, alfa)
      if beta <= alfa:
        break
      return alfa
  else: # turno no MIN
    for proximo_jogo in jogo.jogos_validos():
      utilidade = minimax_alfabeta(jogo.jogar(proximo_jogo), True, jogador, profundidade_maxima - 1, alfa, beta)
      beta = min(utilidade, beta)
      if beta <= alfa:
        break
      return beta

def minimax(board, depth, maximizing_player, alfa = float("-inf"), beta = float("inf")):
    if depth == 0 or board.is_game_over():
        return evaluate(board), board.peek()

    if maximizing_player:
        lastMove = None
        for move in board.legal_moves:
            board.push(move)
            valueAux = minimax(board, depth - 1, False, alfa, beta)
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
            valueAux = minimax(board, depth - 1, True, alfa, beta)
            if beta <= alfa:
            	board.pop()
            	break
            if beta < valueAux[0]:
                board.pop()
            else:
                beta = valueAux[0]
                lastMove = board.pop()
        return beta, lastMove


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
