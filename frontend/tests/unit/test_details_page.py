import streamlit as real_st
import os
import sys
import app.components.details as mod
import pytest
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '../..'
            )
        )
    )


class Col:
    def __init__(self):
        self.image_calls = []
        self.header_calls = []
        self.subheader_calls = []
        self.write_calls = []
        self.button_calls = {}
        self.selectbox_calls = {}

    def __enter__(self):
        # When entering the with-block, this becomes the active column.
        self._parent.active = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._parent.active = None
        return False

    def image(self, url, width=None):
        self.image_calls.append((url, width))

    def header(self, txt):
        self.header_calls.append(txt)

    def subheader(self, txt):
        self.subheader_calls.append(txt)

    def write(self, txt):
        self.write_calls.append(txt)

    def button(self, label, key=None, on_click=None):
        return self.button_calls.get(key, False)

    def selectbox(self, label, options, index=0):
        return self.selectbox_calls.get('selection', options[index])


class STStub:
    """
    Stub of streamlit that routes calls like
    image/header/write/button/selectbox
    to the currently active Col instance, and routes pre-context buttons
    (like Back-to-List) to the second column of the next columns() pair.
    """
    def __init__(self, cols_sequence):
        self.session_state = real_st.session_state
        self._cols_seq = cols_sequence[:]  # copy
        self.active = None
        self.last_error = None
        self.did_rerun = False

    def error(self, msg):
        self.last_error = msg

    def write(self, txt):
        # top-level write or inside col
        if self.active:
            return self.active.write(txt)
        self.last_write = txt

    def columns(self, *args, **kwargs):
        col1, col2 = self._cols_seq.pop(0)
        col1._parent = self
        col2._parent = self
        return (col1, col2)

    def button(self, label, key=None, on_click=None):
        # If inside a with-block, dispatch there:
        if self.active:
            return self.active.button(label, key=key, on_click=on_click)
        # Otherwise, route to the second col of the upcoming columns() call:
        if self._cols_seq:
            _, upcoming_second = self._cols_seq[0]
            return upcoming_second.button(label, key=key, on_click=on_click)
        return False

    def selectbox(self, label, options, index=0):
        return self.active.selectbox(label, options, index=index)

    def image(self, url, width=None):
        return self.active.image(url, width)

    def header(self, txt):
        return self.active.header(txt)

    def subheader(self, txt):
        return self.active.subheader(txt)

    def experimental_rerun(self):
        self.did_rerun = True


@pytest.fixture(autouse=True)
def clear_session_state():
    real_st.session_state.clear()
    yield
    real_st.session_state.clear()


def test_book_not_found(monkeypatch):
    real_st.session_state['selected_book'] = 42
    monkeypatch.setattr(mod, 'api_get', lambda path: None)
    cleared = {'called': False}
    monkeypatch.setattr(
        mod, 'clear_details',
        lambda: cleared.__setitem__('called', True)
    )

    stub = STStub([])
    monkeypatch.setattr(mod, 'st', stub)

    mod.details_page()

    assert stub.last_error == 'Unable to load book details.'
    assert cleared['called']


def test_back_button_top_early_exit(monkeypatch):
    book = {
        'id': 1,
        'title': 'T',
        'authors': ['A'],
        'cover_url': 'u',
        'rating': 5,
        'description': 'D'
    }
    real_st.session_state['selected_book'] = 1
    monkeypatch.setattr(mod, 'api_get', lambda path: book)
    monkeypatch.setattr(mod, 'clear_details', lambda: None)

    col1, col2 = Col(), Col()
    col2.button_calls['back_btn_top_1'] = True

    stub = STStub([(col1, col2)])
    monkeypatch.setattr(mod, 'st', stub)

    mod.details_page()

    # Never entered the with-block, so no image call
    assert col1.image_calls == []


def test_add_to_favourites(monkeypatch):
    bid = 7
    real_st.session_state['selected_book'] = bid
    book = {
        'id': bid,
        'title': 'T',
        'authors': ['A'],
        'cover_url': 'u'
    }

    seq = [book, [], []]
    monkeypatch.setattr(mod, 'api_get', lambda path: seq.pop(0))

    calls = {}
    monkeypatch.setattr(
        mod,
        'api_post',
        lambda path,
        json: calls.setdefault('post', (path, json))
    )
    monkeypatch.setattr(
        mod,
        'api_delete',
        lambda path: calls.setdefault('delete', path)
    )
    monkeypatch.setattr(mod, 'clear_details', lambda: None)

    col1, col2 = Col(), Col()
    col2.button_calls[f'fav_btn_{bid}'] = True
    col2.button_calls[f'upd_btn_{bid}'] = False
    col2.selectbox_calls['selection'] = 'None'

    stub = STStub([(col1, col2)])
    monkeypatch.setattr(mod, 'st', stub)

    mod.details_page()

    assert calls['post'] == ('/favourites/', {'book_id': bid})


def test_update_status_and_remove(monkeypatch):
    bid = 3
    real_st.session_state['selected_book'] = bid
    book = {
        'id': bid,
        'title': 'T',
        'authors': ['A'],
        'cover_url': 'u'
    }

    seq = [book, [], [{
        'id': bid,
        'status': 'Read'
        }]]
    monkeypatch.setattr(mod, 'api_get', lambda path: seq.pop(0))

    ops = {}
    monkeypatch.setattr(
        mod,
        'api_put',
        lambda path,
        json: ops.setdefault('put', (path, json))
    )
    monkeypatch.setattr(mod,
                        'api_delete',
                        lambda path: ops.setdefault('delete', path)
                        )
    monkeypatch.setattr(mod, 'api_post', lambda *a, **k: None)
    monkeypatch.setattr(mod, 'clear_details', lambda: None)

    col1, col2 = Col(), Col()
    col2.button_calls[f'back_btn_top_{bid}'] = False
    col2.button_calls[f'fav_btn_{bid}'] = False
    col2.button_calls[f'upd_btn_{bid}'] = True
    col2.selectbox_calls['selection'] = 'None'

    stub = STStub([(col1, col2)])
    monkeypatch.setattr(mod, 'st', stub)

    mod.details_page()

    assert ops['delete'] == f'/reading-list/{bid}'
