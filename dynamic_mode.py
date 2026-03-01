import random

def spawn_random_obstacle(grid_matrix, p_start, p_end, spawn_chance_pct, active_path=None):
    if random.random() > (spawn_chance_pct / 100.0):
        return False
        
    available_nodes = []
    for r in grid_matrix:
        for n in r:
            if not n.is_barrier() and n != p_start and n != p_end:
                available_nodes.append(n)
                
    if len(available_nodes) == 0:
        return False
        
    selected_node = random.choice(available_nodes)
    selected_node.make_barrier()
    
    if active_path and selected_node in active_path:
        return True
        
    return False
