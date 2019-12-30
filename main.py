from matplotlib import cm
import input_manager as im
import game_board
import numpy as np
import pygame
import player
import game_constants as gcs
from shape import Shape
from piece import Piece

pygame.init()
font = pygame.font.SysFont("Deja Vu", 15)
clock = pygame.time.Clock()

player_colors = cm.get_cmap('gist_rainbow', gcs.NUM_PLAYERS)
player_colors = [(np.asarray(player_colors(n))*255).astype('uint8') for n in range(gcs.NUM_PLAYERS)]
players = [player.Player(player_id, player_colors[player_id]) for player_id in range(gcs.NUM_PLAYERS)]

gcs.board = game_board.make_board()

the_church = player.Player("CATHEDRAL", (200,200,200))
the_church.in_hand = [Piece(Shape.CATHEDRAL, "CATHEDRAL")]

while True:

    if len(players[gcs.active_player_id].in_hand) == 0:
        gcs.active_player_id = (gcs.active_player_id+1)%len(players)

    events = pygame.event.get()
    im.update_inputs(events)

    pygame.draw.rect(gcs.SCREEN, (0,0,0), (0, 0, gcs.NUM_SQ*gcs.PX_per_SQ, gcs.NUM_SQ*gcs.PX_per_SQ))

    game_board.display_board()

    if len(the_church.in_hand) > 0:
        the_church.draw_active_pieces()
        the_church.update()
    else:
        for n in range(gcs.NUM_PLAYERS):
            players[n].remove_isolated_pieces()
            players[n].draw_claimed_land()
            players[n].draw_active_pieces()
        players[gcs.active_player_id].update()

    the_church.draw_active_pieces()
    #game_board.display_text_overlay()
    pygame.draw.rect(gcs.SCREEN, (0,0,0), (0, gcs.NUM_SQ*gcs.PX_per_SQ, gcs.NUM_SQ*gcs.PX_per_SQ, (gcs.FONT_SIZE+2)*(gcs.NUM_PLAYERS+2)))
    for n in range(gcs.NUM_PLAYERS):
        if (n+1)%2:
            pygame.draw.rect(gcs.SCREEN, (20,20,20), (0, (gcs.FONT_SIZE+2)*(n+1) + gcs.NUM_SQ*gcs.PX_per_SQ, gcs.NUM_SQ*gcs.PX_per_SQ, 12))
        gcs.SCREEN.blit(gcs.FONT.render("PLAYER {0}: {1}".format(n, sum([len(p.shape) for p in players[n].in_hand])), 1, player_colors[n]),
                        (10, (gcs.FONT_SIZE+2)*(n+1) + gcs.NUM_SQ*gcs.PX_per_SQ))

    pygame.display.flip()
    clock.tick(60)
