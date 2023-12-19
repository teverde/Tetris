import pygame
import random
import numpy as np
from collections import OrderedDict
from block import *

def remove_empty_columns(arr, _x_offset=0, _keep_counting=True):
  """
  Remove empty columns from arr (i.e. those filled with zeros).
  The return value is (new_arr, x_offset), where x_offset is how
  much the x coordinate needs to be increased in order to maintain
  the block's original position.
  """
  for colid, col in enumerate(arr.T):
    if col.max() == 0:
      if _keep_counting:
        _x_offset += 1
        # Remove the current column and try again.
      arr, _x_offset = remove_empty_columns(
        np.delete(arr, colid, 1), _x_offset, _keep_counting)
      break
    else:
      _keep_counting = False
  return arr, _x_offset


class BlocksGroup(pygame.sprite.OrderedUpdates):


  def get_random_block(self):
    if self.random_bag == []:
      self.random_bag = [OBlock, TBlock, IBlock, LBlock, ZBlock, SBlock, JBlock]
      random.shuffle(self.random_bag)
    return self.random_bag.pop()()

  def __init__(self, *args, **kwargs):
    super().__init__(self, *args, **kwargs)
    self._reset_grid()
    self._ignore_next_stop = False
    self.score = 0
    self.level = 1
    self.lines_counter = 0
    self.combo_counter = 0
    self.next_block = None
    self.next_block2 = None
    self.next_block3 = None
    self.holded_block = None
    self.hold_blocked = False
    self.random_bag = []
    # Not really moving, just to initialize the attribute.
    self.stop_moving_current_block()
    # The first block.
    self._create_new_block()

  def _check_line_completion(self, lines_completed=0):
    """
    Check each line of the grid and remove the ones that
    are complete.
    """
    # Start checking from the bottom.
    for i, row in enumerate(self.grid[::-1]):
      if all(row):
        lines_completed += 1
        # Get the blocks affected by the line deletion and
        # remove duplicates.
        affected_blocks = list(
          OrderedDict.fromkeys(self.grid[-1 - i]))

        for block, y_offset in affected_blocks:
          # Remove the block tiles which belong to the
          # completed line.
          block.struct = np.delete(block.struct, y_offset, 0)
          if block.struct.any():
            # Once removed, check if we have empty columns
            # since they need to be dropped.
            block.struct, x_offset = \
              remove_empty_columns(block.struct)
            # Compensate the space gone with the columns to
            # keep the block's original position.
            block.x += x_offset
            # Force update.
            block.redraw()
          else:
            # If the struct is empty then the block is gone.
            self.remove(block)

        # Instead of checking which blocks need to be moved
        # once a line was completed, just try to move all of
        # them.
        for block in self:
          # Except the current block.
          if block.current:
            continue
          # Pull down each block until it reaches the
          # bottom or collides with another block.
          while True:
            try:
              block.move_down(self)
            except BottomReached:
              break

        self.update_grid()
        # Since we've updated the grid, now the i counter
        # is no longer valid, so call the function again
        # to check if there're other completed lines in the
        # new grid.
        var = self._check_line_completion(lines_completed)
        if var is not None:
          lines_completed = var
        return lines_completed

  def update_score(self, lines_completed):
    if all(v == 0 for v in self.grid[-1]):
      if lines_completed == 1:
        self.score += 800 * self.level
      elif lines_completed == 2:
        self.score += 1200 * self.level
      elif lines_completed == 3:
        self.score += 1800 * self.level
      elif lines_completed == 4:
        self.score += 2000 * self.level
    else:
      if lines_completed == 1:
        self.score += 100 * self.level
      elif lines_completed == 2:
        self.score += 300 * self.level
      elif lines_completed == 3:
        self.score += 500 * self.level
      elif lines_completed == 4:
        self.score += 800 * self.level

    if self.combo_counter > 0:
      self.score += 50 * self.combo_counter * self.level

  def _reset_grid(self):
    self.grid = [[0 for _ in range(10)] for _ in range(20)]

  def _create_new_block(self, not_holded = True, block_type = None):
    if not_holded:
      new_block = self.next_block or self.get_random_block()
      self.next_block = self.next_block2 or self.get_random_block()
      self.next_block2 = self.next_block3 or self.get_random_block()
      if Block.collide(new_block, self):
        raise TopReached
      self.add(new_block)
      self.next_block3 = self.get_random_block()
    else:
      new_block = eval(block_type)
      if Block.collide(new_block, self):
        raise TopReached
      self.add(new_block)

    self.update_grid()
    lines_completed = self._check_line_completion()

    if lines_completed:
      self.update_score(lines_completed)
      self.lines_counter += lines_completed
      if self.lines_counter >= 10:
        self.level += 1
        self.lines_counter -= 10
      self.combo_counter += 1

    elif self.combo_counter > 0:
      self.combo_counter = 0

    self.hold_blocked = False

  def update_grid(self):
    self._reset_grid()
    for block in self:
      for y_offset, row in enumerate(block.struct):
        for x_offset, digit in enumerate(row):
          # Prevent replacing previous blocks.
          if digit == 0:
            continue
          rowid = block.y + y_offset
          colid = block.x + x_offset
          self.grid[rowid][colid] = (block, y_offset)

  @property
  def current_block(self):
    return self.sprites()[-1]

  def update_current_block(self):
    try:
      self.current_block.move_down(self)
    except BottomReached:
      self.stop_moving_current_block()
      self._create_new_block()
    else:
      self.update_grid()

  def move_current_block(self):
    # First check if there's something to move.
    if self._current_block_movement_heading is None:
      return
    action = {
      pygame.K_DOWN: self.current_block.soft_drop,
      pygame.K_LEFT: self.current_block.move_left,
      pygame.K_RIGHT: self.current_block.move_right,
      pygame.K_SPACE: self.current_block.hard_drop
    }
    try:
      # Each function requires the group as the first argument
      # to check any possible collision.
      action[self._current_block_movement_heading](self)
    except BottomReached:
      self.stop_moving_current_block()
      self._create_new_block()
    else:
      self.update_grid()

  def start_moving_current_block(self, key):
    if self._current_block_movement_heading is not None:
      self._ignore_next_stop = True
    self._current_block_movement_heading = key

  def stop_moving_current_block(self):
    if self._ignore_next_stop:
      self._ignore_next_stop = False
    else:
      self._current_block_movement_heading = None

  def rotate_current_block_left(self):
    # Prevent SquareBlocks rotation.
    if not isinstance(self.current_block, OBlock):
      self.current_block.rotate_left(self)
      self.update_grid()

  def rotate_current_block_right(self):
    # Prevent SquareBlocks rotation.
    if not isinstance(self.current_block, OBlock):
      self.current_block.rotate_right(self)
      self.update_grid()

  def remove_current_block(self):
    for block in self.sprites():
      if block.current:
        self.remove(block)
        break

  def hold_current_block(self):
    if self.holded_block:
      var = type(self.holded_block).__name__ + "()"
      self.holded_block = eval(type(self.current_block).__name__ + "()")
      self.remove_current_block()
      self._create_new_block(not_holded = False, block_type = var)

    else:
      self.holded_block = eval(type(self.current_block).__name__ + "()")
      self.remove_current_block()
      self._create_new_block()

    self.hold_blocked = True
