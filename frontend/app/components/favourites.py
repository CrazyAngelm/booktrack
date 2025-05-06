# app/pages/favourites.py
import streamlit as st
from api_client import api_get, api_delete


def favourites_page():
    st.header('My Favourites')
    favs = api_get('/favourites/')
    if not favs:
        st.info("You haven't added any favourites yet.")
        return

    for book in favs:
        cols = st.columns([1, 4, 1], gap='medium', vertical_alignment='center')
        cols[0].image(book['cover_url'], width=140)
        cols[1].markdown(
            f"**{book['title']}**  by {', '.join(book['authors'])}"
        )
        cols[1].markdown(f"Popularity: {book.get('popularity', 'N/A')}")
        cols[1].markdown(f"Excerpt: {book.get('excerpt', '')}")
        if cols[2].button('Remove', key=f'remove_{book["id"]}'):
            api_delete(f'/favourites/{book["id"]}')
            st.experimental_rerun()
