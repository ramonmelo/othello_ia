
import sys
import utils
from dunk_bot.dunk_bot import DunkBot
from video_game.game_player import OthelloGame
import os

def run( args ):
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    board_file = open( "%s/video_game/assets/board" % curr_dir, "r")
    color = "black"

    # Convert the text value to a
    # matrix instance of the board
    board = utils.convert_board_from_file( board_file )

    # Create the BOT
    bot = DunkBot( max_depth = 5 )

    # Start the Video Game
    video_game = OthelloGame( board, bot, bot.transform_color( color ) )
    video_game.start()

if __name__ == "__main__":
    run( sys.argv )

