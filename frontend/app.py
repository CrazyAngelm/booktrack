import os
import streamlit as st
import requests
from datetime import datetime

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
PER_PAGE = int(os.getenv('PER_PAGE', 20))
REQUEST_TIMEOUT = 60  # seconds

# Use a persistent session for connection pooling
session = requests.Session()

# Initialize session state
for key, default in {
    'access_token': None,
    'refresh_token': None,
    'token_expiry': None,
    'user_email': None,
    'selected_book': None,
    'search_page': 1,
    'filter_status': 'All',
    'sort_order': 'Most downloaded'
}.items():
    st.session_state.setdefault(key, default)

# --- Utility functions ---
def clear_auth():
    for k in ['access_token', 'refresh_token', 'token_expiry', 'user_email']:
        st.session_state[k] = None

def get_headers():
    headers = {'Content-Type': 'application/json'}
    token = st.session_state.get('access_token')
    if token:
        headers['Authorization'] = f"Bearer {token}"
    return headers

def refresh_access_token():
    rt = st.session_state.get('refresh_token')
    if not rt:
        return False
    resp = session.post(
        f"{API_BASE_URL}/refresh-token",
        json={'refresh_token': rt},
        timeout=REQUEST_TIMEOUT
    )
    if resp.status_code == 200:
        data = resp.json()
        st.session_state['access_token'] = data['access_token']
        st.session_state['token_expiry'] = data.get('expires_in')
        return True
    else:
        clear_auth()
        return False

def api_request(method, path, params=None, json_data=None):
    url = f"{API_BASE_URL}{path}"
    headers = get_headers()
    try:
        resp = session.request(
            method, url,
            params=params or {},
            json=json_data or {},
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as e:
        st.error(f"Network error: {e}")
        return None

    if resp.status_code == 401:
        if refresh_access_token():
            headers = get_headers()
            resp = session.request(
                method, url,
                params=params or {},
                json=json_data or {},
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
        else:
            st.error('Session expired. Please log in again.')
            clear_auth()
            return None

    if resp.ok:
        try:
            return resp.json()
        except ValueError:
            return None
    else:
        detail = ''
        try:
            detail = resp.json().get('detail', '')
        except ValueError:
            detail = resp.text
        st.error(f"Error [{resp.status_code}]: {detail}")
        return None

# --- Caching for performance ---
@st.cache_data(ttl=300)
def fetch_books(page, query, sort_order):
    if query:
        params = {'query': query, 'page_no': page, 'page_size': PER_PAGE}
        data = api_request('GET', '/books/search', params=params) or []
    else:
        params = {'page_no': page, 'page_size': PER_PAGE}
        data = api_request('GET', '/books', params=params) or []
    if isinstance(data, list):
        reverse = sort_order == 'Most downloaded'
        return sorted(data, key=lambda x: x.get('download_count', 0), reverse=reverse)
    return []

@st.cache_data(ttl=300)
def fetch_book_details(book_id):
    return api_request('GET', f'/books/book-id/{book_id}')

@st.cache_data(ttl=300)
def fetch_favourites():
    return api_request('GET', '/favourites') or {}

@st.cache_data(ttl=300)
def fetch_reading_list():
    return api_request('GET', '/reading-list') or {}

# --- Authentication flows ---
def login(email, password):
    try:
        resp = session.post(
            f"{API_BASE_URL}/login",
            json={'email': email, 'password': password},
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as e:
        st.error(f"Network error: {e}")
        return False

    if resp.status_code == 200:
        data = resp.json()
        st.session_state.update({
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'token_expiry': data.get('expires_in'),
            'user_email': email
        })
        return True
    else:
        detail = ''
        try:
            detail = resp.json().get('detail', '')
        except ValueError:
            detail = resp.text
        st.error(f"Login failed: {detail}")
        return False

def register(name, surname, email, password):
    try:
        resp = session.post(
            f"{API_BASE_URL}/register",
            json={'name': name, 'surname': surname, 'email': email, 'password': password},
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as e:
        st.error(f"Network error: {e}")
        return False

    if resp.status_code in (200, 201):
        st.success('Registration successful! You can now log in.')
        return True
    else:
        detail = ''
        try:
            detail = resp.json().get('detail', '')
        except ValueError:
            detail = resp.text
        st.error(f"Registration failed: {detail}")
        return False

def logout():
    rt = st.session_state.get('refresh_token')
    if rt:
        try:
            session.post(
                f"{API_BASE_URL}/logout",
                json={'refresh_token': rt},
                headers=get_headers(),
                timeout=REQUEST_TIMEOUT
            )
        except requests.RequestException:
            pass
    clear_auth()

# --- UI Pages ---
def auth_page():
    st.title('📚 BookTrack')
    tabs = st.tabs(['🔑 Login', '📝 Register'])
    with tabs[0]:
        email = st.text_input('Email', key='login_email')
        pwd = st.text_input('Password', type='password', key='login_pwd')
        if st.button('Login'):
            if login(email, pwd):
                st.success('Logged in!')
    with tabs[1]:
        fn = st.text_input('First Name', key='reg_name')
        ln = st.text_input('Surname', key='reg_surname')
        email_r = st.text_input('Email', key='reg_email')
        pwd1 = st.text_input('Password', type='password', key='reg_pwd1')
        pwd2 = st.text_input('Confirm Password', type='password', key='reg_pwd2')
        if st.button('Register'):
            if pwd1 != pwd2:
                st.error('Passwords do not match')
            else:
                register(fn, ln, email_r, pwd1)

def clear_selection():
    st.session_state['selected_book'] = None

def set_selection(book_id):
    st.session_state['selected_book'] = book_id

def details_page():
    bid = st.session_state['selected_book']
    data = fetch_book_details(bid)
    if not data:
        st.error("Unable to load details.")
        st.session_state['selected_book'] = None
        return

    # — Header: Title & Back Button —
    # — Actions: Favourites & Reading List —
    title_col, fav_col, rl_col, back_col = st.columns([8, 1.5, 1.5, 1], gap="small", vertical_alignment="bottom")
    with title_col:
        st.title(data.get('title', ''))
    with back_col:
        if st.button("← Back", key=f"back_{bid}", on_click=clear_selection):
            return

    st.markdown("---")

    # Favourite toggle
    fav_ids = [f['book_id'] for f in fetch_favourites().get('favourites', [])]
    is_fav = bid in fav_ids
    with fav_col:
        if st.button(
            "💔 Remove Favourite" if is_fav else "❤️ Add Favourite",
            use_container_width=True
        ):
            api_request(
                'PUT', f"/favourites/book-id/{bid}",
                params={'is_favourite': not is_fav}
            )
            fetch_favourites.clear()
            return

    # Reading-status selectbox with immediate update
    def _on_status_change():
        new_status = st.session_state[f"reading_status_{bid}"]
        # fetch existing entry (ignore 404)
        entry = None
        resp = session.get(
            f"{API_BASE_URL}/reading-list/book-id/{bid}",
            headers=get_headers(), timeout=REQUEST_TIMEOUT
        )
        if resp.status_code == 200:
            entry = resp.json()
        # apply change
        if new_status == 'None':
            if entry:
                session.delete(
                    f"{API_BASE_URL}/reading-list/book-id/{bid}",
                    headers=get_headers(), timeout=REQUEST_TIMEOUT
                )
        else:
            if entry:
                api_request(
                    'PUT', f"/reading-list/book-id/{bid}",
                    params={'status': new_status}
                )
            else:
                api_request(
                    'POST', "/reading-list",
                    params={'book_id': bid, 'status': new_status}
                )
        fetch_reading_list.clear()

    # determine current status
    entry = None
    resp = session.get(
        f"{API_BASE_URL}/reading-list/book-id/{bid}",
        headers=get_headers(), timeout=REQUEST_TIMEOUT
    )
    if resp.status_code == 200:
        entry = resp.json()
    current = entry.get('status') if entry else 'None'
    options = ['None', 'Want', 'Reading', 'Read']

    with rl_col:
        st.selectbox(
            "Reading Status",
            options,
            index=options.index(current),
            key=f"reading_status_{bid}",
            on_change=_on_status_change,
            help="Select to add/update/remove from your reading list",
            
            
        )

    # — Book Metadata —
    img_col, info_col = st.columns([1, 2], gap="medium")
    cover = data.get('formats', {}).get('image/jpeg')
    if cover:
        img_col.image(cover, width=220)
    with info_col:
        st.subheader("Authors")
        for a in data.get('authors', []):
            yrs = f"{a.get('birth_year','')}–{a.get('death_year','')}"
            st.write(f"{a.get('name','')} ({yrs})")

        st.subheader("Summary")
        summary = (data.get('summaries') or ["No summary available"])[0]
        st.write(summary)

        st.subheader("Download Count")
        st.write(data.get('download_count', 0))

        st.subheader("Subjects")
        st.write(", ".join(data.get('subjects', [])))

        st.subheader("Languages / Media")
        langs = ", ".join(data.get('languages', []))
        media = data.get('media_type', '')
        st.write(f"{langs}  |  {media}")

    st.markdown("---")

 


def search_page():
    st.header('🔍 Discover')
    s1, s2, _, s3 = st.columns([4, 2, 4, 2], vertical_alignment='bottom')
    query = s1.text_input('Search by title or author', key='search_query')
    if s2.button('Search'):
        st.session_state['search_page'] = 1
    sort = s3.selectbox('Sort', ['Most downloaded', 'Least downloaded'], key='sort_order')
    books = fetch_books(st.session_state['search_page'], query, sort)
    st.markdown('---')
    for b in books:
        img = b.get('formats', {}).get('image/jpeg')
        title = b.get('title', 'No title')
        auths = ', '.join([a.get('name') for a in b.get('authors', [])])
        # safe summary
        summaries = b.get('summaries') or ['']
        desc = summaries[0]
        desc = desc[:200] + '...' if len(desc) > 200 else desc
        dl = b.get('download_count', 0)
        langs = ', '.join(b.get('languages', []))
        cols = st.columns([1, 4, 2], vertical_alignment='center')
        if img:
            cols[0].image(img, width=100)
        cols[1].markdown(f"**{title}** by {auths}")
        cols[1].write(desc)
        cols[1].write(f"Downloads: {dl} | Languages: {langs}")
        if cols[2].button('Details', key=f"d{b.get('id')}", on_click=set_selection, args=(b.get('id'),)):
            return
    def _prev():
        if st.session_state['search_page'] > 1:
            st.session_state['search_page'] -= 1

    def _next():
        st.session_state['search_page'] += 1

    p1, p2, p3 = st.columns([1,1,1])
    p1.button('← Previous', key='search_prev', on_click=_prev)
    p2.markdown(f"Page {st.session_state['search_page']}", unsafe_allow_html=True)
    # only show “Next” when we got a full page of results

    p3.button('Next →', key='search_next', on_click=_next)

def favourites_page():
    st.header('❤️ Favourites')
    st.markdown('---')
    favs = fetch_favourites().get('favourites', [])
    for f in favs:
        bid = f['book_id']
        b = fetch_book_details(bid)
        if not b:
            continue
        img = b.get('formats', {}).get('image/jpeg')
        title = b.get('title', 'No title')
        auths = ', '.join([a.get('name') for a in b.get('authors', [])])
        summaries = b.get('summaries') or ['']
        desc = summaries[0]
        desc = desc[:150] + '...' if len(desc) > 150 else desc
        dl = b.get('download_count', 0)
        langs = ', '.join(b.get('languages', []))
        cols = st.columns([1, 4, 1])
        if img:
            cols[0].image(img, width=100)
        cols[1].markdown(f"**{title}** by {auths}")
        cols[1].write(desc)
        cols[1].write(f"Downloads: {dl} | Languages: {langs}")
        if cols[2].button('Remove', key=f"rm{bid}"):
            api_request('PUT', f'/favourites/book-id/{bid}', params={'is_favourite': False})
            fetch_favourites.clear()
            return

def reading_list_page():

    s1, s2 = st.columns([8, 2], vertical_alignment='center')
    s1.header('📖 Reading List')
    status = s2.selectbox('Filter', ['All', 'Want', 'Reading', 'Read'], key='filter_status')
    st.markdown('---')
    rl = fetch_reading_list().get('reading_list', [])
    for r in rl:
        if status != 'All' and r['status'] != status:
            continue
        bid = r['book_id']
        b = fetch_book_details(bid)
        if not b:
            continue
        img = b.get('formats', {}).get('image/jpeg')
        title = b.get('title', 'No title')
        summaries = b.get('summaries') or ['']
        desc = summaries[0]
        desc = desc[:150] + '...' if len(desc) > 150 else desc
        dl = b.get('download_count', 0)
        cols = st.columns([1, 4, 1])
        if img:
            cols[0].image(img, width=100)
        cols[1].markdown(f"**{title}** — {r['status']}")
        cols[1].write(desc)
        cols[1].write(f"Downloads: {dl}")
        if cols[2].button('Details', key=f"rl{bid}", on_click=set_selection, args=(bid,)):
            return

def dashboard_page():
    st.header('📊 Dashboard')
    rl = fetch_reading_list().get('reading_list', [])
    reading = sum(1 for r in rl if r['status'] == 'Reading')
    completed = sum(1 for r in rl if r['status'] == 'Read')
    favs = fetch_favourites().get('favourites', [])
    recent = 'None'
    if favs:
        bid = favs[-1]['book_id']
        b = fetch_book_details(bid)
        recent = b.get('title') if b else 'Unknown'
    c1, c2, c3 = st.columns(3)
    c1.metric('Reading', reading)
    c2.metric('Completed', completed)
    c3.metric('Recent Favourite', recent)

# --- Main Setup ---
st.set_page_config(page_title='BookTrack', layout='wide')

# Authentication
if not st.session_state['access_token']:
    auth_page()
    st.stop()

# Sidebar: user & logout
st.sidebar.markdown(f"**User:** {st.session_state['user_email']}")
if st.sidebar.button('Logout'):
    logout()
    st.experimental_rerun()

# Details view
if st.session_state['selected_book'] is not None:
    details_page()
    st.stop()

# Main tabs
tabs = st.tabs(['Search', 'Favourites', 'Reading List', 'Dashboard'])
with tabs[0]:
    search_page()
with tabs[1]:
    favourites_page()
with tabs[2]:
    reading_list_page()
with tabs[3]:
    dashboard_page()
