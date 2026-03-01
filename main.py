import pygame
import tkinter as tk
from tkinter import ttk, messagebox
import time

from grid_utils import make_grid, draw, get_clicked_pos, generate_random_maze, reset_search
from algorithm import a_star_search, gbfs_search
from dynamic_mode import spawn_random_obstacle
from node import WHITE, PURPLE

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH + 100))
pygame.display.set_caption("Dynamic Pathfinding Agent")

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 24)

class AppConfig:
    def __init__(self):
        self.rows = 50
        self.algorithm = "A*"
        self.heuristic = "Manhattan"
        self.density = 30
        self.dynamic_mode = False
        self.ready = False

def get_config_from_ui():
    config = AppConfig()
    
    root = tk.Tk()
    root.title("Pathfinding Config")
    root.geometry("350x300")
    
    tk.Label(root, text="Grid Size (NxN):").pack(pady=5)
    size_var = tk.IntVar(value=50)
    tk.Entry(root, textvariable=size_var).pack()
    
    tk.Label(root, text="Algorithm:").pack(pady=5)
    algo_var = tk.StringVar(value="A*")
    ttk.Combobox(root, textvariable=algo_var, values=["A*", "GBFS"], state="readonly").pack()
    
    tk.Label(root, text="Heuristic:").pack(pady=5)
    heur_var = tk.StringVar(value="Manhattan")
    ttk.Combobox(root, textvariable=heur_var, values=["Manhattan", "Euclidean"], state="readonly").pack()
    
    tk.Label(root, text="Random Map Density (%):").pack(pady=5)
    density_var = tk.IntVar(value=30)
    tk.Entry(root, textvariable=density_var).pack()
    
    dyn_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Enable Dynamic Mode", variable=dyn_var).pack(pady=5)
    
    def on_start():
        try:
            config.rows = size_var.get()
            config.algorithm = algo_var.get()
            config.heuristic = heur_var.get()
            config.density = density_var.get()
            config.dynamic_mode = dyn_var.get()
            config.ready = True
            root.destroy()
        except:
            messagebox.showerror("Error", "Invalid input values")

    tk.Button(root, text="Start Simulation", command=on_start).pack(pady=15)
    
    def on_closing():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    return config

def draw_metrics(win, nodes_visited, path_cost, exec_time_ms, algo, heur, dyn):
    # A slightly nicer dark grey background for the UI panel
    pygame.draw.rect(win, (30, 32, 35), (0, WIDTH, WIDTH, 100))
    pygame.draw.line(win, (100, 100, 100), (0, WIDTH), (WIDTH, WIDTH), 2)
    
    dyn_text = "ON" if dyn else "OFF"
    dyn_color = (0, 255, 0) if dyn else (255, 100, 100)
    
    text_algo = STAT_FONT.render(f"Algo: {algo} ({heur})", True, WHITE)
    text_dyn = STAT_FONT.render(f"Dyn: {dyn_text}", True, dyn_color)
    text_visited = STAT_FONT.render(f"Nodes Visited: {nodes_visited}", True, (200, 200, 255))
    text_cost = STAT_FONT.render(f"Path Cost: {path_cost}", True, (200, 255, 200))
    text_time = STAT_FONT.render(f"Exec Time: {exec_time_ms:.2f} ms", True, (255, 200, 200))
    text_help = STAT_FONT.render("LMB: Draw | RMB: Erase | SPACE: Start | C: Clear | R: Rand Maze", True, (150, 150, 150))
    
    win.blit(text_algo, (20, WIDTH + 10))
    win.blit(text_dyn, (250, WIDTH + 10))
    win.blit(text_visited, (20, WIDTH + 40))
    
    win.blit(text_cost, (WIDTH // 2 + 50, WIDTH + 10))
    win.blit(text_time, (WIDTH // 2 + 50, WIDTH + 40))
    
    win.blit(text_help, (20, WIDTH + 70))

def main():
    config = get_config_from_ui()
    if not config.ready:
        pygame.quit()
        return
        
    ROWS = config.rows
    grid = make_grid(ROWS, WIDTH)
    
    start = None
    end = None
    
    run = True
    started = False
    
    nodes_visited = 0
    path_cost = 0
    exec_time = 0
    
    in_transit = False
    current_path = []
    agent_pos_idx = 0
    transit_speed_ms = 50
    last_transit_time = 0
    
    search_generator = None
    start_time = 0
    
    def draw_func():
        draw(WIN, grid, ROWS, WIDTH)
        draw_metrics(WIN, nodes_visited, path_cost, exec_time, config.algorithm, config.heuristic, config.dynamic_mode)
        pygame.display.update()

    clock = pygame.time.Clock()
    
    while run:
        clock.tick(60)
        draw_func()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if started or in_transit:
                continue
                
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[1] >= WIDTH: continue
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                node = grid[row][col]
                
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != start and node != end:
                    node.make_barrier()
                    
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[1] >= WIDTH: continue
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                node = grid[row][col]
                node.reset()
                if node == start: start = None
                if node == end: end = None
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not started and not in_transit:
                    if start and end:
                        generate_random_maze(grid, start, end, config.density)
                        
                if event.key == pygame.K_c and not started and not in_transit:
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)
                    nodes_visited = 0
                    path_cost = 0
                    exec_time = 0
                    
                if event.key == pygame.K_SPACE and not started and not in_transit:
                    if start and end:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                        
                        reset_search(grid, start, end)
                        
                        started = True
                        if config.algorithm == "A*":
                            search_generator = a_star_search(lambda: None, grid, start, end, config.heuristic)
                        else:
                            search_generator = gbfs_search(lambda: None, grid, start, end, config.heuristic)
                        
                        start_time = time.perf_counter()
                        
        if started and search_generator:
            try:
                for _ in range(50):
                    result = next(search_generator, None)
                    if result is None:
                        started = False
                        search_generator = None
                        exec_time = (time.perf_counter() - start_time) * 1000
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showinfo("No Path", "No valid path exists between start and end nodes.")
                        root.destroy()
                        break
                        
                    finished, visited, path = result
                    nodes_visited = visited
                    
                    if finished:
                        exec_time = (time.perf_counter() - start_time) * 1000
                        started = False
                        search_generator = None
                        path_cost = len(path)
                        
                        if path_cost > 0:
                            in_transit = True
                            current_path = path
                            agent_pos_idx = 0
                            last_transit_time = pygame.time.get_ticks()
                        break
                        
            except StopIteration:
                exec_time = (time.perf_counter() - start_time) * 1000
                started = False
                search_generator = None
                
        if in_transit and config.dynamic_mode:
            current_t = pygame.time.get_ticks()
            if current_t - last_transit_time > transit_speed_ms:
                last_transit_time = current_t
                
                if agent_pos_idx < len(current_path):
                    prev_node = current_path[agent_pos_idx-1] if agent_pos_idx > 0 else start
                    if prev_node != start and prev_node != end:
                        prev_node.make_path()
                        
                    current_node = current_path[agent_pos_idx]
                    if current_node != end:
                        current_node.color = PURPLE
                        
                    agent_pos_idx += 1
                    
                    replan_needed = spawn_random_obstacle(grid, start, end, 5, current_path[agent_pos_idx:])
                    if replan_needed:
                        in_transit = False
                        reset_search(grid, current_node, end)
                        
                        if start != current_node:
                            start.make_path()
                        
                        start = current_node
                        start.make_start()
                        
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                        
                        started = True
                        if config.algorithm == "A*":
                            search_generator = a_star_search(lambda: None, grid, start, end, config.heuristic)
                        else:
                            search_generator = gbfs_search(lambda: None, grid, start, end, config.heuristic)
                            
                        start_time = time.perf_counter()
                else:
                    in_transit = False
                    
    pygame.quit()

if __name__ == "__main__":
    main()
