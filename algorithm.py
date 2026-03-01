import pygame
import math
from queue import PriorityQueue

def h(p1, p2, heuristic_type):
    x1, y1 = p1
    x2, y2 = p2
    if heuristic_type == "Manhattan":
        return abs(x1 - x2) + abs(y1 - y2)
    elif heuristic_type == "Euclidean":
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return 0

def reconstruct_path(came_from, current, draw):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    
    path.reverse()
    for node in path:
        if not node.is_end() and not node.is_start():
            node.make_path()
        draw()
    return path

def a_star_search(draw, grid, start, end, heuristic_type):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos(), heuristic_type)

    open_set_hash = {start}
    nodes_visited = 0

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path = reconstruct_path(came_from, end, draw)
            return True, nodes_visited, path

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos(), heuristic_type)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if not neighbor.is_end() and not neighbor.is_start():
                        neighbor.make_open()

        if current != start and current != end:
            current.make_closed()
        
        nodes_visited += 1
        yield False, nodes_visited, []

    return False, nodes_visited, []

def gbfs_search(draw, grid, start, end, heuristic_type):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    open_set_hash = {start}
    visited_nodes = {start}
    nodes_visited = 0

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path = reconstruct_path(came_from, end, draw)
            return True, nodes_visited, path

        for neighbor in current.neighbors:
            if neighbor not in visited_nodes and not neighbor.is_barrier():
                visited_nodes.add(neighbor)
                came_from[neighbor] = current
                h_score = h(neighbor.get_pos(), end.get_pos(), heuristic_type)
                count += 1
                open_set.put((h_score, count, neighbor))
                open_set_hash.add(neighbor)
                if not neighbor.is_end() and not neighbor.is_start():
                    neighbor.make_open()

        if current != start and current != end:
            current.make_closed()
            
        nodes_visited += 1
        yield False, nodes_visited, []

    return False, nodes_visited, []
