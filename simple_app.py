import streamlit as st

def main():
    st.title('Simple Test App')
    st.write('Testing if Streamlit works')
    
    if st.button('Click me'):
        st.write('Button clicked!')

if __name__ == '__main__':
    main()
