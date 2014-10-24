import pygame
from pygame.locals import *
import numpy as np
import os
import time
import threading

from exceptions import NoMoveException, EndGameException

class OthelloGame(object):

  HUMAN_MOVE = 0
  BOT_MOVE   = 1
  HUMAN_WIN  = 2
  BOT_WIN    = 3
  DRAW_GAME  = 4

  MESSAGES = {
    HUMAN_MOVE: "Human Turn",
    BOT_MOVE:   "Bot Turn",
    HUMAN_WIN:  "Human Win!",
    BOT_WIN:    "Bot Win!",
    DRAW_GAME:  "Draw game!"
  }

  def __init__(self, board, bot, human_color):
    # Pygame Settings
    self.size = (600, 640)
    self.clock = pygame.time.Clock()
    self.clock_hz = 30
    self.ok = True
    self.offset_x = 20
    self.offset_y = 70
    self.place_size = 70
    self.text_font = None

    # Game Settings
    self.board = board
    self.bot = bot
    self.last_bot_move = self.bot.NOPE_MOVE

    self.human_color = human_color
    self.bot_color = self.bot.opposity_color( self.human_color )

    self.human_moves = []
    self.bot_moves = []
    self.state = self.HUMAN_MOVE

    self.end_score = False

    self.no_move_flag = True

    # Bot Executor
    self.bot_thread = None

  # ################################################
  # Draw Functions

  def draw_board(self):
    for x in xrange(0,8):
      for y in xrange(0,8):
        x_pos = (x * self.place_size) + self.offset_x
        y_pos = (y * self.place_size) + self.offset_y

        place = pygame.Rect( (x_pos, y_pos), (self.place_size, self.place_size) )
        pygame.draw.rect( self.gameDisplay, (235, 248, 236, 1), place, 1 )

  def draw_board_pieces(self):
    for idx, place in enumerate( self.board ):

      x = (idx % 8) * self.place_size + self.offset_x + self.place_size / 2
      y = (idx / 8) * self.place_size + self.offset_y + self.place_size / 2

      if place == self.bot.WHITE:
        pygame.draw.circle( self.gameDisplay, (255,255,255), ( x, y ), 30 )
      elif place == self.bot.BLACK:
        pygame.draw.circle( self.gameDisplay, (0,0,0), ( x, y ), 30 )

  def draw_possible_moves(self):
    if self.state == self.HUMAN_MOVE:
      for position in self.human_moves:

        x = position[0] * self.place_size + self.offset_x + self.place_size / 2
        y = position[1] * self.place_size + self.offset_y + self.place_size / 2

        pygame.draw.circle( self.gameDisplay, (147,147,147), ( x, y ), 30 )

  def draw_text(self, text, position):
    label = self.text_font.render(text, 1, (255,255,255))
    label_rect = label.get_rect()
    label_rect.topleft = position

    self.gameDisplay.blit( label, label_rect )

  def draw_messages(self):

    score_black, score_white = self.bot.count_board_score( self.board )

    self.draw_text("Current Score", (20, 10))
    self.draw_text("WHITE: %d" % score_white, (20, 30))
    self.draw_text("BLACK: %d" % score_black, (20, 45))

    message_position = ( self.size[0] - 120, 30 )

    if self.end_score:
      self.draw_text( self.MESSAGES[ self.validate_score(score_black, score_white) ], message_position )
    else:
      self.draw_text( self.MESSAGES[ self.state ], message_position )

  def draw_alert_message(self, message):
    self.draw_text( message, (200, 10) )

  # ################################################
  # Logic Functions

  def validate_score(self, score_black, score_white):
    if score_white > score_black :
      return self.BOT_WIN
    elif score_black > score_white:
      return self.HUMAN_WIN
    else:
      return self.DRAW_GAME

  # def opposity_player(self):
    # return self.HUMAN_MOVE if self.state == self.BOT_MOVE else self.BOT_MOVE

  def listen_bot_movement(self):
    if self.state == self.BOT_MOVE:

      if self.bot_thread == None:
        self.bot_thread = threading.Thread( target = self.execute_bot_movement )

      if not self.bot_thread.is_alive():
        self.bot_thread.start()

  def execute_bot_movement(self):
    if self.state == self.BOT_MOVE:

      self.bot_moves = self.bot.list_moves( self.board, self.bot_color )

      if self.bot_moves.size == 0:

        if self.no_move_flag:
          self.end_score = True

        self.no_move_flag = True
        print "No bot move"
        self.state = self.HUMAN_MOVE

      else:
        self.no_move_flag = False

        self.last_bot_move = self.bot.play( self.board, self.bot_color )

        self.bot.set_color_position( self.board, self.last_bot_move, self.bot_color )

      # Change player to human
      self.state = self.HUMAN_MOVE
      self.update_human_movements()

      # Clean the thead holder
      self.bot_thread = None

  def update_human_movements(self):
    self.human_moves = self.bot.list_moves( self.board, self.human_color )

    # If no moves available,
    # change player to bot
    if self.human_moves.size == 0:

      if self.no_move_flag:
        self.end_score = True

      self.no_move_flag = True
      print "No human move"
      self.state = self.BOT_MOVE

    else:
      self.no_move_flag = False

  def process_event(self, event):
    if self.state == self.HUMAN_MOVE:

      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        click_position = event.pos

        click_position = np.array( click_position )
        click_position -= (self.offset_x, self.offset_y)
        click_position /= self.place_size

        if click_position.tolist() in self.human_moves.tolist():

          self.bot.set_color_position( self.board, click_position, self.human_color )
          self.state = self.BOT_MOVE

  def start(self):
    pygame.init()
    pygame.font.init()

    self.gameDisplay = pygame.display.set_mode( self.size )
    self.gameDisplay.fill( (55,117,177) )

    pygame.display.set_caption("Othello VideoGame")

    self.update_human_movements()

    self.text_font = pygame.font.Font("%s/assets/ubuntumono.ttf" % os.path.dirname(os.path.abspath(__file__)), 18)

    while self.ok:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.ok = False

        # Process the human click if is
        # its turn
        self.process_event( event )

      # try:

      # Display update
      self.gameDisplay.fill( (55,117,177) )
      self.draw_board()
      self.draw_board_pieces()
      self.draw_possible_moves()
      self.draw_messages()

      # Execute the bot movevent if is
      # its turn
      self.listen_bot_movement()

      # except EndGameException as e1:
      #   self.ok = False
      #   self.end_score = True

      pygame.display.update()
      self.clock.tick( self.clock_hz )

      if self.end_score: break

    if self.end_score:
      print "End game"

    while self.end_score:

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.end_score = False

      self.gameDisplay.fill( (55,117,177) )
      self.draw_board()
      self.draw_board_pieces()
      self.draw_messages()

      pygame.display.update()
      self.clock.tick( self.clock_hz )

    pygame.quit()

