import streamlit as st

def clear_details():
    """Reset selection to go back to the list view."""
    st.session_state['selected_book'] = None

def set_selected_book(book_id: int):
    """Select a book and trigger the Details page."""
    st.session_state['selected_book'] = book_id
