import pygame

NUM_SQ = 12 # Number of squares.
PX_per_SQ = 30 # Number of pixels per square.
NUM_PLAYERS = 3

FONT_SIZE = 15

pygame.init()
SCREEN = pygame.display.set_mode((PX_per_SQ * NUM_SQ, PX_per_SQ * NUM_SQ + (FONT_SIZE+2)*(NUM_PLAYERS+2)))
FONT = pygame.font.SysFont("calibri", FONT_SIZE)

board = None

active_player_id = 0