# app/pages/dashboard.py
import streamlit as st
from api_client import api_get


def dashboard_page():
    st.header('Dashboard')
    rl = api_get('/reading-list/')
    reading = sum(1 for r in rl if r['status'] == 'Reading')
    completed = sum(1 for r in rl if r['status'] == 'Read')
    favs = api_get('/favourites/')
    recent = favs[-1]['title'] if favs else 'None'

    c1, c2, c3 = st.columns(3)
    c1.metric('Currently Reading', reading)
    c2.metric('Completed', completed)
    c3.metric('Recent Favourite', recent)
