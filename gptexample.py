import pygame
import random

# Inicializar Pygame
pygame.init()

# Definir colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Configuración de la pantalla
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Inicializar pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Definir formas de bloques
SHAPES = [
	[[1, 1, 1, 1]],  # I
	[[1, 1, 1], [1]],  # J
	[[1, 1, 1], [0, 0, 1]],  # L
	[[1, 1], [1, 1]],  # O
	[[1, 1, 1], [0, 1]],  # S
	[[1, 1, 1], [1, 0]],  # T
	[[1, 1], [0, 1, 1]]  # Z
]

# Colores correspondientes a las formas
SHAPE_COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, MAGENTA, RED]

# Clase para representar las piezas
class Piece:
	def __init__(self, shape, color):
		self.shape = shape
		self.color = color
		self.x = GRID_WIDTH // 2 - len(shape[0]) // 2
		self.y = 0

# Función para dibujar la cuadrícula
def draw_grid():
	for x in range(0, SCREEN_WIDTH, GRID_SIZE):
		pygame.draw.line(screen, WHITE, (x, 0), (x, SCREEN_HEIGHT))
	for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
		pygame.draw.line(screen, WHITE, (0, y), (SCREEN_WIDTH, y))

# Función para dibujar una pieza en la pantalla
def draw_piece(piece):
	for y, row in enumerate(piece.shape):
		for x, cell in enumerate(row):
			if cell:
				pygame.draw.rect(screen, piece.color, (piece.x * GRID_SIZE + x * GRID_SIZE, piece.y * GRID_SIZE + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Función para verificar colisiones
def check_collision(piece, grid):
	for y, row in enumerate(piece.shape):
		for x, cell in enumerate(row):
			if cell:
				if (
					piece.x + x < 0
					or piece.x + x >= GRID_WIDTH
					or piece.y + y >= GRID_HEIGHT
					or grid[piece.y + y][piece.x + x] is not None
				):
					return True
	return False

# Función principal
def main():
	clock = pygame.time.Clock()
	grid = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
	current_piece = Piece(random.choice(SHAPES), random.choice(SHAPE_COLORS))
	fall_time = 0
	fall_speed = 1

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					current_piece.x -= 1
					if check_collision(current_piece, grid):
						current_piece.x += 1
				elif event.key == pygame.K_RIGHT:
					current_piece.x += 1
					if check_collision(current_piece, grid):
						current_piece.x -= 1
				elif event.key == pygame.K_DOWN:
					current_piece.y += 1
					if check_collision(current_piece, grid):
						current_piece.y -= 1
				elif event.key == pygame.K_UP:
					# Rotar la pieza
					rotated_piece = list(zip(*reversed(current_piece.shape)))
					if not check_collision(Piece(rotated_piece, current_piece.color), grid):
						current_piece.shape = rotated_piece

		screen.fill(BLACK)

		fall_time += clock.get_rawtime()
		clock.tick()
		if fall_time / 1000 >= fall_speed:
			current_piece.y += 1
			fall_time = 0
			if check_collision(current_piece, grid):
				# Fijar la pieza en el tablero y generar una nueva pieza
				for y, row in enumerate(current_piece.shape):
					for x, cell in enumerate(row):
						if cell:
							grid[current_piece.y + y][current_piece.x + x] = current_piece.color
				current_piece = Piece(random.choice(SHAPES), random.choice(SHAPE_COLORS))

		if check_collision(current_piece, grid):
			# Si hay colisión en la parte inferior, fijar la pieza en el tablero y generar una nueva pieza
			for y, row in enumerate(current_piece.shape):
				for x, cell in enumerate(row):
					if cell:
						grid[current_piece.y + y][current_piece.x + x] = current_piece.color
			current_piece = Piece(random.choice(SHAPES), random.choice(SHAPE_COLORS))

		draw_grid()
		draw_piece(current_piece)

		# Dibujar las piezas fijas en el tablero
		for y, row in enumerate(grid):
			for x, color in enumerate(row):
				if color:
					pygame.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

		pygame.display.flip()

if __name__ == "__main__":
	main()
