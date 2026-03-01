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
        self.delay_ms = 0
        self.dynamic_mode = False
        self.ready = False

def get_config_from_ui():
    config = AppConfig()
    
    root = tk.Tk()
    root.title("Pathfinding Config")
    root.geometry("350x400")
    
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
    
    tk.Label(root, text="Delay (ms):").pack(pady=5)
    delay_var = tk.IntVar(value=0)
    tk.Entry(root, textvariable=delay_var).pack()
    
    dyn_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Enable Dynamic Mode", variable=dyn_var).pack(pady=5)
    
    def on_start():
        try:
            config.rows = size_var.get()
            config.algorithm = algo_var.get()
            config.heuristic = heur_var.get()
            config.density = density_var.get()
            config.delay_ms = delay_var.get()
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

    pygame.draw.rect(win, (30, 32, 35), (0, WIDTH, WIDTH, 100))
    pygame.draw.line(win, (100, 100, 100), (0, WIDTH), (WIDTH, WIDTH), 2)
    
    dyn_text = "ON" if dyn else "OFF"
    dyn_color = (0, 255, 0) if dyn else (255, 100, 100)
    
    text_algo = STAT_FONT.render(f"Algo: {algo} ({heur})", True, WHITE)
    text_dyn = STAT_FONT.render(f"Dyn: {dyn_text}", True, dyn_color)
    text_visited = STAT_FONT.render(f"Nodes Visited: {nodes_visited}", True, (200, 200, 255))
    text_cost = STAT_FONT.render(f"Path Cost: {path_cost}", True, (200, 255, 200))
    text_time = STAT_FONT.render(f"Exec Time: {exec_time_ms:.2f} ms", True, (255, 200, 200))
    text_help = STAT_FONT.render("LMB: Draw | RMB: Erase | SPACE: Start | C: Clear | R: Rand | ESC: Back", True, (150, 150, 150))
    
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
    
    app_running = True
    algo_started = False
    
    count_visited = 0
    route_cost = 0
    time_taken = 0
    
    moving_agent = False
    active_path = []
    idx_pos = 0
    speed_transit_ms = 50
    time_last_move = 0
    
    gen_search = None
    t_start = 0
    
    def render_all():
        draw(WIN, grid, ROWS, WIDTH)
        draw_metrics(WIN, count_visited, route_cost, time_taken, config.algorithm, config.heuristic, config.dynamic_mode)
        pygame.display.update()

    fps_clock = pygame.time.Clock()
    
    while app_running:
        fps_clock.tick(60)
        render_all()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_running = False
                return False
                
            if algo_started or moving_agent:
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
                if event.key == pygame.K_r and not algo_started and not moving_agent:
                    if start and end:
                        generate_random_maze(grid, start, end, config.density)
                        
                if event.key == pygame.K_c and not algo_started and not moving_agent:
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)
                    count_visited = 0
                    route_cost = 0
                    time_taken = 0
                    
                if event.key == pygame.K_ESCAPE and not algo_started and not moving_agent:
                    app_running = False
                    return True
                    
                if event.key == pygame.K_SPACE and not algo_started and not moving_agent:
                    if start and end:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                        
                        reset_search(grid, start, end)
                        
                        algo_started = True
                        if config.algorithm == "A*":
                            gen_search = a_star_search(lambda: None, grid, start, end, config.heuristic)
                        else:
                            gen_search = gbfs_search(lambda: None, grid, start, end, config.heuristic)
                        
                        t_start = time.perf_counter()
                        
        if algo_started and gen_search:
            try:
                steps_per_frame = 1 if config.delay_ms > 0 else 50
                
                for _ in range(steps_per_frame):
                    if config.delay_ms > 0:
                        pygame.time.delay(config.delay_ms)
                        
                    result = next(gen_search, None)
                    if result is None:
                        algo_started = False
                        gen_search = None
                        time_taken = (time.perf_counter() - t_start) * 1000
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showinfo("No Path", "No valid path exists between start and end nodes.")
                        root.destroy()
                        break
                        
                    finished, visited, path = result
                    count_visited = visited
                    
                    if finished:
                        time_taken = (time.perf_counter() - t_start) * 1000
                        algo_started = False
                        gen_search = None
                        route_cost = len(path)
                        
                        if route_cost > 0 and config.dynamic_mode:
                            moving_agent = True
                            active_path = path
                            idx_pos = 0
                            time_last_move = pygame.time.get_ticks()
                        break
                        
            except StopIteration:
                time_taken = (time.perf_counter() - t_start) * 1000
                algo_started = False
                gen_search = None
                
        if moving_agent and config.dynamic_mode:
            current_t = pygame.time.get_ticks()
            if current_t - time_last_move > speed_transit_ms:
                time_last_move = current_t
                
                if idx_pos < len(active_path):
                    prev_node = active_path[idx_pos-1] if idx_pos > 0 else start
                    if prev_node != start and prev_node != end:
                        prev_node.make_path()
                        
                    current_node = active_path[idx_pos]
                    if current_node != end:
                        current_node.color = PURPLE
                        
                    idx_pos += 1
                    
                    replan_needed = spawn_random_obstacle(grid, start, end, 5, active_path[idx_pos:])
                    if replan_needed:
                        moving_agent = False
                        reset_search(grid, current_node, end)
                        
                        if start != current_node:
                            start.make_path()
                        
                        start = current_node
                        start.make_start()
                        
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                        
                        algo_started = True
                        if config.algorithm == "A*":
                            gen_search = a_star_search(lambda: None, grid, start, end, config.heuristic)
                        else:
                            gen_search = gbfs_search(lambda: None, grid, start, end, config.heuristic)
                            
                        t_start = time.perf_counter()
                else:
                    moving_agent = False
                    
    pygame.quit()
    return False

if __name__ == "__main__":
    while True:
        pygame.init()
        should_restart = main()
        if not should_restart:
            break
