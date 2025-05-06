import streamlit as st
from app.state import set_selected_book, clear_details

def test_set_and_clear_state(tmp_path, monkeypatch):
    # ensure clean session state
    st.session_state.clear()

    set_selected_book(99)
    assert st.session_state['selected_book'] == 99

    clear_details()
    assert 'selected_book' not in st.session_state or st.session_state.get('selected_book') is None
