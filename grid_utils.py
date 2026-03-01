import pygame
import random
from node import Node, WHITE, GREY

def make_grid(rows, width):
    grid = []

    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    row = max(0, min(row, rows - 1))
    col = max(0, min(col, rows - 1))

    return row, col

def generate_random_maze(grid, start, end, density_percentage):
    rows = len(grid)
    density = density_percentage / 100.0
    for row in grid:
        for node in row:
            if node != start and node != end:
                node.reset()
                if random.random() < density:
                    node.make_barrier()

def reset_search(grid, start, end):
    for row in grid:
        for node in row:
            if node != start and node != end and not node.is_barrier():
                node.reset()
