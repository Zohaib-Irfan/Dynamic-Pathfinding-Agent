import random

def spawn_random_obstacle(grid, start, end, spawn_chance_percentage, current_path=None):
    if random.random() > (spawn_chance_percentage / 100.0):
        return False
        
    empty_nodes = []
    for row in grid:
        for node in row:
            if not node.is_barrier() and node != start and node != end:
                empty_nodes.append(node)
                
    if not empty_nodes:
        return False
        
    target_node = random.choice(empty_nodes)
    target_node.make_barrier()
    
    if current_path and target_node in current_path:
        return True
        
    return False
