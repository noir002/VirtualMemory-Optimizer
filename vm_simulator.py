import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from collections import OrderedDict
import numpy as np
import subprocess
import re
import random

# Configure matplotlib - use simplest backend
import matplotlib
matplotlib.use('TkAgg', force=True)  # Force TkAgg backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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
        # Neo-inspired color scheme
        self.BACKGROUND_COLOR = '#0c1021'  # Dark blue background
        self.ACCENT_COLOR = '#00ffff'      # Cyan accent
        self.SECONDARY_COLOR = '#007acc'   # Lighter blue
        self.TEXT_COLOR = '#ffffff'        # White text
        self.HIGHLIGHT_COLOR = '#1e90ff'   # Bright blue highlight
        
        self.root.configure(bg=self.BACKGROUND_COLOR)
        
        # Flag to control auto-refresh
        self.simulation_running = False
        self.force_refresh = True
        self.last_selected_pid = None
        
        # Configure styles
        style = ttk.Style()
        style.configure('TFrame', background=self.BACKGROUND_COLOR)
        style.configure('TLabel', background=self.BACKGROUND_COLOR, foreground=self.ACCENT_COLOR)
        style.configure('TButton', background=self.SECONDARY_COLOR, foreground=self.TEXT_COLOR)
        style.configure('TRadiobutton', background=self.BACKGROUND_COLOR, foreground=self.ACCENT_COLOR)
        style.configure('TEntry', fieldbackground=self.SECONDARY_COLOR, foreground=self.TEXT_COLOR)
        
        # Create main frames
        self.control_frame = ttk.Frame(root, padding="10")
        self.control_frame.pack(fill=tk.X)
        
        self.viz_frame = ttk.Frame(root, padding="10")
        self.viz_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_controls()
        self.setup_visualization()
        
        # Initialize process list
        self.process_list = []
        self.update_process_list()
        
    def get_running_processes(self):
        """Get list of running processes with their PIDs, CPU and memory usage"""
        try:
            # Run ps command to get process information
            result = subprocess.run(
                ['ps', '-eo', 'pid,pcpu,pmem,comm'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            processes = []
            # Parse the output, skipping the header line
            for line in result.stdout.strip().split('\n')[1:]:
                parts = re.split(r'\s+', line.strip(), maxsplit=3)
                if len(parts) >= 4:
                    pid, cpu, mem, name = parts
                    # Extract the base name from path
                    base_name = name.split('/')[-1]
                    processes.append({
                        'pid': pid,
                        'cpu': cpu,
                        'mem': mem,
                        'name': base_name
                    })
            
            # Sort by memory usage (highest first)
            return sorted(processes, key=lambda x: float(x['mem']), reverse=True)
        except subprocess.SubprocessError as e:
            messagebox.showerror("Error", f"Failed to get process list: {str(e)}")
            return []
            
    def update_process_list(self):
        """Update the list of running processes"""
        try:
            # Skip updates if simulation is running and not forced
            if self.simulation_running and not self.force_refresh:
                self.root.after(10000, self.update_process_list)
                return
                
            self.force_refresh = False
            self.process_list = self.get_running_processes()
            
            # Update the dropdown values
            process_values = [f"{p['pid']} - {p['name']} (CPU: {p['cpu']}%, MEM: {p['mem']}%)" 
                            for p in self.process_list]
            
            if hasattr(self, 'process_dropdown'):
                # Save current selection if possible
                current_selection = self.selected_process.get()
                current_pid = None
                
                if current_selection:
                    try:
                        current_pid = current_selection.split(' - ')[0].strip()
                    except:
                        pass
                
                # Update dropdown options
                self.process_dropdown['values'] = process_values
                
                # Try to preserve the selected PID after refresh
                if current_pid and self.last_selected_pid:
                    # Look for the same PID in the new list
                    for i, proc in enumerate(process_values):
                        if proc.startswith(current_pid + ' '):
                            self.process_dropdown.current(i)
                            self.selected_process.set(proc)
                            print(f"DEBUG: Preserved selection of PID {current_pid}")
                            break
                elif process_values:
                    self.process_dropdown.current(0)
                    self.selected_process.set(process_values[0])
            
            # Schedule periodic updates with reduced frequency
            self.root.after(10000, self.update_process_list)  # Every 10 seconds
        except Exception as e:
            print(f"DEBUG: Error updating process list: {str(e)}")
            # Still schedule next update even if this one fails
            self.root.after(10000, self.update_process_list)
    
    def setup_controls(self):
        # Create a tech-styled frame
        control_inner_frame = ttk.Frame(self.control_frame, style='TFrame')
        control_inner_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add a title label with tech font
        title_label = ttk.Label(control_inner_frame, 
                               text="VIRTUAL MEMORY SIMULATOR v1.0",
                               font=('Courier', 16, 'bold'),
                               foreground=self.ACCENT_COLOR)
        subtitle_label = ttk.Label(control_inner_frame,
                                  text="[ MATRIX SYSTEMS INITIALIZED ]",
                                  font=('Courier', 10),
                                  foreground=self.SECONDARY_COLOR)
        subtitle_label.pack(pady=(0, 10))
        title_label.pack(pady=(0, 20))
        
        # Create a frame for process selection
        process_frame = ttk.Frame(self.control_frame)
        process_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(process_frame, text="Select Running Process:").pack(side=tk.LEFT, padx=5)
        self.selected_process = tk.StringVar()
        self.process_dropdown = ttk.Combobox(process_frame, 
                                            textvariable=self.selected_process,
                                            width=50,
                                            state="readonly")
        self.process_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Bind selection event to clear page sequence when process is selected
        def on_process_selected(event):
            # Get the newly selected process
            selection = self.selected_process.get()
            if selection:
                try:
                    pid = selection.split(' - ')[0].strip()
                    self.last_selected_pid = pid
                    print(f"DEBUG: User selected process with PID: {pid}")
                    
                    # Clear the page sequence field when a process is selected
                    self.sequence_var.set("")
                    
                    # Disable auto-refresh temporarily to ensure the selection sticks
                    self.simulation_running = True
                    self.root.after(2000, self.enable_refresh)
                except Exception as e:
                    print(f"DEBUG: Error in process selection: {str(e)}")
        
        self.process_dropdown.bind("<<ComboboxSelected>>", on_process_selected)
        
        # Refresh button for process list
        ttk.Button(process_frame, 
                  text="↻", 
                  width=3,
                  command=lambda: self.manual_refresh()).pack(side=tk.LEFT, padx=5)
        
        # Create a frame for simulation parameters
        sim_frame = ttk.Frame(self.control_frame)
        sim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Frames input
        ttk.Label(sim_frame, text="Number of Frames:").pack(side=tk.LEFT, padx=5)
        self.frames_var = tk.StringVar(value="4")
        ttk.Entry(sim_frame, textvariable=self.frames_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Page sequence input (now optional, will be populated from process)
        ttk.Label(sim_frame, text="Page Sequence (optional):").pack(side=tk.LEFT, padx=5)
        self.sequence_var = tk.StringVar(value="")
        ttk.Entry(sim_frame, textvariable=self.sequence_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # Algorithm selection
        self.algorithm_var = tk.StringVar(value="LRU")
        ttk.Radiobutton(sim_frame, text="LRU", variable=self.algorithm_var, value="LRU").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sim_frame, text="Optimal", variable=self.algorithm_var, value="Optimal").pack(side=tk.LEFT, padx=5)
        
        # Run button
        ttk.Button(sim_frame, text="Run Simulation", command=self.run_simulation).pack(side=tk.LEFT, padx=5)
        
    def enable_refresh(self):
        """Re-enable the auto-refresh after a delay"""
        self.simulation_running = False
        print("DEBUG: Auto-refresh re-enabled")
        
    def setup_visualization(self):
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8), facecolor=self.BACKGROUND_COLOR)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        
        # Configure axes colors
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor(self.BACKGROUND_COLOR)
            ax.tick_params(colors=self.ACCENT_COLOR)
            for spine in ax.spines.values():
                spine.set_edgecolor(self.ACCENT_COLOR)
                
        # Add space between subplots
        self.fig.subplots_adjust(hspace=0.3)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Results text with tech styling
        self.results_text = tk.Text(self.viz_frame, height=6, width=70,
                                  bg=self.SECONDARY_COLOR, fg=self.TEXT_COLOR,
                                  font=('Courier', 10),
                                  relief=tk.RIDGE,
                                  insertbackground=self.ACCENT_COLOR)
        self.results_text.pack(fill=tk.X, padx=20, pady=10)
        
        # Add a border effect
        border_frame = ttk.Frame(self.viz_frame, style='TFrame')
        border_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="System Ready")
        status_label = ttk.Label(border_frame, 
                                textvariable=self.status_var,
                                font=('Courier', 10),
                                foreground=self.ACCENT_COLOR)
        status_label.pack(side=tk.RIGHT)
        
    def get_process_memory_pages(self, pid):
        """Generate simulated memory page accesses based on actual process memory info"""
        try:
            print(f"DEBUG: Getting memory info for PID {pid}")
            # Check if the process still exists
            if not self.process_exists(pid):
                print(f"DEBUG: Process {pid} no longer exists")
                raise ValueError(f"Process with PID {pid} no longer exists")
                
            # Get memory stats for the process using ps
            result = subprocess.run(
                ['ps', '-o', 'pid,rss,vsz,command', '-p', pid], 
                capture_output=True, 
                text=True,
                check=True
            )
            
            # Parse output, skip header
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                raise ValueError(f"No process found with PID {pid}")
                
            # Split the line by whitespace
            parts = re.split(r'\s+', lines[1].strip(), maxsplit=3)
            if len(parts) < 3:
                raise ValueError(f"Unexpected output format from ps command")
                
            # Extract RSS (Resident Set Size) and VSZ (Virtual Memory Size)
            rss = int(parts[1])  # In KB
            vsz = int(parts[2])  # In KB
            
            print(f"DEBUG: Process stats - RSS: {rss}KB, VSZ: {vsz}KB")
            # Calculate the number of pages based on memory size
            page_size = 4096  # 4KB page size (standard on most systems)
            num_pages = min(10, max(4, int(rss / (1024 * 10))))  # Scale down for visualization
            print(f"DEBUG: Using {num_pages} pages for simulation")
            
            # Generate a sequence that simulates memory access patterns
            sequence = []
            # Create "hot" pages (frequently accessed)
            hot_pages = list(range(1, min(5, num_pages) + 1))
            # Create "cold" pages (less frequently accessed)
            cold_pages = list(range(min(5, num_pages) + 1, num_pages + 1))
            
            # Ratio of RSS to VSZ gives an idea of memory usage pattern
            locality_factor = min(0.8, max(0.2, rss / vsz))
            print(f"DEBUG: Locality factor: {locality_factor}")
            
            # Generate sequence with locality of reference based on real memory usage
            for i in range(30):  # Generate 30 page accesses
                if random.random() < locality_factor:
                    # Access a hot page (representing frequent access)
                    if hot_pages:
                        sequence.append(random.choice(hot_pages))
                    else:
                        sequence.append(1)  # Fallback if no hot pages
                else:
                    # Access a cold page or introduce a new page
                    if i > 20 and random.random() < 0.3:
                        # Occasionally introduce a page fault by accessing new page
                        sequence.append(num_pages + 1 + len(set(sequence)))
                    elif cold_pages:
                        sequence.append(random.choice(cold_pages))
                    else:
                        sequence.append(random.choice(range(1, num_pages + 1)))
            
            print(f"DEBUG: Generated sequence: {sequence}")
            self.status_var.set(f"Generated sequence based on PID {pid} (RSS: {rss}KB, VSZ: {vsz}KB)")
            return sequence
            
        except Exception as e:
            print(f"DEBUG: Error in get_process_memory_pages: {str(e)}")
            messagebox.showwarning("Warning", f"Couldn't get memory info for PID {pid}: {str(e)}\nUsing simulated data.")
            # Fallback to a default sequence
            return [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    
    def process_exists(self, pid):
        """Check if a process with given PID exists"""
        try:
            result = subprocess.run(
                ['ps', '-p', pid], 
                capture_output=True, 
                text=True,
                check=True
            )
            # If we have at least 2 lines (header + process), the process exists
            return len(result.stdout.strip().split('\n')) >= 2
        except subprocess.CalledProcessError:
            # Command returns non-zero exit code when process doesn't exist
            return False
        except Exception as e:
            print(f"DEBUG: Error checking process existence: {str(e)}")
            return False
     
    def manual_refresh(self):
        """Manual refresh of the process list"""
        print("DEBUG: Manual refresh triggered")
        self.force_refresh = True
        
        # Temporarily clear the current selection to force a complete refresh
        current = self.selected_process.get()
        self.selected_process.set("")
        
        # Update the list
        self.update_process_list()
        
        # After updating, try to restore selection if still valid
        if current:
            try:
                pid = current.split(' - ')[0].strip()
                for i, proc_str in enumerate(self.process_dropdown['values']):
                    if proc_str.startswith(pid + ' '):
                        self.process_dropdown.current(i)
                        self.selected_process.set(proc_str)
                        break
            except Exception as e:
                print(f"DEBUG: Error restoring selection after refresh: {str(e)}")
                pass
        
    def run_simulation(self):
        try:
            print("DEBUG: Starting simulation")
            # Set flag to prevent refresh during simulation
            self.simulation_running = True
            
            # Clear previous results first
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Running simulation...\n")
            self.root.update()
            
            frames = int(self.frames_var.get())
            print(f"DEBUG: Using {frames} frames")
            
            # Check if we should use process-based pages or manual entry
            if self.selected_process.get() and not self.sequence_var.get():
                # Get the current actual selection
                process_selection = self.selected_process.get()
                print(f"DEBUG: Using process-based sequence from {process_selection}")
                
                # Extract PID from the selected process string
                selected_pid = process_selection.split(' - ')[0].strip()
                print(f"DEBUG: Extracted PID: {selected_pid}")
                
                # Store this as the last selected PID to preserve it
                self.last_selected_pid = selected_pid
                
                # Get memory pages for this process
                sequence = self.get_process_memory_pages(selected_pid)
                # Update the sequence field for user visibility
                self.sequence_var.set(','.join(map(str, sequence)))
            else:
                print("DEBUG: Using manually entered sequence")
                # Use manually entered sequence
                sequence = [int(x.strip()) for x in self.sequence_var.get().split(',') if x.strip()]
                
            if not sequence:
                print("DEBUG: No sequence provided")
                messagebox.showerror("Error", "No page sequence provided")
                self.simulation_running = False
                return
                
            print(f"DEBUG: Final sequence length: {len(sequence)}")    
            algorithm = PageReplacementAlgorithm(frames)
            
            print(f"DEBUG: Running {self.algorithm_var.get()} algorithm")
            if self.algorithm_var.get() == "LRU":
                faults, final_state, history = algorithm.lru_replace(sequence)
            else:
                faults, final_state, history = algorithm.optimal_replace(sequence)
            
            print("DEBUG: Simulation completed, visualizing results")
            self.visualize_results(sequence, history, faults, final_state)
            
            # Simulation is done, allow refreshes again
            self.simulation_running = False
            
        except Exception as e:
            print(f"DEBUG: Error in run_simulation: {str(e)}")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Simulation error: {str(e)}\n")
            messagebox.showerror("Error", f"Simulation error: {str(e)}")
            self.simulation_running = False
            return
        
    def visualize_results(self, sequence, history, faults, final_state):
        print("DEBUG: Starting visualization")
        self.status_var.set("Processing simulation...")
        self.root.update()
        
        # Initialize faults_array at the beginning to ensure it's always defined
        faults_array = [1 if h['fault'] else 0 for h in history]
        
        try:
            # Clear previous plots
            self.ax1.clear()
            self.ax2.clear()
            
            print("DEBUG: Plotting memory states")
            # Plot memory state changes with custom colormap
            states = np.array([h['state'] for h in history])
            im = self.ax1.imshow(states.T, aspect='auto', cmap='Blues_r')
            
            # Styling
            self.ax1.set_title('Memory State Over Time', color=self.ACCENT_COLOR)
            self.ax1.set_xlabel('Access Sequence', color=self.ACCENT_COLOR)
            self.ax1.set_ylabel('Frame Number', color=self.ACCENT_COLOR)
            
            # Plot page faults
            print("DEBUG: Plotting page faults")
            self.ax2.plot(faults_array, '-o', color=self.ACCENT_COLOR, label='Page Fault',
                         markerfacecolor=self.HIGHLIGHT_COLOR)
            
            # Styling
            self.ax2.set_title('Page Faults', color=self.ACCENT_COLOR)
            self.ax2.set_xlabel('Access Sequence', color=self.ACCENT_COLOR)
            self.ax2.set_ylabel('Fault (1) / Hit (0)', color=self.ACCENT_COLOR)
            self.ax2.grid(True, color=self.SECONDARY_COLOR, alpha=0.3)
            
            # Update layout
            print("DEBUG: Updating layout")
            self.fig.tight_layout()
            
            # Draw
            print("DEBUG: Drawing canvas")
            self.canvas.draw()
            self.root.update()
            
            print("DEBUG: Canvas drawn successfully")
        except Exception as e:
            print(f"DEBUG: Error in visualization: {str(e)}")
            # Create a simple text-based visualization as fallback
            self.status_var.set(f"Error in plot visualization. Using text output. Error: {str(e)}")
            self.create_text_visualization(sequence, history, faults_array, final_state)
        
        # Check if we're using a real process
        process_info = ""
        try:
            if self.selected_process.get():
                try:
                    # Get selected PID
                    selected_pid = self.selected_process.get().split(' - ')[0].strip()
                    
                    print(f"DEBUG: Getting detailed info for PID {selected_pid}")
                    # Get detailed process info
                    result = subprocess.run(
                        ['ps', '-o', 'pid,rss,vsz,%cpu,%mem,command', '-p', selected_pid],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    if len(result.stdout.strip().split('\n')) >= 2:
                        process_info = "Process: " + self.selected_process.get() + "\n"
                        process_info += "Details: " + result.stdout.strip().split('\n')[1] + "\n\n"
                except Exception as e:
                    print(f"DEBUG: Error getting process info: {str(e)}")
                    # Ignore errors getting process info
                    pass
            
            total_faults = sum(faults_array)
            fault_rate = (total_faults / len(faults_array)) * 100
            
            print("DEBUG: Updating status and results text")
            self.status_var.set(f"Simulation completed - {total_faults} page faults detected")
            
            # Update results text
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, process_info)
            self.results_text.insert(tk.END, f"Total Page Faults: {total_faults}\n")
            self.results_text.insert(tk.END, f"Page Fault Rate: {fault_rate:.2f}%\n")
            self.results_text.insert(tk.END, f"Final Memory State: {final_state}\n")
            self.results_text.insert(tk.END, f"Access Sequence: {' → '.join(map(str, sequence))}\n")
            
            print("DEBUG: Visualization completed successfully")
        except Exception as e:
            print(f"DEBUG: Error updating results: {str(e)}")
            messagebox.showerror("Error", f"Error displaying results: {str(e)}")
            
            # Last resort fallback to show at least some results
            try:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "Error displaying full results. Basic information:\n\n")
                self.results_text.insert(tk.END, f"Sequence length: {len(sequence)}\n")
                self.results_text.insert(tk.END, f"Page faults: {sum(faults_array)}\n")
                self.results_text.insert(tk.END, f"Final state: {final_state}\n")
            except:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "Error displaying results.\n")
                
    def create_text_visualization(self, sequence, history, faults, final_state):
        """Create a simple text-based visualization as fallback"""
        try:
            print("DEBUG: Creating text-based visualization")
            # Create a text-based visualization in the results area
            summary = "VISUALIZATION (TEXT FORMAT):\n"
            summary += "-" * 50 + "\n"
            
            # Show page faults
            summary += "PAGE FAULTS:\n"
            for i, (fault, page) in enumerate(zip(faults, sequence)):
                symbol = "X" if fault else "."
                summary += f"{symbol} "
                if (i + 1) % 20 == 0:
                    summary += "\n"
            
            summary += "\n\n"
            
            # Show memory states
            summary += "MEMORY STATES:\n"
            for i, state in enumerate(history):
                if i % 5 == 0:  # Show every 5th state to save space
                    summary += f"Step {i}: {state['state']} (Page {state['page']})\n"
            
            # Show final state
            summary += f"\nFinal Memory State: {final_state}\n"
            
            # Update the results text with this information
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, summary)
            
            print("DEBUG: Text visualization completed")
        except Exception as e:
            print(f"DEBUG: Error in text visualization: {str(e)}")
            # Last resort - just show the error
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Visualization Error: {str(e)}\n\n")
            self.results_text.insert(tk.END, "Please try a different process or algorithm.")

def main():
    try:
        root = ThemedTk(theme="equilux")
        app = VirtualMemorySimulator(root)
        
        # Handle window closing properly
        def on_closing():
            print("DEBUG: Closing application")
            plt.close('all')
            root.quit()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    except Exception as e:
        print(f"ERROR: Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
