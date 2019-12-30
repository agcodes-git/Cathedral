import pygame, copy
import game_constants as gcs
from piece import Piece

def make_board():
    board = [[['FREE', None] for _ in range(gcs.NUM_SQ)] for _ in range(gcs.NUM_SQ)]
    #board[5][5] = ["OTHER", 'CATHEDRAL']
    return board

def sector_land():

    #print('Sector land!')

    unique_player_ids = set()
    for x in range(gcs.NUM_SQ):
        for y in range(gcs.NUM_SQ):
            unique_player_ids.add(gcs.board[x][y][1])

    # Exit early if not everyone's played yet.
    if len(list(unique_player_ids)) < gcs.NUM_PLAYERS+1: return

    temporary_board_A = copy.deepcopy(gcs.board)
    temporary_board_B = copy.deepcopy(gcs.board)

    # Everything touching your pieces or your land is your land.
    # Anything touching another player's piece or another player's land is not.
    for trial in range(gcs.NUM_SQ * gcs.NUM_SQ):

        for x in range(gcs.NUM_SQ):
            for y in range(gcs.NUM_SQ):

                neighboring_values = set() # The text labels on each tile: [TYPE, PLAYER_ID]
                neighboring_points = Piece._get_neighbor_points_for_point([x,y])

                for point in neighboring_points:
                    if (0 <= point[0] < gcs.NUM_SQ) and (0 <= point[1] < gcs.NUM_SQ):

                        neighbor_player_id = temporary_board_A[point[0]][point[1]][1]
                        neighbor_tile_type = temporary_board_A[point[0]][point[1]][0]

                        # Ignore free tiles and temporary tiles.
                        if (neighbor_player_id is not None) and \
                            (neighbor_tile_type not in  ["OCCUPIED", "ODD_LAND"]):
                            neighboring_values.add(neighbor_player_id)

                # If only one player type neighbors us, become their land.
                unique_player_ids = list(neighboring_values)
                if len(unique_player_ids) == 1 and unique_player_ids[0] != "CATHEDRAL":
                    temporary_board_B[x][y] = ['LAND', unique_player_ids[0]]

        # Exit early, if the there are no more changed to occur.
        if trial > 5 and all([A == B for A,B in zip(temporary_board_A, temporary_board_B)]): break
        temporary_board_A = temporary_board_B

    # They're separate, to be clear.
    temporary_board_A = copy.deepcopy(temporary_board_B)
    temporary_board_B = copy.deepcopy(temporary_board_A)

    #Now we're going to recede.
    for trial in range(gcs.NUM_SQ * gcs.NUM_SQ):

        for x in range(gcs.NUM_SQ):
            for y in range(gcs.NUM_SQ):

                neighboring_values = set() # The text labels on each tile: [TYPE, PLAYER_ID]
                neighboring_points = Piece._get_neighbor_points_for_point([x,y])

                for point in neighboring_points:
                    if (0 <= point[0] < gcs.NUM_SQ) and (0 <= point[1] < gcs.NUM_SQ):

                        neighbor_player_id = temporary_board_A[point[0]][point[1]][1]
                        neighbor_tile_type = temporary_board_A[point[0]][point[1]][0]

                        # An irksome exception. If a piece of land is secured with one piece and that
                        # piece is removed, the land shouldn't count against the existing land.
                        # Pockets of land stopping a piece from being removed are never supported
                        # by other land, as far as I can tell (unless other shapes of pieces are created).
                        neighbor_neighbors = Piece._get_neighbor_points_for_point(point)
                        neighbor_neighbors = [p for p in neighbor_neighbors if (0 <= p[0] < gcs.NUM_SQ)
                                                                           and (0 <= p[1] < gcs.NUM_SQ)]
                        neighbor_neighbors_tile_type = [temporary_board_A[p[0]][p[1]][0] for p in neighbor_neighbors]

                        # Don't ignore any tiles in this calculation....
                        neighboring_values.add(neighbor_player_id)

                # If there are adjacent free tiles, or different player's land
                # or different player's pieces are adjacent to this tile, revert.
                # ...unless it's land that is secured by a piece that would be removed.
                unique_player_ids = list(neighboring_values)
                if len(unique_player_ids) != 1 or unique_player_ids[0] is None:
                    temporary_board_B[x][y] = gcs.board[x][y]

        if trial > 5 and all([A == B for A,B in zip(temporary_board_A, temporary_board_B)]): break
        temporary_board_A = copy.deepcopy(temporary_board_B)

    gcs.board = temporary_board_A

# ----------------------------------------------------------------------------------------------------------------------
#   DRAWING FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------
def _draw_loop(element_function):
    for x in range(gcs.NUM_SQ):
        for y in range(gcs.NUM_SQ):
            element_function(x, y)

def display_board():

    def draw_tile(x, y):

            draw_x = gcs.PX_per_SQ * x
            draw_y = gcs.PX_per_SQ * y

            board_light = (50,50,50)
            board_dark = (40,40,40)

            board_color = board_light if (x%2 - y%2) else board_dark
            pygame.draw.rect(gcs.SCREEN, board_color,
            (draw_x, draw_y, gcs.PX_per_SQ-1, gcs.PX_per_SQ-1))

    _draw_loop(draw_tile)

def display_text_overlay():

    def draw_text(x, y):

        text_color =  (150,150,150)

        for n, text in enumerate(gcs.board[x][y]):
            gcs.SCREEN.blit(gcs.FONT.render(str(text), 1, text_color),
                            (12+x*gcs.PX_per_SQ, 12*(n+1)+y*gcs.PX_per_SQ))

    _draw_loop(draw_text)