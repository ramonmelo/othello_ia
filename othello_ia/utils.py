
import numpy as np

def convert_board_from_file( board_file ):

    board_txt = board_file.read()
    board_file.close()

    board_txt = board_txt.replace("\n", "")
    board = np.array( [token for token in board_txt] )

    return board

def write_move(move):

    output = open("move.txt", "w")
    output.write( "%i,%i" % tuple(move) )
    output.close()
