
import sys
import utils
from dunk_bot.dunk_bot import DunkBot

import time

def run( args ):
    board_file = None
    color = None

    # Read the input arguments
    try:
        board_file = open( args[1], "r")
        color = args[2]

        print "Input OK"
    except Exception, e:
        print "Input error"
        return

    # Convert the text value to a
    # matrix instance of the board
    board = utils.convert_board_from_file( board_file )

    # Play the game!
    nope_move = DunkBot.NOPE_MOVE
    last_move = nope_move

    total_time = 0.0

    for depth in xrange(3, 6):
        print "--------------------------------"
        print "New try..."

        start = time.clock()

        bot = DunkBot( max_depth = depth )
        move = tuple( bot.play( board, color ) )

        if (move == nope_move).all() and (last_move != nope_move).all():
            move = last_move

        print "Selected move: ", move

        utils.write_move( move )

        total_time += time.clock() - start

        print "Total time: ", total_time
        if total_time > 4: break

        last_move = move

if __name__ == "__main__":
    run( sys.argv )


