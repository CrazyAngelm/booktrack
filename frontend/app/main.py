import streamlit as st
from components.search import search_page
from components.details import details_page
from components.favourites import favourites_page
from components.reading_list import reading_list_page
from components.dashboard import dashboard_page

st.set_page_config(page_title='BookTrack', layout='wide')
st.session_state.setdefault('selected_book', None)

if st.session_state['selected_book'] is not None:
    details_page()
    st.stop()

tabs = st.tabs(['Search', 'Favourites', 'Reading List', 'Dashboard'])
with tabs[0]:
    search_page()
with tabs[1]:
    favourites_page()
with tabs[2]:
    reading_list_page()
with tabs[3]:
    dashboard_page()
