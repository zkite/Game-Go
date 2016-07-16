VALID = 0
OCCUPIED = 1
SUICIDE = 2
KO = 3
COMPLETED = 4


class MoveResult:
	def __init__(self, status, prisoners=[]):
		self.status = status
		self.prisoners = prisoners


EMPTY = 0
BLACK = 1
WHITE = 2
SPECTR = 3

SCORE = 7


class GoGame:
	def __init__(self, size=8):
		self.size = size
		self.board = []

		for i in range(size + 1):
			self.board.append([EMPTY] * (size + 1))

		self.to_play = BLACK
		self.white_prisoners = 0
		self.black_prisoners = 0
		self.move_number = 1
		self.last_move_pass = 0
		self.game_completed = 0
		self.last_ko_move = None
		self.last_ko_prisoner = None

	def pass_move(self):
		self.move_number = self.move_number + 1
		if self.to_play == BLACK:
			self.to_play = WHITE
		else:
			self.to_play = BLACK
		if self.last_move_pass:
			self.game_completed = 1
		self.last_move_pass = 1

	def is_occupied(self, x, y):
		return (self.board[x][y] != EMPTY)

	def erase_stone(self, x, y):
		self.board[x][y] = EMPTY

	def place_stone(self, x, y, color):
		self.board[x][y] = color

	def move_stone(self, x, y, color=None, allow_suicide=None):
		if color == None:
			color = self.to_play

		if self.board[x][y] != EMPTY:
			return MoveResult(OCCUPIED)

		if self.game_completed:
			return MoveResult(COMPLETED)

		self.board[x][y] = color

		if color == BLACK:
			opposite = WHITE
		else:
			opposite = BLACK

		prisoners = []
		for (xx, yy) in self.calculate_grouped_adjacent(x, y)[opposite]:
			new_prisoners = self.calculate_prisoners(xx, yy)
			for new_prisoner in new_prisoners:
				if not new_prisoner in prisoners:
					prisoners.append(new_prisoner)

		suicide = 0
		if len(prisoners) == 0 and len(self.calculate_prisoners(x, y)) > 0:
			if allow_suicide:
				new_prisoners = self.calculate_prisoners(x, y)
				for new_prisoner in new_prisoners:
					if not new_prisoner in prisoners:
						prisoners.append(new_prisoner)
				if len(prisoners) > 0:
					suicide = 1
			else:
				self.board[x][y] = EMPTY
				return MoveResult(SUICIDE)

		if len(prisoners) == 1:
			if self.last_ko_move == prisoners[0] and self.last_ko_prisoner == (x, y):
				self.board[x][y] = EMPTY
				return MoveResult(KO)
			else:
				self.last_ko_move = (x, y)
				self.last_ko_prisoner = prisoners[0]
		else:
			self.last_ko_move = None
			self.last_ko_prisoner = None

		for (xx, yy) in prisoners:
			if not suicide:
				if color == BLACK:
					self.white_prisoners = self.white_prisoners + 1
				else:
					self.black_prisoners = self.black_prisoners + 1
			else:
				if color == BLACK:
					self.black_prisoners = self.black_prisoners + 1
				else:
					self.white_prisoners = self.white_prisoners + 1

			self.board[xx][yy] = EMPTY

		if color == BLACK:
			self.to_play = WHITE
		else:
			self.to_play = BLACK

		self.move_number = self.move_number + 1
		self.last_move_pass = 0

		return MoveResult(VALID, prisoners)

	def calculate_grouped_adjacent(self, x, y, dead_points=[]):

		adjacent = [[], [], []]
		if x != 0:
			if (x - 1, y) in dead_points:
				color = EMPTY
			else:
				color = self.board[x - 1][y]
			adjacent[color].append((x - 1, y))
		if y != 0:
			if (x, y - 1) in dead_points:
				color = EMPTY
			else:
				color = self.board[x][y - 1]
			adjacent[color].append((x, y - 1))
		if x != self.size:
			if (x + 1, y) in dead_points:
				color = EMPTY
			else:
				color = self.board[x + 1][y]
			adjacent[color].append((x + 1, y))
		if y != self.size:
			if (x, y + 1) in dead_points:
				color = EMPTY
			else:
				color = self.board[x][y + 1]
			adjacent[color].append((x, y + 1))
		return adjacent

	def calculate_prisoners(self, x, y):

		points_looked_at = []
		points_to_look_at = []
		points_to_look_at.append((x, y))
		while 1:
			if len(points_to_look_at) == 0:
				break
			else:
				(xx, yy) = points_to_look_at.pop()
				points_looked_at.append((xx, yy))
				adjacent = self.calculate_grouped_adjacent(xx, yy)
				if len(adjacent[0]) > 0:
					return []
				else:
					for point in adjacent[self.board[xx][yy]]:
						if not point in points_looked_at and not point in points_to_look_at:
							points_to_look_at.append(point)
		return points_looked_at

	def calculate_score(self, dead_points=[]):
		black_score = self.white_prisoners
		if black_score >= SCORE:
			self.game_completed = 1
		white_score = self.black_prisoners
		if white_score >= SCORE:
			self.game_completed = 1
		for (x, y) in dead_points:
			if self.board[x][y] == BLACK:
				white_score = white_score + 1
			elif self.board[x][y] == WHITE:
				black_score = black_score + 1
		return (black_score, white_score)
