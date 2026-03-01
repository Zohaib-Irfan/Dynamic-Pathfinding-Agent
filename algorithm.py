import pygame
import math
from queue import PriorityQueue

def calc_h(pt1, pt2, h_type):
    val_x1, val_y1 = pt1
    val_x2, val_y2 = pt2
    if h_type == "Manhattan":
        return abs(val_x1 - val_x2) + abs(val_y1 - val_y2)
    elif h_type == "Euclidean":
        return math.sqrt((val_x1 - val_x2)**2 + (val_y1 - val_y2)**2)
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

def a_star_search(draw_fn, grid_structure, start_n, end_n, h_type):
    sequence = 0
    pq = PriorityQueue()
    pq.put((0, sequence, start_n))
    parent_map = {}
    g = {n: float("inf") for r in grid_structure for n in r}
    g[start_n] = 0
    f = {n: float("inf") for r in grid_structure for n in r}
    f[start_n] = calc_h(start_n.get_pos(), end_n.get_pos(), h_type)

    pq_hash = {start_n}
    expansions = 0

    while not pq.empty():
        curr = pq.get()[2]
        pq_hash.remove(curr)

        if curr == end_n:
            final_route = reconstruct_path(parent_map, end_n, draw_fn)
            yield True, expansions, final_route
            return

        for neighbor in curr.neighbors:
            t_g_score = g[curr] + 1

            if t_g_score < g[neighbor]:
                parent_map[neighbor] = curr
                g[neighbor] = t_g_score
                f[neighbor] = t_g_score + calc_h(neighbor.get_pos(), end_n.get_pos(), h_type)
                if neighbor not in pq_hash:
                    sequence += 1
                    pq.put((f[neighbor], sequence, neighbor))
                    pq_hash.add(neighbor)
                    if not neighbor.is_end() and not neighbor.is_start():
                        neighbor.make_open()

        if curr != start_n and curr != end_n:
            curr.make_closed()
        expansions += 1
        yield False, expansions, []

    return False, expansions, []

def gbfs_search(draw_fn, grid_structure, start_n, end_n, h_type):
    sequence = 0
    pq = PriorityQueue()
    pq.put((0, sequence, start_n))
    parent_map = {}
    
    pq_hash = {start_n}
    seen = {start_n}
    expansions = 0

    while not pq.empty():
        curr = pq.get()[2]
        pq_hash.remove(curr)

        if curr == end_n:
            final_route = reconstruct_path(parent_map, end_n, draw_fn)
            yield True, expansions, final_route
            return

        for neighbor in curr.neighbors:
            if neighbor not in seen and not neighbor.is_barrier():
                seen.add(neighbor)
                parent_map[neighbor] = curr
                h_val = calc_h(neighbor.get_pos(), end_n.get_pos(), h_type)
                sequence += 1
                pq.put((h_val, sequence, neighbor))
                pq_hash.add(neighbor)
                if not neighbor.is_end() and not neighbor.is_start():
                    neighbor.make_open()

        if curr != start_n and curr != end_n:
            curr.make_closed()
            
        expansions += 1
        yield False, expansions, []

    return False, expansions, []
