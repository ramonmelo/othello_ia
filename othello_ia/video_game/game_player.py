import pygame
from pygame.locals import *
import numpy as np
import os
import time
import threading

from exceptions import NoMoveException, EndGameException

class OthelloGame(object):

  HUMAN_MOVE = 0
  BOT_MOVE = 1

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
    self.human_color = human_color
    self.bot_color = self.bot.opposity_color( self.human_color )
    self.human_moves = None
    self.state = self.HUMAN_MOVE
    self.move_flag = True
    self.end_score = False

    # Bot Executor
    self.bot_thread = None

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

      if self.human_moves == None:
        self.human_moves = self.bot.list_moves( self.board, self.human_color )

      if self.human_moves != None and self.human_moves.size != 0:

        for position in self.human_moves:

          x = position[0] * self.place_size + self.offset_x + self.place_size / 2
          y = position[1] * self.place_size + self.offset_y + self.place_size / 2

          pygame.draw.circle( self.gameDisplay, (147,147,147), ( x, y ), 30 )

        self.move_flag = True

      else:

        self.state == self.BOT_MOVE

        if not self.move_flag:
          raise EndGameException

        self.move_flag = False

        # raise NoMoveException("Human has no moves")

  def draw_text(self, text, position):
    label = self.text_font.render(text, 1, (255,255,255))
    label_rect = label.get_rect()
    label_rect.topleft = position

    self.gameDisplay.blit( label, label_rect )

  def draw_messages(self):
    if self.text_font == None:
      font_file_name = "%s/assets/ubuntumono.ttf" % os.path.dirname(os.path.abspath(__file__))
      self.text_font = pygame.font.Font(font_file_name, 18)

    score_black, score_white = self.bot.count_board_score( self.board )

    self.draw_text("Current Score", (20, 10))
    self.draw_text("WHITE: %d" % score_white, (20, 30))
    self.draw_text("BLACK: %d" % score_black, (20, 45))

    message_position = ( self.size[0] - 120, 30 )

    if self.end_score:

      if score_black > score_white:
        self.draw_text("Human Win!", message_position )

      elif score_white > score_black:
        self.draw_text("Bot Win!", message_position )

      else:
        self.draw_text("Draw game!", message_position )

    else:

      if self.state == self.HUMAN_MOVE:
        self.draw_text("Human Turn", message_position )

      elif self.state == self.BOT_MOVE:
        self.draw_text("Bot Turn", message_position )

  def draw_alert_message(self, message):
    self.draw_text( message, (200, 10) )

  def opposity_player(self):
    return self.HUMAN_MOVE if self.state == self.BOT_MOVE else self.BOT_MOVE

  def listen_bot_movement(self):
    if self.state == self.BOT_MOVE:

      if self.bot_thread == None:
        self.bot_thread = threading.Thread( target = self.execute_bot_movement )

      if not self.bot_thread.is_alive():
        self.bot_thread.start()

  def execute_bot_movement(self):
    if self.state == self.BOT_MOVE:
      move = self.bot.play( self.board, self.bot_color )

      if move != None:
        self.bot.set_color_position( self.board, move, self.bot_color )

        # self.human_moves = None
        # self.move_flag = True
      # else:
        # if not self.move_flag:
          # raise EndGameException
        # self.move_flag = False

      self.state = self.HUMAN_MOVE
      self.bot_thread = None

  def process_event(self, event):

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
      click_position = event.pos

      click_position = np.array( click_position )
      click_position -= (self.offset_x, self.offset_y)
      click_position /= self.place_size

      if self.human_moves != None:
        if click_position.tolist() in self.human_moves.tolist():
          self.bot.set_color_position( self.board, click_position, self.human_color )
          self.state = self.BOT_MOVE

  def start(self):
    pygame.init()
    pygame.font.init()

    self.gameDisplay = pygame.display.set_mode( self.size )
    self.gameDisplay.fill( (55,117,177) )

    pygame.display.set_caption("Othello VideoGame")

    while self.ok:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.ok = False

        # Process the human click if is
        # its turn
        self.process_event( event )

      try:

        # Display update
        self.gameDisplay.fill( (55,117,177) )
        self.draw_board()
        self.draw_board_pieces()
        self.draw_possible_moves()
        self.draw_messages()

        # Execute the bot movevent if is
        # its turn
        self.listen_bot_movement()

      # except NoMoveException as e:
        # self.state = self.opposity_player()

      except EndGameException as e1:
        self.ok = False
        self.end_score = True

      pygame.display.update()
      self.clock.tick( self.clock_hz )

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

