
import numpy as np
import time

class DunkBot(object):
  """
  DunkBot

  A bot that plays Othello Game
  """

  # Constant declarations

  # Color types
  COLOR_BLACK = "black"
  COLOR_WHITE = "white"

  # Color type on board
  WHITE = 'W'
  BLACK = 'B'
  EMPTY = '.'

  # None movement
  NOPE_MOVE = np.array((-1,-1))

  # Available actions
  ACTIONS = [
    np.array( [  0, -1] ), # UP
    np.array( [  0,  1] ), # DOWN
    np.array( [ -1,  0] ), # LEFT
    np.array( [  1,  0] ), # RIGHT
    np.array( [ -1, -1] ), # UP_LEFT
    np.array( [  1, -1] ), # UP_RIGHT
    np.array( [ -1,  1] ), # DOWN_LEFT
    np.array( [  1,  1] ), # DOWN_RIGHT
  ]

  # Position modifier for each position
  # on the board
  POSITION_MODIFIER = np.array([
     4, -4,  2,  2,  2,  2, -4,  4,
    -4, -4,  0,  0,  0,  0, -4, -4,
     2,  0,  0,  0,  0,  0,  0,  2,
     2,  0,  0,  0,  0,  0,  0,  2,
     2,  0,  0,  0,  0,  0,  0,  2,
     2,  0,  0,  0,  0,  0,  0,  2,
    -4, -4,  0,  0,  0,  0, -4, -4,
     4, -4,  2,  2,  2,  2, -4,  4
  ])

  def __init__(self, max_depth = 4):
    """
    Dunk Constructor

    Params:
      max_depth   : Max depth of MiniMax search

    Defaults:
      max_depth   : 4
    """

    self.max_depth = max_depth

    print "Init with max depth: ",  self.max_depth

  @property
  def max_depth(self):
    return self._max_depth

  @max_depth.setter
  def max_depth(self, value):
      self._max_depth = value

  def opposity_color(self, color):
    '''
    Return the opposity color for the
    given color

    Params:
      color : Color to be switched

    Return:
      Opposity color
    '''

    color_change = {
      self.WHITE: self.BLACK,
      self.BLACK: self.WHITE
    }

    return color_change[ self.transform_color( color ) ]

  def transform_color(self, color):
    '''
    Transform a color to internal representation
    on the board

    Params:
      color : Color string the be converted

    Return:
      Internal representation of the color
    '''

    color_poll = {
      self.WHITE: self.WHITE,
      self.BLACK: self.BLACK,
      self.COLOR_WHITE: self.WHITE,
      self.COLOR_BLACK: self.BLACK
    }

    return color_poll[ color ]

  def print_board(self, board):
    '''
    Pretty print a board

    Params:
      board : Board to be printed
    '''

    print board.reshape((8,8))

  def count_board_score(self, board):
    '''
    Count the current score for each color

    Params:
      board : Board used to count the score

    Return:
      Tuple with the current score with
      black points followed by white points

      (score_black, score_white)
    '''

    score_black = 0
    score_white = 0

    for place in board:
      if place == self.BLACK:
        score_black += 1
      elif place == self.WHITE:
        score_white += 1

    return score_black, score_white

  def get_value(self, board, x, y):
    '''
    Get the value of a position on a board

    Can raise a IndexError if the index is
    outside the range of (0-7)

    Params:
      board : Board to get the value
      x     : X position on the board
              Range (0-7)
      y     : Y position on the board
              Range (0-7)

    Return:
      The value of the position on the board
    '''

    if not (0 <= x <= 7 and 0 <= y <= 7):
        raise IndexError

    return board[ x + y * 8 ]

  def set_value(self, board, x, y, value):
    '''
    Set a value to a position on the board

    Can raise a IndexError if the index is
    outside the range of (0-7)

    Params:
      board : Board to set the value
      x     : X position on the board
              Range (0-7)
      y     : Y position on the board
              Range (0-7)
      value : Value to be setted
    '''

    if not (0 <= x <= 7 and 0 <= y <= 7):
        raise IndexError

    board[ x + y * 8 ] = value

  def get_color_positions(self, board, color):
    '''
    Return a list of position of a determined color

    Params:
      board : Board to search the color
      color : Color to be searched

    Return:
      List of positions of the passed color on the
      board
    '''

    color_positions = []

    for idx, place in enumerate( board ):
        if place == color:
            x = idx % 8
            y = idx / 8

            color_positions.append( np.array([x, y]) )

    return color_positions

  def set_color_position(self, board, position, color):
    '''
    Change all pieces on the board that are vertical,
    horizontal or diagonal with the passed position

    Params:
      board    : Board where the pieces will be changed
      position : Final position used as anchor for
                 changing
      color    : Color to be setted on the board
    '''

    if (position == self.NOPE_MOVE).all(): return

    for action in self.ACTIONS:

      test_position = position + action

      while True:
        try:
          local_state = self.get_value( board, *test_position )

          if local_state == color:

            self.set_color_direction(
              board = board,
              base_position = position,
              final_position = test_position,
              action = action,
              color = color
            )

            break

          elif local_state == self.EMPTY:
            break

          test_position += action

        except IndexError, e:
            break


  def set_color_direction(self, board, base_position, final_position, action, color):
    '''
    Set color to the board in the direction of the action
    from the base_position until reach the final_position

    Params:
      board          : Board where the color will be setted
      base_position  : Starting position for changing
      final_position : End position for changing
      action         : Action used to move on the board
      color          : Color to be setted
    '''

    current_pos = base_position

    while True:
        x, y = current_pos

        self.set_value(
            board = board,
            x = x,
            y = y,
            value = color
        )

        if (current_pos == final_position).all():
            break

        current_pos = current_pos + action

  def calculate_score(self, parent, board, move):
    '''
    Calculate the score of a board based on the amount
    of changed pieces and the position modifier

    Params:
      parent : Parent node from of the current node
      board  : Board of the current node
      move   : Movement used the change from Parent to
               current node

    Return:
      The calculated score of the board
    '''

    score = 0

    if parent:
        diff = parent["board"] != board

        score = 0
        score += np.count_nonzero( diff ) - 1
        score += self.get_value( self.POSITION_MODIFIER, *move )

    return score

  def create_node(self, board, parent, action, move):
    '''
    Create a new node based the new board

    Params:
      board  : New created board that this node will
               represent
      parent : Parent node from the current node was
               originated
      action : Action used the create the new node
      move   : Final position where the new pieces
               will be placed

    Return:
      The new node
    '''

    node = {
        "board": board,
        "parent": parent,
        "action": action,
        "move": move,
        "score": self.calculate_score( parent, board, move ),
        "depth": parent["depth"] + 1 if parent else 0
    }

    return node

  def execute_action(self, base_position, board, action, current_color):
    '''
    Test if a action movement based on a position and color is valid

    Params:
      base_position : Starting position to init the movement
      board         : Board where the movement will be tested
      action        : Action used to move on the board
      current_color : Color used in the test

    Return:
      A tuple with two values:
        valid         : True if is a valid movement, False otherwise
        test_position : Final position where a piece can be placed
    '''

    other_color = self.opposity_color(current_color)
    test_position = base_position + action
    cover = False
    valid = False

    while True:
      try:
        local_state = self.get_value( board, *test_position )

        if local_state == other_color:
          cover = True

        elif local_state == current_color:
          break

        elif local_state == self.EMPTY and cover:
          valid = True
          break

        else:
          break

        test_position += action

      except IndexError, e:
          break

    return valid, test_position

  def expand(self, node, color):
    '''
    Exapnd a node based on a color. Create all valid new board
    derived from the base node board

    Params:
      node  : Node to be expanded
      color : Color used to expand the current board

    Return:
      List of valid nodes expanded from the base node
    '''

    result_list = []

    color_positions = self.get_color_positions( node["board"], color )

    for base_position in color_positions:

      for action in self.ACTIONS:

        valid, final_position = self.execute_action(
          base_position = base_position,
          board = node["board"],
          action = action,
          current_color = color
        )

        if valid:

          new_board = node["board"].copy()

          self.set_color_position(
            board = new_board,
            position = final_position,
            color = color
          )

          result_list.append(
            self.create_node(
              board = new_board,
              parent = node,
              action = action,
              move = final_position
            )
          )

    return result_list

  # MiniMax Alpha-Beta Implementation

  def select_move( self, root_node, color ):
    '''
    Select the best movement based on the current board
    and color. Applies the MiniMax Alpha-Beta algorithm
    to select the movement.

    Params:
      root_node : Base node to be used on search
      color     : Color side to search the best movement

    Return:
      The best movement available after the search
    '''

    value, node = self.select_max_value(
      node = root_node,
      color = color,
      alpha = float("-inf"),
      beta = float("inf")
    )

    return node["move"] if node else self.NOPE_MOVE

  def select_max_value( self, node, color, alpha, beta ):
    '''
    Max value search part of the MiniMax Alpha-Beta search

    Params:
      node  : Base node on the Max value search
      color : Color to expand on the board
      alpha : The best Max Value
      beta  : The best Min Value

    Return:
      A tuple with two values:
        alpha : Best Max Value
        node  : Best node on the current search
    '''

    if node["depth"] == self.max_depth:
      return node["score"], node

    expand_list = self.expand(
      node = node,
      color = color
    )

    expand_list.sort( key=lambda node: node["score"] )
    expand_list.reverse()

    other_color = self.opposity_color( color )

    best_node = None

    for child_node in expand_list:

      min_value, min_node = self.select_min_value(
        node = child_node,
        color = other_color,
        alpha = alpha,
        beta = beta
      )

      if min_value > alpha:
        alpha = min_value

        if node["depth"] == 0:
          best_node = child_node

      if alpha >= beta:
        break

    return alpha, best_node

  def select_min_value( self, node, color, alpha, beta ):
    '''
    Min value search part of the MiniMax Alpha-Beta search

    Params:
      node  : Base node on the Max value search
      color : Color to expand on the board
      alpha : The best Max Value
      beta  : The best Min Value

    Return:
      A tuple with two values:
        beta : Best Min Value
        node  : Best node on the current search
    '''

    if node["depth"] == self.max_depth:
      return node["score"], node

    expand_list = self.expand(
      node = node,
      color = color
    )

    expand_list.sort( key=lambda node: node["score"] )

    other_color = self.opposity_color( color )

    best_node = None

    for child_node in expand_list:

      max_value, max_node = self.select_max_value(
        node = child_node,
        color = other_color,
        alpha = alpha,
        beta = beta
      )

      if max_value < beta:
        beta = max_value

        if node["depth"] == 0:
          best_node = child_node

      if beta <= alpha:
        break

    return beta, best_node

  def list_moves( self, board, color ):
    '''
    List all available movements based on
    the board and color

    Params:
      board : Base board
      color : Color the list the movements

    Return:
      List of available movements
    '''

    color = self.transform_color( color )

    source_node = self.create_node(
      board = board,
      parent = None,
      action = None,
      move = None
    )

    expand_list = self.expand(
      node = source_node,
      color = color
    )

    return np.array( [ node["move"] for node in expand_list ] )

  def play( self, board, color ):
    '''
    Entry point for the bot thinking process

    Params:
      board : Base board where the bot will search
              the best movement
      color : Color which the bot must search for

    Return:
      The best movement for the color
    '''

    color = self.transform_color( color )

    root_node = self.create_node(
      board = board,
      parent = None,
      action = None,
      move = None
    )

    start = time.clock()

    move = self.select_move( root_node, color )

    time_lapse = time.clock() - start
    print "Time lapse: ", time_lapse

    return move
