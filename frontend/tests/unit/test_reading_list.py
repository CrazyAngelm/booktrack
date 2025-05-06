import streamlit as real_st
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import app.components.reading_list as mod
import pytest

class Col:
    def __init__(self):
        self.image_calls = []
        self.markdown_calls = []
        self.button_calls = {}  # key -> True/False

    def image(self, url, width=None):
        self.image_calls.append((url, width))

    def markdown(self, txt):
        self.markdown_calls.append(txt)

    def button(self, label, key=None, on_click=None, args=None):
        clicked = self.button_calls.get(key, False)
        if clicked and on_click:
            on_click(*args if args else [])
        return clicked
    
class STStub:
    """
    Stub for streamlit in reading_list_page:
     - header, info, selectbox, columns, experimental_rerun
     - shares real session_state
    """
    def __init__(self, cols_sequence, select_ret='All'):
        self.session_state = real_st.session_state
        self._cols_seq = cols_sequence[:]
        self.last_header = None
        self.last_info = None
        self.select_ret = select_ret
        self.did_rerun = False

    def header(self, txt):
        self.last_header = txt

    def info(self, txt):
        self.last_info = txt

    def selectbox(self, label, options, key=None):
        # return the preset filter value
        return self.select_ret

    def columns(self, *args, **kwargs):
        # pop next group of cols
        return self._cols_seq.pop(0)

    def experimental_rerun(self):
        self.did_rerun = True

@pytest.fixture(autouse=True)
def clear_state():
    real_st.session_state.clear()
    yield
    real_st.session_state.clear()

def test_empty_reading_list(monkeypatch):
    # api_get returns empty
    monkeypatch.setattr(mod, 'api_get', lambda path: [])
    stub = STStub([])
    monkeypatch.setattr(mod, 'st', stub)

    mod.reading_list_page()

    assert stub.last_header == 'My Reading List'
    assert stub.last_info == "Your reading list is empty."

def test_render_all_status(monkeypatch):
    # Prepare two books with different statuses
    rl = [
        {'id':1,'title':'Book1','authors':['A'],'cover_url':'u1','status':'Want','popularity':10,'excerpt':'X'},
        {'id':2,'title':'Book2','authors':['B'],'cover_url':'u2','status':'Read','popularity':20,'excerpt':'Y'},
    ]
    monkeypatch.setattr(mod, 'api_get', lambda path: rl)

    # Stub columns for each book: two columns for image+text+button
    cols_sequence = []
    cols_sequence.append((Col(), Col(), Col()))  # for Book1
    cols_sequence.append((Col(), Col(), Col()))  # for Book2

    stub = STStub(cols_sequence, select_ret='All')
    monkeypatch.setattr(mod, 'st', stub)
    # track set_selected_book calls
    calls = []
    monkeypatch.setattr(mod, 'set_selected_book', lambda bid: calls.append(bid))

    mod.reading_list_page()

    # Verify both books were rendered
    # After loop, cols_sequence should be empty
    assert stub._cols_seq == []

    # Check that each first column got image called
    # We can inspect the initial Cols we created:
    col1a, col2a, col3a = cols_sequence[0]
    assert col1a.image_calls == [('u1', 140)]
    assert any('**Book1**' in md for md in col2a.markdown_calls)

    col1b, col2b, col3b = cols_sequence[1]
    assert col1b.image_calls == [('u2', 140)]
    assert any('**Book2**' in md for md in col2b.markdown_calls)

def test_filter_by_status_and_details_click(monkeypatch):
    # Only render items matching status="Reading"
    rl = [
        {'id':1,'title':'B1','authors':['A'],'cover_url':'u','status':'Reading','popularity':5,'excerpt':''},
        {'id':2,'title':'B2','authors':['B'],'cover_url':'v','status':'Want','popularity':8,'excerpt':''},
    ]
    monkeypatch.setattr(mod, 'api_get', lambda path: rl)

    # Prep cols only for the one matching
    col1, col2, col3 = Col(), Col(), Col()
    # Simulate clicking Details button
    col3.button_calls['reading_1'] = True

    stub = STStub([(col1, col2, col3)], select_ret='Reading')
    monkeypatch.setattr(mod, 'st', stub)

    # capture set_selected_book and rerun
    selected = []
    monkeypatch.setattr(mod, 'set_selected_book', lambda bid: selected.append(bid))

    mod.reading_list_page()

    # Only Book1 should produce columns
    assert stub._cols_seq == []  # used up
    assert selected == [1]
    assert stub.did_rerun is True