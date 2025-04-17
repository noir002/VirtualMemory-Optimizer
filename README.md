# Virtual Memory Simulator

A simulation tool for visualizing and comparing different page replacement algorithms used in virtual memory management.

## Overview

This project provides:
1. A visual simulation of page replacement algorithms (LRU and Optimal)
2. The ability to select real running processes and generate page access sequences based on their memory usage
3. Visualization of memory state transitions and page fault statistics

## Prerequisites

- Python 3.6+
- Required packages listed in `requirements.txt`

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/VirtualMemoryOptimization.git
cd VirtualMemoryOptimization
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Running the Application

### Option 1: Main Application (with Matplotlib visualization)

```
python app.py
```

This version includes interactive graphs and visualizations using Matplotlib.

### Option 2: Simple Application (without Matplotlib)

If you encounter issues with Matplotlib or prefer a simpler interface:

```
python simple_app.py
```

The simple version provides all the same features but uses a text-based output instead of matplotlib graphs.

## Features

- **Process Selection**: Choose from currently running processes on your system
- **Memory Frame Configuration**: Set the number of frames for simulation
- **Algorithm Selection**: Choose between LRU (Least Recently Used) and Optimal page replacement algorithms
- **Custom Page Sequences**: Manually enter page sequences or generate based on real process memory usage
- **Memory State Visualization**: See how memory frames change with each page access
- **Statistics**: Compare page fault rates and efficiency between algorithms

## Usage Tips

1. Use the "Refresh" button to update the list of running processes
2. Select a process from the dropdown menu to generate a page sequence based on its memory usage
3. Adjust the number of memory frames as needed
4. Choose an algorithm (LRU or Optimal)
5. Click "Run Simulation" to see the results
6. Optionally, enter your own page sequence (comma-separated numbers) in the input field

## Troubleshooting

If you encounter issues with the matplotlib version:
- Try running the simple version (`simple_app.py`)
- Check that all dependencies are installed correctly
- Ensure you have appropriate permissions to monitor system processes

## License

This project is licensed under the MIT License - see the LICENSE file for details.
