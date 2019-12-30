import game_constants as gcs

class Piece:

    # Statuses.
    HOVERING = "HOVERING"
    PLACED = "PLACED"
    CEMENTED = "CEMENTED"

    def __init__(self, shape, player_id):

        self.player_id = player_id
        self._base_shape = shape
        self.status = Piece.HOVERING

        # This gets defined once an orientation is defined.
        # 'shape' is the rotated shape, while _base_shape is
        # the shape we start out with/are manipulating.
        self.shape = None

        self._orientation = None
        self._set_orientation(0)

        self.position = [None, None]

    def can_place(self):

        for point in self.shape:

            x = point[0] + self.position[0]
            y = point[1] + self.position[1]

            # Check if we're on the board.
            if not((0 <= x < gcs.NUM_SQ) and
                   (0 <= y < gcs.NUM_SQ)):
                return False

            # Check if the area we're on is free.
            # (We know no OOB error b/c of previous lines)
            if not( (gcs.board[x][y][0] in  ['FREE', 'ODD_LAND']) or (gcs.board[x][y][0] == "LAND" and gcs.board[x][y][1] == self.player_id)):
                return False

            # If the point is free, but all its neighbors are 'OCCUPIED',
            # and of a single player ID, then it's an odd zone and we cannot
            # play our piece in there. (A fix for 'ODD_LAND'.)
            point_neighbors = Piece._get_neighbor_points_for_point(point)
            point_neighbors = [(x + p[0], y + p[1]) for p in point_neighbors]
            point_neighbors = [p for p in point_neighbors if (0 <= p[0] < gcs.NUM_SQ) and
                                                            (0 <= p[1] < gcs.NUM_SQ)]

            point_neighbors = [gcs.board[p[0]][p[1]] for p in point_neighbors]
            if all([pn[0] == 'OCCUPIED' for pn in point_neighbors]) and \
                    len(list(set([pn[1] for pn in point_neighbors]))) == 1 and\
                     list(set([pn[1] for pn in point_neighbors]))[0] != self.player_id:
                return False

        # If we haven't failed so far...
        return True

    def place_piece(self):
        can_place = self.can_place()
        if can_place: self.status = Piece.PLACED
        return can_place

    def get_neighbor_points(self):
        return Piece._get_neighbor_points_for_shape(self.shape)

    @staticmethod
    def _get_neighbor_points_for_shape(shape):

        lists_of_points = [Piece._get_neighbor_points_for_point(point) for point in shape]

        # Flatten the lists so I have one list with all the points.
        all_neighbors = [] # This is the list of all points.
        for point_list in lists_of_points:
            for point in point_list:
                all_neighbors.append(point)

        return list(set(all_neighbors)) # Remove duplicates.

    @staticmethod
    def _get_neighbor_points_for_point(point):
        return \
            [
                (point[0] + 1, point[1] + 1),
                (point[0] + 0, point[1] + 1),
                (point[0] - 1, point[1] + 1),

                (point[0] + 1, point[1] + 0),
                (point[0] - 1, point[1] + 0),

                (point[0] + 1, point[1] - 1),
                (point[0] + 0, point[1] - 1),
                (point[0] - 1, point[1] - 1),
            ]

    def _set_orientation(self, new_orientation):
        self._orientation = (new_orientation % 4)
        self.shape = self._rotate_shape(self._base_shape, self._orientation)

    def rotate(self):
        self._set_orientation(self._orientation+1)

    @staticmethod
    def _rotate_shape(shape, rotation):
        return [Piece._rotate_point(point, rotation) for point in shape]

    @staticmethod
    def _rotate_point(point, rotation):

        rotated_point = [None, None]
        if rotation == 0:
            rotated_point[0] = -point[0]
            rotated_point[1] = point[1]
        if rotation == 1:
            rotated_point[0] = point[1]
            rotated_point[1] = point[0]
        if rotation == 2:
            rotated_point[0] = point[0]
            rotated_point[1] = -point[1]
        if rotation == 3:
            rotated_point[0] = -point[1]
            rotated_point[1] = -point[0]

        return rotated_point