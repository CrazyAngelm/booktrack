# app/pages/reading_list.py
import streamlit as st
from app.api_client import api_get
from app.state import set_selected_book


def reading_list_page():
    st.header('My Reading List')
    status_filter = st.selectbox(
        'Filter',
        ['All', 'Want', 'Reading', 'Read'],
        key='filter_status'
    )
    rl = api_get('/reading-list/')

    if not rl:
        st.info("Your reading list is empty.")
        return

    for book in rl:
        if status_filter != 'All' and book['status'] != status_filter:
            continue
        cols = st.columns([1, 4, 1], gap='medium', vertical_alignment='center')
        cols[0].image(book['cover_url'], width=140)
        cols[1].markdown(f"**{book['title']}** — Status: {book['status']}")
        cols[1].markdown(f"by {', '.join(book['authors'])}")
        cols[1].markdown(f"Popularity: {book.get('popularity', 'N/A')}")
        cols[1].markdown(f"Excerpt: {book.get('excerpt', '')}")
        if cols[2].button(
            'Details',
            key=f'reading_{book["id"]}',
            on_click=set_selected_book,
            args=(book['id'],)
        ):
            st.experimental_rerun()
