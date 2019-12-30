from shape import Shape
from piece import Piece
import input_manager as im
import game_constants as gcs
import pygame
import game_board

class Player:

    def __init__(self, player_id, player_color):

        self.player_id = player_id
        self.player_color = player_color

        if self.player_id != "CATHEDRAL":
            self.in_hand = self.get_new_hand()

        self.out_of_hand = []

        self.active_piece_id = 0

    def update(self):

        self.draw_active_pieces()
        self.draw_preview()

        if im.pressed('mb1'):

            placed_piece = self.in_hand[self.active_piece_id].place_piece()
            if placed_piece:

                # Turn to the next player.
                gcs.active_player_id = (gcs.active_player_id+1) % gcs.NUM_PLAYERS

                # Assuming the above is successful, update the board to reflect that the
                # area is temporarily occupied, and also remove this piece from our hand.
                for point in self.in_hand[self.active_piece_id].shape:
                    x = point[0] + self.in_hand[self.active_piece_id].position[0]
                    y = point[1] + self.in_hand[self.active_piece_id].position[1]
                    gcs.board[x][y] = ['OCCUPIED', self.player_id]

                self.out_of_hand.append(self.in_hand[self.active_piece_id])
                self.active_piece_id = self.active_piece_id % max(1,(len(self.in_hand)-1))
                self.in_hand.remove(self.out_of_hand[-1])

                # Now let's cement our pieces.
                self.cement_pieces()

                # Sector land only when a piece is moved.
                game_board.sector_land()

        #if im.pressed('mb2'): self.active_piece_id = (self.active_piece_id+1) % len(self.in_hand)
        #self.active_piece_id = min(max(0, self.active_piece_id-im.scroll_direction), len(self.in_hand)-1) #(self.active_piece_id+im.scroll_direction) % len(self.in_hand)
        self.active_piece_id = (self.active_piece_id+im.scroll_direction) % max(1,len(self.in_hand))
        if im.pressed('mb3'): self.in_hand[self.active_piece_id].rotate()

    def remove_isolated_pieces(self):

        for active_piece in self.out_of_hand:

            # Cemented pieces cannot be removed in this manner.
            if active_piece.status == Piece.CEMENTED: continue

            # Figure out who owns the land under this piece.
            owners = [gcs.board[active_piece.position[0]+point[0]][active_piece.position[1]+point[1]][1] for point in active_piece.shape]
            owners = list(set(owners))

            # If the land is exclusively someone else's, remove this piece from it.
            if len(owners) == 1 and owners[0] is not None and owners[0] != self.player_id:

                active_piece.status = Piece.HOVERING
                active_piece.position = [None, None]
                self.in_hand.append(active_piece)
                self.out_of_hand.remove(active_piece)

    def get_new_hand(self):
        return [Piece(s, self.player_id) for s in
        [
            Shape.APARTMENT, Shape.HOUSE, Shape.APARTMENT,
            Shape.BRIDGE, Shape.T_SHAPE, Shape.HOUSE,
            Shape.SQUARE, Shape.C_SHAPE, Shape.L_SHAPE,
            Shape.PLUS, Shape.L_SHAPE, Shape.BIG_WIGGLE,
            Shape.WEIRD_A if self.player_id % 2 else Shape.WEIRD_B,
            Shape.S_CURVE_A if self.player_id % 2 else Shape.S_CURVE_B
        ]]

    def cement_pieces(self):

        # If our piece is the cathedral or neighbor to it, then it gets cemented automatically.
        for a in range(len(self.out_of_hand)):

            a_position = self.out_of_hand[a].position
            relative_a_neighbor_points = self.out_of_hand[a].get_neighbor_points()
            absolute_a_neighbor_points = [(a_position[0] + rp[0], a_position[1] + rp[1]) for rp in
                                          relative_a_neighbor_points]

            touching_or_is_cathedral = False
            for point in absolute_a_neighbor_points:
                if (0 <= point[0] < gcs.NUM_SQ) and (0 <= point[1] < gcs.NUM_SQ):
                    if gcs.board[point[0]][point[1]][1] == "CATHEDRAL":
                        touching_or_is_cathedral = True
                        break

            # If we're touching the cathedral (or are it), then
            # out entire shape ought to become cemented.
            if touching_or_is_cathedral:
                for point in self.out_of_hand[a].shape:
                    x = point[0] + self.out_of_hand[a].position[0]
                    y = point[1] + self.out_of_hand[a].position[1]
                    gcs.board[x][y] = ['CEMENTED', self.player_id]


        # Otherwise, we've gotta look for our own neighbors.
        for a in range(len(self.out_of_hand)):
            for b in range(a+1, len(self.out_of_hand)):

                a_position = self.out_of_hand[a].position
                b_position = self.out_of_hand[b].position

                relative_a_neighbor_points = self.out_of_hand[a].get_neighbor_points()
                relative_b_shape_points = self.out_of_hand[b].shape

                absolute_a_neighbor_points = [(a_position[0]+rp[0], a_position[1]+rp[1]) for rp in relative_a_neighbor_points]
                absolute_b_shape_points = [(b_position[0]+rp[0], b_position[1]+rp[1]) for rp in relative_b_shape_points]

                # If any two of my pieces touch, regardless of status, cement them together,
                # and update the global game board to reflect that these spots are occupied.
                if any(a_point in absolute_a_neighbor_points for a_point in absolute_b_shape_points):

                    self.out_of_hand[b].status = Piece.CEMENTED
                    self.out_of_hand[a].status = Piece.CEMENTED

                    for point in self.out_of_hand[a].shape:
                        x = point[0] + self.out_of_hand[a].position[0]
                        y = point[1] + self.out_of_hand[a].position[1]
                        gcs.board[x][y] = ['CEMENTED', self.player_id]

                    for point in self.out_of_hand[b].shape:
                        x = point[0] + self.out_of_hand[b].position[0]
                        y = point[1] + self.out_of_hand[b].position[1]
                        gcs.board[x][y] = ['CEMENTED', self.player_id]

#----------------------------------------------------------------------------------------------------------------------
#   DRAWING FUNCTIONS
#----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def darker(color, div=2.0): return [max(0,min(int(c/div),255)) for c in color]

    def draw_claimed_land(self):

        for x in range(gcs.NUM_SQ):
            for y in range(gcs.NUM_SQ):
                if (gcs.board[x][y][0] == "LAND") and (gcs.board[x][y][1] == self.player_id):
                    pygame.draw.rect(gcs.SCREEN, Player.darker(self.player_color),
                                     (x*gcs.PX_per_SQ, y*gcs.PX_per_SQ,
                                      gcs.PX_per_SQ-1, gcs.PX_per_SQ-1))

        # Now for all my pieces which may have 'ODD_LAND', check.
        for active_piece in self.out_of_hand:
            if True: #active_piece.status == "OCCUPIED": # Bugged, but if I needed speed could try it.
                for piece_point in active_piece.get_neighbor_points():

                    x = active_piece.position[0] + piece_point[0]
                    y = active_piece.position[1] + piece_point[1]

                    point_neighbors = Piece._get_neighbor_points_for_point((x,y))
                    point_neighbors = [p for p in point_neighbors if (0 <= p[0] < gcs.NUM_SQ) and
                                                                    (0 <= p[1] < gcs.NUM_SQ)]

                    point_neighbors = [gcs.board[p[0]][p[1]] for p in point_neighbors]
                    if all([pn[0] == 'OCCUPIED' for pn in point_neighbors]) and \
                            len(list(set([pn[1] for pn in point_neighbors]))) == 1:

                        pygame.draw.rect(gcs.SCREEN, Player.darker(self.player_color),
                                         (x * gcs.PX_per_SQ, y * gcs.PX_per_SQ,
                                          gcs.PX_per_SQ + 10, gcs.PX_per_SQ + 10))

    def draw_active_pieces(self):

        for active_piece in self.out_of_hand:
            for point in active_piece.shape:
                px = (point[0] + active_piece.position[0]) * gcs.PX_per_SQ
                py = (point[1] + active_piece.position[1]) * gcs.PX_per_SQ
                pygame.draw.rect(gcs.SCREEN, self.player_color,
                                 (px, py, gcs.PX_per_SQ - 1, gcs.PX_per_SQ - 1))

                # gcs.SCREEN.blit(gcs.FONT.render(active_piece.status, 1, (200,200,200)),
                #                 (10 + px, py + gcs.PX_per_SQ - 20))

    def draw_preview(self):

        mx, my = im.mouse_position
        board_mx = int(mx/gcs.PX_per_SQ)
        board_my = int(my/gcs.PX_per_SQ)

        active_piece = self.in_hand[self.active_piece_id]
        active_piece.position = [board_mx, board_my]

        can_place = active_piece.can_place()
        piece_color = self.player_color if can_place else Player.darker(self.player_color, 1.5)

        for point in active_piece.shape:

            px = (point[0] + board_mx) * gcs.PX_per_SQ
            py = (point[1] + board_my) * gcs.PX_per_SQ
            pygame.draw.rect(gcs.SCREEN, piece_color,
                             (px, py, gcs.PX_per_SQ-1, gcs.PX_per_SQ-1))

        # for point in active_piece.get_neighbor_points():
        #
        #     px = (point[0] + board_mx) * gcs.PX_per_SQ
        #     py = (point[1] + board_my) * gcs.PX_per_SQ
        #     pygame.draw.rect(gcs.SCREEN, piece_color,
        #                      (px, py, gcs.PX_per_SQ-1, gcs.PX_per_SQ-1), 1)