import pygame
import random
from node import Node, WHITE, GREY

def make_grid(total_rows, screen_width):
    grid_array = []
    
    node_gap = screen_width // total_rows
    for i in range(total_rows):
        grid_array.append([])
        for j in range(total_rows):
            n = Node(i, j, node_gap, total_rows)
            grid_array[i].append(n)
    
    return grid_array

def draw_grid(surface, total_rows, screen_width):
    node_gap = screen_width // total_rows
    for i in range(total_rows):
        pygame.draw.line(surface, GREY, (0, i * node_gap), (screen_width, i * node_gap))
        for j in range(total_rows):
            pygame.draw.line(surface, GREY, (j * node_gap, 0), (j * node_gap, screen_width))

def draw(surface, grid_array, total_rows, screen_width):
    surface.fill(WHITE)

    for row in grid_array:
        for n in row:
            n.draw(surface)

    draw_grid(surface, total_rows, screen_width)


def get_clicked_pos(mouse_pos, total_rows, screen_width):
    node_gap = screen_width // total_rows
    pos_y, pos_x = mouse_pos

    calc_row = pos_y // node_gap
    calc_col = pos_x // node_gap

    calc_row = max(0, min(calc_row, total_rows - 1))
    calc_col = max(0, min(calc_col, total_rows - 1))

    return calc_row, calc_col

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
