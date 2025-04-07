import os
import sys

# Get the path of the current file
src_dir = os.path.dirname(os.path.abspath(__file__))

# Get the root directory of the project (assumes 'src' is one level deep)
project_root = os.path.dirname(os.path.dirname(src_dir))

# Add project root to Python path to allow module imports
sys.path.insert(0, project_root)

# Streamlit for UI, algorithms for simulation, and visualization utilities
import streamlit as st
from src.algorithms.page_replacement import LRUAlgorithm, OptimalAlgorithm
from src.visualization.memory_viz import create_memory_visualization, create_page_fault_graph

def parse_page_sequence(input_str: str) -> list:
    """
    Parse the input string into a list of page numbers (integers).
    Returns an empty list if the input is invalid.
    """
    try:
        return [int(x.strip()) for x in input_str.split(',')]
    except ValueError:
        st.error('Please enter valid numbers separated by commas')
        return []

def main():
    # Set Streamlit page configuration
    st.set_page_config(
        page_title="Virtual Memory Simulator",
        page_icon="🧠",
        layout="wide"
    )
    
    # Set page title
    st.title('Virtual Memory Management Visualization')
    
    # Sidebar: memory configuration section
    st.sidebar.header('Memory Configuration')
    
    # User selects number of memory frames
    total_frames = st.sidebar.slider('Total Memory Frames', 4, 20, 8)
    
    # User selects page size
    page_size = st.sidebar.slider('Page Size (KB)', 1, 16, 4)
    
    # Sidebar: page replacement configuration section
    st.sidebar.header('Page Replacement')
    
    # Text input for the page access sequence
    page_sequence = st.sidebar.text_input(
        'Enter page sequence (comma-separated)',
        '1,2,3,4,1,2,5,1,2,3,4,5'
    ).strip()
    
    # Dropdown to select page replacement algorithm
    algorithm_name = st.sidebar.selectbox(
        'Select Page Replacement Algorithm',
        ['LRU', 'Optimal']
    )
    
    # Initialize the selected algorithm class
    algorithm = LRUAlgorithm(total_frames) if algorithm_name == 'LRU' else OptimalAlgorithm(total_frames)
    
    # When user clicks "Run Simulation" button
    if st.sidebar.button('Run Simulation'):
        # Parse the user input sequence
        sequence = parse_page_sequence(page_sequence)
        
        # If input is valid, run the simulation
        if sequence:
            with st.spinner('Running simulation...'):
                # Run simulation using the selected algorithm
                page_faults, final_memory, history = algorithm.simulate(sequence)
                
                # Split layout into two columns for output
                col1, col2 = st.columns(2)
                
                # Column 1: display page faults and memory visualization
                with col1:
                    st.metric('Page Faults', page_faults)
                    st.plotly_chart(create_memory_visualization(final_memory, page_size))
                
                # Column 2: display page fault rate and graph
                with col2:
                    st.metric('Page Fault Rate', f"{(page_faults/len(sequence))*100:.2f}%")
                    st.plotly_chart(create_page_fault_graph(history))
                
                # Display the full page access sequence
                st.subheader('Page Access Sequence')
                st.write(' → '.join(map(str, sequence)))
                
                # Display detailed simulation steps
                st.subheader('Simulation History')
                for i, state in enumerate(history):
                    st.text(
                        f"Step {i+1}: Accessing Page {state['page_accessed']} "
                        f"{'(Page Fault)' if state['page_fault'] else '(Hit)'}"
                    )

# Entry point for the Streamlit app
if __name__ == '__main__':
    main()
