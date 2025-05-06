import streamlit as real_st
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import app.components.search as mod
from app.api_client import api_get
import types
import pytest

class ColStub:
    def __init__(self, text_input_ret="", button_ret=False):
        self.text_input_ret = text_input_ret
        self.button_ret = button_ret
        self.markdown_calls = []

    def text_input(self, label, key=None):
        return self.text_input_ret

    def button(self, label, key=None):
        return self.button_ret

    def markdown(self, txt, unsafe_allow_html=False):
        self.markdown_calls.append((txt, unsafe_allow_html))


@pytest.fixture(autouse=True)
def clear_session_state():
    real_st.session_state.clear()
    yield
    real_st.session_state.clear()


def make_stub_st(cols_sequence):
    """
    Returns a stub of the 'st' namespace with:
     - session_state linked to real_st.session_state
     - header, markdown, experimental_rerun as no-ops
     - columns() popping from cols_sequence
    """
    stub = types.SimpleNamespace()
    stub.session_state = real_st.session_state
    stub.header = lambda *a, **k: None
    stub.markdown = lambda *a, **k: None
    stub.experimental_rerun = lambda : None
    # columns() will pop the next tuple/list from cols_sequence
    stub.columns = lambda *a, **k: cols_sequence.pop(0)
    return stub


def test_search_calls_api(monkeypatch):
    """Default load should call api_get('/books/', {'search':'', 'page':1})."""
    called = {}
    def fake_api_get(path, params):
        called['path'], called['params'] = path, params
        return {'results': [], 'total_pages': 1}

    # Patch api_get in the module under test
    monkeypatch.setattr(mod, 'api_get', fake_api_get)

    # Prepare stubbed st.columns sequence:
    # 1st call: (col1, col2)
    # 2nd call: (prev, info, nxt)
    col1 = ColStub(text_input_ret="", button_ret=False)
    col2 = ColStub(text_input_ret="", button_ret=False)
    prev = ColStub(button_ret=False)
    info = ColStub()
    nxt = ColStub(button_ret=False)
    cols_seq = [
        (col1, col2),
        (prev, info, nxt),
    ]

    # Replace st in module
    monkeypatch.setattr(mod, 'st', make_stub_st(cols_seq))

    # Run the page
    mod.search_page()

    # Assert api_get saw correct args
    assert called['path'] == '/books/'
    assert called['params'] == {'search': "", 'page': 1}


def test_search_button_sets_page(monkeypatch):
    """Clicking the Search button should set session_state['search_page']=1."""
    # Stub api_get so page runs
    monkeypatch.setattr(mod, 'api_get',
                        lambda path, params: {'results': [], 'total_pages': 1})

    # First columns: user types "foo" & clicks Search
    col1 = ColStub(text_input_ret="foo", button_ret=False)
    col2 = ColStub(text_input_ret="", button_ret=True)
    # Then pagination columns (no nav clicks)
    prev = ColStub(button_ret=False)
    info = ColStub()
    nxt = ColStub(button_ret=False)
    cols_seq = [
        (col1, col2),
        (prev, info, nxt),
    ]
    monkeypatch.setattr(mod, 'st', make_stub_st(cols_seq))

    mod.search_page()
    assert real_st.session_state['search_page'] == 1


def test_pagination_prev_and_next(monkeypatch):
    """When Prev is clicked (page>1) it decrements; when Next is clicked (page<total), it increments."""
    # Stub out api_get to always return 3 total pages
    monkeypatch.setattr(mod, 'api_get',
                        lambda path, params: {'results': [], 'total_pages': 3})

    # ----- PREV BUTTON -----
    # Start on page 2
    real_st.session_state['search_page'] = 2

    # Stub columns: no search click, Prev=True, Next=False
    col1 = ColStub(text_input_ret="", button_ret=False)
    col2 = ColStub(text_input_ret="", button_ret=False)
    prev = ColStub(button_ret=True)
    info = ColStub()
    nxt = ColStub(button_ret=False)
    cols_seq = [(col1, col2), (prev, info, nxt)]
    monkeypatch.setattr(mod, 'st', make_stub_st(cols_seq))

    mod.search_page()
    # Expect 2 → 1
    assert real_st.session_state['search_page'] == 1

    # ----- NEXT BUTTON -----
    # Now start back on page 1
    real_st.session_state['search_page'] = 1

    # Stub columns again: no search click, Prev=False, Next=True
    col1 = ColStub(text_input_ret="", button_ret=False)
    col2 = ColStub(text_input_ret="", button_ret=False)
    prev = ColStub(button_ret=False)
    info = ColStub()
    nxt = ColStub(button_ret=True)
    cols_seq = [(col1, col2), (prev, info, nxt)]
    monkeypatch.setattr(mod, 'st', make_stub_st(cols_seq))

    mod.search_page()
    # Expect 1 → 2
    assert real_st.session_state['search_page'] == 2
