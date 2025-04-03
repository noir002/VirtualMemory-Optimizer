import streamlit as st  # Import Streamlit library for building the web app

# Define the main function to run the Streamlit app
def main():
    st.title('Simple Test App')  # Set the title of the Streamlit app
    st.write('Testing if Streamlit works')  # Display a message on the page
    
    # Create a button that, when clicked, displays a message
    if st.button('Click me'):
        st.write('Button clicked!')  # Display this message when the button is clicked

# Run the main function when the script is executedd
if __name__ == '__main__':
    main()
