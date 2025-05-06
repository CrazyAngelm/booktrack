import os
import random
import streamlit as st
import requests

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api/v1')
BYPASS_AUTH = os.getenv('BYPASS_AUTH', 'false').lower() == 'true'
USE_FAKE_DATA = os.getenv('USE_FAKE_DATA', 'false').lower() == 'true'
PER_PAGE = 20

# Demo cover images
COVER_URLS = [
    'https://covers.openlibrary.org/b/id/8231856-L.jpg',
    'https://covers.openlibrary.org/b/id/8319256-L.jpg',
    'https://covers.openlibrary.org/b/id/8074151-L.jpg',
    'https://covers.openlibrary.org/b/id/8522721-L.jpg',
    'https://covers.openlibrary.org/b/id/8091016-L.jpg',
    'https://covers.openlibrary.org/b/id/8281994-L.jpg',
    'https://covers.openlibrary.org/b/id/10279816-L.jpg',
    'https://covers.openlibrary.org/b/id/10013571-L.jpg',
    'https://covers.openlibrary.org/b/id/8314150-L.jpg',
    'https://covers.openlibrary.org/b/id/8773951-L.jpg'
]

# Fake data setup
if USE_FAKE_DATA:
    FAKE_BOOKS = []
    for i in range(1, 51):
        FAKE_BOOKS.append({
            'id': i,
            'title': f'Sample Book {i}',
            'authors': [f'Author {i}'],
            'excerpt': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'cover_url': COVER_URLS[(i-1) % len(COVER_URLS)],
            'popularity': random.randint(1, 100)
        })
    FAKE_BOOKS.sort(key=lambda b: b['popularity'], reverse=True)
    FAKE_DETAILS = {
        b['id']: {
            'id': b['id'],
            'title': b['title'],
            'authors': b['authors'],
            'cover_url': b['cover_url'],
            'description': f'Full description for {b["title"]}. Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'rating': round(random.uniform(1, 5), 1)
        }
        for b in FAKE_BOOKS
    }
    FAKE_FAV = [FAKE_BOOKS[i] for i in random.sample(range(len(FAKE_BOOKS)), 10)]
    FAKE_RL = [
        {**FAKE_BOOKS[1], 'status': 'Reading'},
        {**FAKE_BOOKS[3], 'status': 'Want'},
        {**FAKE_BOOKS[4], 'status': 'Read'}
    ]

# Initialize session state defaults
st.session_state.setdefault('token', 'demo')
st.session_state.setdefault('search_page', 1)
st.session_state.setdefault('selected_book', None)

# API helper functions
def api_get(path, params=None):
    if USE_FAKE_DATA:
        # List
        if path == '/books/' and params is not None:
            page = params.get('page', 1)
            start = (page - 1) * PER_PAGE
            end = start + PER_PAGE
            return {
                'results': FAKE_BOOKS[start:end],
                'total_pages': (len(FAKE_BOOKS) + PER_PAGE - 1) // PER_PAGE
            }
        # Details
        if path.startswith('/books/'):
            bid = int(path.rsplit('/', 1)[1])
            return FAKE_DETAILS.get(bid)
        if path == '/favourites/':
            return FAKE_FAV
        if path == '/reading-list/':
            return FAKE_RL
    resp = requests.get(f"{API_BASE_URL}{path}", params=params or {}, headers={})
    return resp.json() if resp.ok else {}

def api_post(path, json=None):
    if USE_FAKE_DATA and path == '/favourites/':
        FAKE_FAV.append(FAKE_DETAILS.get(json['book_id']))
        return True
    resp = requests.post(f"{API_BASE_URL}{path}", json=json or {}, headers={})
    return resp.ok

def api_put(path, json=None):
    if USE_FAKE_DATA and path.startswith('/reading-list/'):
        bid = int(path.rsplit('/', 1)[1])
        for r in FAKE_RL:
            if r['id'] == bid:
                r['status'] = json['status']
                return True
        FAKE_RL.append({**FAKE_DETAILS[bid], 'status': json['status']})
        return True
    resp = requests.put(f"{API_BASE_URL}{path}", json=json or {}, headers={})
    return resp.ok

def api_delete(path):
    if USE_FAKE_DATA:
        bid = int(path.rsplit('/', 1)[1])
        if path.startswith('/favourites/'):
            FAKE_FAV[:] = [f for f in FAKE_FAV if f['id'] != bid]
        if path.startswith('/reading-list/'):
            FAKE_RL[:] = [r for r in FAKE_RL if r['id'] != bid]
        return True
    resp = requests.delete(f"{API_BASE_URL}{path}", headers={})
    return resp.ok

# State management callbacks
def clear_details():
    st.session_state['selected_book'] = None

def set_selected_book(book_id):
    st.session_state['selected_book'] = book_id

# Page: Details view
def details_page():
    bid = st.session_state['selected_book']
    book = api_get(f'/books/{bid}')
    if not book:
        st.error('Unable to load book details.')
        clear_details()
        return

    if st.button('← Back to List', key=f'back_btn_top_{bid}', on_click=clear_details):
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
            return

        # Reading status
        rl = api_get('/reading-list/')
        current = next((r['status'] for r in rl if r['id'] == bid), None)
        options = ['None', 'Want', 'Reading', 'Read']
        selection = st.selectbox('Reading Status', options, index=options.index(current) if current in options else 0)
        if st.button('Update Status', key=f'upd_btn_{bid}'):
            if selection != 'None':
                api_put(f'/reading-list/{bid}', {'status': selection})
            else:
                api_delete(f'/reading-list/{bid}')
            return

    st.write('---')
    if st.button('← Back to List', key=f'back_btn_bottom_{bid}', on_click=clear_details):
        return

# Page: Search & Discover

def search_page():
    st.header('Discover Books')
    col1, col2 = st.columns([2, 1], gap='small', vertical_alignment='bottom')
    query = col1.text_input('Search by title or author')
    if col2.button('Search', key='search_button'):
        st.session_state['search_page'] = 1

    page = st.session_state['search_page']
    data = api_get('/books/', {'search': query, 'page': page})

    ## empty space
    st.markdown('---')
    for b in data.get('results', []):
        img_col, txt_col, act_col = st.columns([1, 4, 1], gap='medium', vertical_alignment='center')
        img_col.image(b['cover_url'], width=140)
        txt_col.markdown(f"**{b['title']}**  by {', '.join(b['authors'])}")
        txt_col.markdown(f"Popularity: {b['popularity']}")
        txt_col.markdown(f"Excerpt: {b['excerpt']}")
        if act_col.button('Details', key=f'detail_{b['id']}', on_click=set_selected_book, args=(b['id'],)):
            return

    st.markdown('---')
    p1, p2, p3 = st.columns([1, 1, 1], vertical_alignment='center' )
    if p1.button('Previous', key='prev_page', use_container_width=True) and page > 1:
        st.session_state['search_page'] = page - 1
    p2.markdown(f"<h5 style='text-align: center;'>Page {page} of {data.get('total_pages', 1)}</h5>", unsafe_allow_html=True)
    if p3.button('Next', key='next_page', use_container_width=True) and page < data.get('total_pages', 1):
        st.session_state['search_page'] = page + 1

# Page: Favourites

def favourites_page():
    st.header('My Favourites')
    for f in api_get('/favourites/'):
        img_col, txt_col, rm_col = st.columns([1, 4, 1], gap='medium', vertical_alignment='center')
        img_col.image(f['cover_url'], width=140)
        txt_col.markdown(f"**{f['title']}**  by {', '.join(f['authors'])}")
        txt_col.markdown(f"Popularity: {f['popularity']}")
        txt_col.markdown(f"Excerpt: {f['excerpt']}")
        if rm_col.button('Remove', key=f'remove_{f['id']}'):
            api_delete(f'/favourites/{f['id']}')
            return

# Page: Reading List

def reading_list_page():
    c1, c2, c3 = st.columns([8, 1, 1], gap='small', vertical_alignment='bottom')
    c1.header('My Reading List')
    status_filter = c2.selectbox('Filter', ['All', 'Want', 'Reading', 'Read'], key='filter_status')
    for r in api_get('/reading-list/'):
        if status_filter != 'All' and r['status'] != status_filter:
            continue
        img_col, txt_col, act_col = st.columns([1, 4, 1], gap='medium', vertical_alignment='center')
        img_col.image(r['cover_url'], width=140)
        txt_col.markdown(f"**{r['title']}** \u2014 Status: {r['status']}")
        txt_col.markdown(f"by {', '.join(r['authors'])}")
        txt_col.markdown(f"Popularity: {r['popularity']}")
        txt_col.markdown(f"Excerpt: {r['excerpt']}")
        if act_col.button('Details', key=f'reading_{r['id']}', on_click=set_selected_book, args=(r['id'],)):
            return

# Page: Dashboard

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

# Main

st.set_page_config(page_title='BookTrack', layout='wide')

# Show details if a book is selected
if st.session_state['selected_book'] is not None:
    details_page()
    st.stop()

# Otherwise show tabs
tabs = st.tabs(['Search', 'Favourites', 'Reading List', 'Dashboard'])
with tabs[0]:
    search_page()
with tabs[1]:
    favourites_page()
with tabs[2]:
    reading_list_page()
with tabs[3]:
    dashboard_page()
