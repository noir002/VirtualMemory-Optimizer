import streamlit as st
import numpy as np
import plotly.graph_objects as go
from collections import OrderedDict
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add error handling decorator
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f'Error in {func.__name__}: {str(e)}')
            st.error(f'An error occurred: {str(e)}')
    return wrapper

class MemoryManager:
    def __init__(self, total_frames, page_size):
        self.total_frames = total_frames
        self.page_size = page_size
        self.memory = [-1] * total_frames  # -1 represents empty frame
        self.page_table = {}
        self.page_faults = 0
        self.access_time = []
        
    def lru_replace(self, page_sequence):
        page_faults = 0
        memory = []
        access_history = OrderedDict()
        
        for page in page_sequence:
            if page not in memory:
                page_faults += 1
                if len(memory) >= self.total_frames:
                    # Find least recently used page
                    lru_page = next(iter(access_history))
                    memory.remove(lru_page)
                    del access_history[lru_page]
                memory.append(page)
            
            # Update access history
            if page in access_history:
                del access_history[page]
            access_history[page] = True
            
        return page_faults, memory

    def optimal_replace(self, page_sequence):
        page_faults = 0
        memory = []
        
        for i, page in enumerate(page_sequence):
            if page not in memory:
                page_faults += 1
                if len(memory) >= self.total_frames:
                    # Find page that won't be used for the longest time
                    future_usage = {}
                    for p in memory:
                        try:
                            future_usage[p] = page_sequence[i:].index(p)
                        except ValueError:
                            future_usage[p] = float('inf')
                    victim = max(future_usage.items(), key=lambda x: x[1])[0]
                    memory.remove(victim)
                memory.append(page)
                
        return page_faults, memory

@handle_errors
def create_memory_visualization(memory_state, page_size):
    fig = go.Figure()
    
    y_positions = np.arange(len(memory_state))
    colors = ['#2ecc71' if x != -1 else '#e74c3c' for x in memory_state]
    
    fig.add_trace(go.Bar(
        x=[1] * len(memory_state),
        y=y_positions,
        orientation='h',
        marker_color=colors,
        text=[f'Page {x}' if x != -1 else 'Empty' for x in memory_state],
        textposition='inside',
        width=0.8
    ))
    
    fig.update_layout(
        title='Memory State Visualization',
        xaxis_title='Memory Pages',
        yaxis_title='Frame Number',
        showlegend=False,
        height=400,
        width=600,
        yaxis={'autorange': 'reversed'}
    )
    
    return fig

@handle_errors
def main():
    print('Starting main function')
    st.write('Debug: Starting application')
    st.title('Virtual Memory Management Visualization')
    print('Title set')
    
    st.sidebar.header('Memory Configuration')
    total_frames = st.sidebar.slider('Total Memory Frames', 4, 20, 8)
    page_size = st.sidebar.slider('Page Size (KB)', 1, 16, 4)
    
    memory_manager = MemoryManager(total_frames, page_size)
    
    st.sidebar.header('Page Replacement')
    page_sequence = st.sidebar.text_input(
        'Enter page sequence (comma-separated)',
        '1,2,3,4,1,2,5,1,2,3,4,5'
    ).strip()
    
    try:
        page_sequence = [int(x.strip()) for x in page_sequence.split(',')]
    except ValueError:
        st.error('Please enter valid numbers separated by commas')
        return
    
    algorithm = st.sidebar.selectbox(
        'Select Page Replacement Algorithm',
        ['LRU', 'Optimal']
    )
    
    if st.sidebar.button('Run Simulation'):
        with st.spinner('Running simulation...'):
            if algorithm == 'LRU':
                page_faults, final_memory = memory_manager.lru_replace(page_sequence)
            else:
                page_faults, final_memory = memory_manager.optimal_replace(page_sequence)
            
            # Update memory state for visualization
            memory_manager.memory = [-1] * total_frames
            for i, page in enumerate(final_memory):
                if i < total_frames:
                    memory_manager.memory[i] = page
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.metric('Page Faults', page_faults)
            with col2:
                st.metric('Page Fault Rate', f"{(page_faults/len(page_sequence))*100:.2f}%")
            
            # Display memory visualization
            st.plotly_chart(create_memory_visualization(memory_manager.memory, page_size))
            
            # Display page access sequence
            st.subheader('Page Access Sequence')
            st.write(' → '.join(map(str, page_sequence)))

if __name__ == '__main__':
    main()
