import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from collections import OrderedDict
import numpy as np

# Configure matplotlib
import matplotlib.pyplot as plt
plt.style.use('dark_background')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PageReplacementAlgorithm:
    def __init__(self, total_frames):
        self.total_frames = total_frames
        self.memory = [-1] * total_frames
        self.page_faults = 0
        self.history = []

    def lru_replace(self, page_sequence):
        self.memory = [-1] * self.total_frames
        self.page_faults = 0
        access_history = OrderedDict()
        self.history = []

        for page in page_sequence:
            current_state = self.memory.copy()
            if page not in self.memory:
                self.page_faults += 1
                if -1 in self.memory:
                    # Empty frame available
                    idx = self.memory.index(-1)
                else:
                    # Find least recently used
                    lru_page = next(iter(access_history))
                    idx = self.memory.index(lru_page)
                    del access_history[lru_page]
                self.memory[idx] = page
            
            # Update access history
            if page in access_history:
                del access_history[page]
            access_history[page] = True
            
            self.history.append({
                'page': page,
                'state': current_state.copy(),
                'fault': page not in current_state
            })

        return self.page_faults, self.memory, self.history

    def optimal_replace(self, page_sequence):
        self.memory = [-1] * self.total_frames
        self.page_faults = 0
        self.history = []

        for i, page in enumerate(page_sequence):
            current_state = self.memory.copy()
            if page not in self.memory:
                self.page_faults += 1
                if -1 in self.memory:
                    # Empty frame available
                    idx = self.memory.index(-1)
                else:
                    # Find optimal victim
                    future_use = {}
                    for p in self.memory:
                        try:
                            future_use[p] = page_sequence[i:].index(p)
                        except ValueError:
                            future_use[p] = float('inf')
                    victim = max(future_use.items(), key=lambda x: x[1])[0]
                    idx = self.memory.index(victim)
                self.memory[idx] = page

            self.history.append({
                'page': page,
                'state': current_state.copy(),
                'fault': page not in current_state
            })

        return self.page_faults, self.memory, self.history

class VirtualMemorySimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Memory Management Simulator")
        self.root.geometry("1200x900")
        self.root.configure(bg='#1e1e1e')
        
        # Configure styles
        style = ttk.Style()
        style.configure('TFrame', background='#1e1e1e')
        style.configure('TLabel', background='#1e1e1e', foreground='#00ff00')
        style.configure('TButton', background='#404040', foreground='#00ff00')
        style.configure('TRadiobutton', background='#1e1e1e', foreground='#00ff00')
        style.configure('TEntry', fieldbackground='#404040', foreground='#00ff00')
        
        # Configure matplotlib style
        plt.style.use('dark_background')
        plt.rcParams.update({
            'grid.color': '#404040',
            'text.color': '#00ff00',
            'axes.labelcolor': '#00ff00',
            'axes.edgecolor': '#00ff00',
            'xtick.color': '#00ff00',
            'ytick.color': '#00ff00'
        })
        
        # Create main frames
        self.control_frame = ttk.Frame(root, padding="10")
        self.control_frame.pack(fill=tk.X)
        
        self.viz_frame = ttk.Frame(root, padding="10")
        self.viz_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_controls()
        self.setup_visualization()
        
    def setup_controls(self):
        # Create a tech-styled frame
        control_inner_frame = ttk.Frame(self.control_frame, style='TFrame')
        control_inner_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add a title label with tech font
        title_label = ttk.Label(control_inner_frame, 
                               text="VIRTUAL MEMORY SIMULATOR v1.0",
                               font=('Courier', 16, 'bold'),
                               foreground='#00ff00')
        title_label.pack(pady=(0, 20))
        # Frames input
        ttk.Label(self.control_frame, text="Number of Frames:").pack(side=tk.LEFT, padx=5)
        self.frames_var = tk.StringVar(value="4")
        ttk.Entry(self.control_frame, textvariable=self.frames_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Page sequence input
        ttk.Label(self.control_frame, text="Page Sequence (comma-separated):").pack(side=tk.LEFT, padx=5)
        self.sequence_var = tk.StringVar(value="1,2,3,4,1,2,5,1,2,3,4,5")
        ttk.Entry(self.control_frame, textvariable=self.sequence_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # Algorithm selection
        self.algorithm_var = tk.StringVar(value="LRU")
        ttk.Radiobutton(self.control_frame, text="LRU", variable=self.algorithm_var, value="LRU").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.control_frame, text="Optimal", variable=self.algorithm_var, value="Optimal").pack(side=tk.LEFT, padx=5)
        
        # Run button
        ttk.Button(self.control_frame, text="Run Simulation", command=self.run_simulation).pack(side=tk.LEFT, padx=5)
        
    def setup_visualization(self):
        # Create matplotlib figure with dark theme
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8), facecolor='#1e1e1e')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Results text with tech styling
        self.results_text = tk.Text(self.viz_frame, height=6, width=70,
                                  bg='#404040', fg='#00ff00',
                                  font=('Courier', 10),
                                  relief=tk.RIDGE)
        self.results_text.pack(fill=tk.X, padx=20, pady=10)
        
        # Add a border effect
        border_frame = ttk.Frame(self.viz_frame, style='TFrame')
        border_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="System Ready")
        status_label = ttk.Label(border_frame, 
                                textvariable=self.status_var,
                                font=('Courier', 10),
                                foreground='#00ff00')
        status_label.pack(side=tk.RIGHT)
        
    def run_simulation(self):
        try:
            frames = int(self.frames_var.get())
            sequence = [int(x.strip()) for x in self.sequence_var.get().split(',')]
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            return
            
        algorithm = PageReplacementAlgorithm(frames)
        
        if self.algorithm_var.get() == "LRU":
            faults, final_state, history = algorithm.lru_replace(sequence)
        else:
            faults, final_state, history = algorithm.optimal_replace(sequence)
            
        self.visualize_results(sequence, history, faults, final_state)
        
    def visualize_results(self, sequence, history, faults, final_state):
        self.status_var.set("Processing simulation...")
        self.root.update()
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        
        # Plot memory state changes
        states = np.array([h['state'] for h in history])
        im = self.ax1.imshow(states.T, aspect='auto', cmap='YlOrRd')
        self.ax1.set_title('Memory State Over Time')
        self.ax1.set_xlabel('Access Sequence')
        self.ax1.set_ylabel('Frame Number')
        
        # Plot page faults
        faults = [1 if h['fault'] else 0 for h in history]
        self.ax2.plot(faults, 'r-o', label='Page Fault')
        self.ax2.set_title('Page Faults')
        self.ax2.set_xlabel('Access Sequence')
        self.ax2.set_ylabel('Fault (1) / Hit (0)')
        self.ax2.grid(True)
        
        self.fig.tight_layout()
        self.canvas.draw()
        self.status_var.set(f"Simulation completed - {sum(faults)} page faults detected")
        
        # Update results text
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Total Page Faults: {sum(faults)}\n")
        self.results_text.insert(tk.END, f"Page Fault Rate: {(sum(faults)/len(faults))*100:.2f}%\n")
        self.results_text.insert(tk.END, f"Final Memory State: {final_state}\n")
        self.results_text.insert(tk.END, f"Access Sequence: {' → '.join(map(str, sequence))}\n")

def main():
    root = ThemedTk(theme="equilux")
    app = VirtualMemorySimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
