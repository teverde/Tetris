import pygame
import numpy as np
from block import *
from blockgroup import *

def draw_grid(background):
  grid_color = 50, 50, 50
  # Vertical lines.
  for i in range(11):
    x = TILE_SIZE * i
    pygame.draw.line(
      background, grid_color, (x, 0), (x, GRID_HEIGHT)
    )
  # Horizontal liens.
  for i in range(21):
    y = TILE_SIZE * i
    pygame.draw.line(
      background, grid_color, (0, y), (GRID_WIDTH, y)
    )

def draw_shadow(current_block, group, background):
  background.fill(BLACK)
  draw_grid(background)
  var = current_block.y

  while current_block.rect.bottom <= GRID_HEIGHT and not Block.collide(current_block, group):
    current_block.y += 1
  current_block.y -= 1

  for y, row in enumerate(current_block.struct):
    for x, col in enumerate(row):
      if col:
        pygame.draw.rect(
          background,
          GREY,
          pygame.Rect((x + current_block.x) * TILE_SIZE + 1, (y + current_block.y) * TILE_SIZE + 1,
            TILE_SIZE - 2, TILE_SIZE - 2)
        )
  current_block.y = var

def draw_centered_surface1(screen, surface, y):
  screen.blit(surface, (400 - surface.get_width()/2, y))

def draw_centered_surface2(screen, surface, y):
  screen.blit(surface, (600 - surface.get_width()/2, y))

def main():
  pygame.init()
  pygame.display.set_caption("Tetris - By Tatsuya Yamaguchi")
  pygame.mixer.music.load("public\korobeiniki.mp3")
  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  top_score = 0
  run = True
  paused = False
  game_over = False
  # Create background.
  background = pygame.Surface(screen.get_size())
  bgcolor = BLACK
  background.fill(bgcolor)
  # Draw the grid on top of the background.
  draw_grid(background)
  # This makes blitting faster.
  background = background.convert()

  try:
    font = pygame.font.Font("public\Roboto-Regular.ttf", 20)
  except OSError:
    # If the font file is not available, the default will be used.
    pass
  level_msg = font.render(
    "Nivel:", True, WHITE, bgcolor)
  next_block_text = font.render(
    "Siguientes figuras:", True, WHITE, bgcolor)
  score_msg_text = font.render(
    "Puntaje:", True, WHITE, bgcolor)
  hold_block_msg = font.render(
    "Figura Retenida:", True, WHITE, bgcolor)
  pause_msg = font.render(
    "Pausa (P)", True, WHITE, bgcolor)
  top_score_msg = font.render(
    "Puntaje maximo:", True, WHITE, bgcolor)
  game_over_text1= font.render(
    "GAME OVER", True, (255, 220, 0), bgcolor)
  game_over_text2= font.render(
    "Jugar de nuevo (R)", True, (255, 220, 0), bgcolor)
  game_over_text3= font.render(
    "Salir del juego (Q)", True, (255, 220, 0), bgcolor)



  # Event constants.
  MOVEMENT_KEYS = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_SPACE
  EVENT_UPDATE_CURRENT_BLOCK = pygame.USEREVENT + 1
  EVENT_MOVE_CURRENT_BLOCK = pygame.USEREVENT + 2
  pygame.time.set_timer(EVENT_MOVE_CURRENT_BLOCK, 100)

  blocks = BlocksGroup()
  draw_shadow(blocks.current_block, blocks, background)

  pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK,
  int(1000 * pow((.8- (blocks.level - 1) * 0.007), (blocks.level - 1))))

  pygame.mixer.music.play(-1)

  while run:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
        break
      elif event.type == pygame.KEYUP:
        if not paused and not game_over:
          if event.key in MOVEMENT_KEYS:
            blocks.stop_moving_current_block()
          elif event.key == pygame.K_UP:
            blocks.rotate_current_block_left()
          elif event.key == pygame.K_z or event.key == pygame.K_LCTRL:
            blocks.rotate_current_block_right()
          elif event.key == pygame.K_c and blocks.hold_blocked == False:
            blocks.hold_current_block()
          draw_shadow(blocks.current_block, blocks, background)
        if event.key == pygame.K_p:
          paused = not paused
          if paused:
            pygame.mixer.music.pause()
          else:
            pygame.mixer.music.unpause()
        if game_over:
          if event.key == pygame.K_r:
            blocks = BlocksGroup()
            draw_shadow(blocks.current_block, blocks, background)
            game_over = False
          elif event.key == pygame.K_q:
            run = False


      # Stop moving blocks if the game is over or paused.
      if game_over or paused:
        continue

      if event.type == pygame.KEYDOWN:
        if event.key in MOVEMENT_KEYS:
          blocks.start_moving_current_block(event.key)

      try:
        if event.type == EVENT_UPDATE_CURRENT_BLOCK:
          blocks.update_current_block()
        elif event.type == EVENT_MOVE_CURRENT_BLOCK:
          blocks.move_current_block()
      except TopReached:
        game_over = True

    # Draw background and grid.
    screen.blit(background, (0, 0))
    # Blocks.
    blocks.draw(screen)
    # Sidebar with misc. information.
    if not paused:
      draw_centered_surface1(screen, level_msg, 50)
      level_text = font.render(
        str(blocks.level), True, WHITE, bgcolor)
      draw_centered_surface1(screen, level_text, 80)
      draw_centered_surface1(screen, next_block_text, 130)
      draw_centered_surface1(screen, blocks.next_block.image, 180)
      draw_centered_surface1(screen, blocks.next_block2.image, 330)
      draw_centered_surface1(screen, blocks.next_block3.image, 480)

      draw_centered_surface2(screen, top_score_msg, 50)
      top_score_text = font.render(
        str(top_score), True, WHITE, bgcolor)
      draw_centered_surface2(screen, top_score_text, 80)
      draw_centered_surface2(screen, score_msg_text, 130)
      score_text = font.render(
        str(blocks.score), True, WHITE, bgcolor)
      draw_centered_surface2(screen, score_text, 160)
      draw_centered_surface2(screen, hold_block_msg, 210)
      if blocks.holded_block:
        draw_centered_surface2(screen, blocks.holded_block.image, 260)

    else:
      draw_centered_surface1(screen, pause_msg, 250)

    if game_over:
      screen.blit(background, (0, 0))
      blocks.draw(screen)
      draw_centered_surface1(screen, game_over_text1, 50)
      draw_centered_surface1(screen, game_over_text2, 100)
      draw_centered_surface1(screen, game_over_text3, 150)
      if blocks.score > top_score:
        top_score = blocks.score

    # Update.
    pygame.display.flip()

  pygame.quit()

if __name__ == "__main__":
  main()