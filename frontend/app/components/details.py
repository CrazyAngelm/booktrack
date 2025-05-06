# app/pages/details.py
import streamlit as st
from app.api_client import api_get, api_post, api_put, api_delete
from app.state import clear_details


def details_page():
    bid = st.session_state['selected_book']
    book = api_get(f'/books/{bid}')
    if not book:
        st.error('Unable to load book details.')
        clear_details()
        return

    if st.button(
        '← Back to List',
        key=f'back_btn_top_{bid}',
        on_click=clear_details
    ):
        return

    st.write('---')
    col1, col2 = st.columns([1, 2], gap='medium')
    with col1:
        st.image(book['cover_url'], width=240)
    with col2:
        st.header(book['title'])
        st.subheader('Authors')
        st.write(', '.join(book['authors']))
        st.subheader('Rating')
        st.write(f"{book.get('rating', 'N/A')} ⭐️")
        st.subheader('Description')
        st.write(book.get('description', 'No description available.'))

        # Favourites toggle
        favs = api_get('/favourites/')
        is_fav = any(f['id'] == bid for f in favs)
        label = 'Remove from Favourites' if is_fav else 'Add to Favourites'
        if st.button(label, key=f'fav_btn_{bid}'):
            if is_fav:
                api_delete(f'/favourites/{bid}')
            else:
                api_post('/favourites/', {'book_id': bid})
            st.experimental_rerun()

        # Reading status
        rl = api_get('/reading-list/')
        current = next((r['status'] for r in rl if r['id'] == bid), None)
        options = ['None', 'Want', 'Reading', 'Read']
        idx = options.index(current) if current in options else 0
        selection = st.selectbox('Reading Status', options, index=idx)
        if st.button('Update Status', key=f'upd_btn_{bid}'):
            if selection != 'None':
                api_put(f'/reading-list/{bid}', {'status': selection})
            else:
                api_delete(f'/reading-list/{bid}')
            st.experimental_rerun()

    st.write('---')
    if st.button(
        '← Back to List',
        key=f'back_btn_bottom_{bid}',
        on_click=clear_details
    ):
        return
