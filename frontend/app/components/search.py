import streamlit as st
from app.api_client import api_get
from app.components.book_card import render_book_card
from app.state import set_selected_book


def search_page():
    st.header('Discover Books')
    col1, col2 = st.columns([2, 1], gap='small', vertical_alignment='bottom')
    query = col1.text_input('Search by title or author', key='search_query')
    if col2.button('Search', key='search_button'):
        st.session_state['search_page'] = 1

    page = st.session_state.get('search_page', 1)
    data = api_get('/books/', {'search': query, 'page': page})

    st.markdown('---')
    for book in data.get('results', []):
        render_book_card(book, on_click=set_selected_book)

    st.markdown('---')
    prev, info, nxt = st.columns(3, vertical_alignment='center')
    if prev.button('Previous', key='prev_page') and page > 1:
        st.session_state['search_page'] = page - 1
        st.experimental_rerun()
    info.markdown(
        f"""<h5 style='text-align:center;'>Page {
            page
            } of {data.get('total_pages', 1)}</h5>""",
        unsafe_allow_html=True
    )
    if nxt.button(
        'Next', key='next_page'
    ) and page < data.get('total_pages', 1):
        st.session_state['search_page'] = page + 1
        st.experimental_rerun()
