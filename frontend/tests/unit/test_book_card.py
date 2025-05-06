import streamlit as st

from app.components.book_card import render_book_card

class DummyCol:
    def __init__(self):
        self._clicked = False
    def image(self, *args, **kwargs): pass
    def markdown(self, *args, **kwargs): pass
    def button(self, label, key=None, on_click=None, args=None):
        # simulate click only if label == 'Details'
        if label == 'Details':
            on_click(*args)
        return False

def test_render_book_card(monkeypatch):
    # monkey-patch columns to return three DummyCols
    monkeypatch.setattr(st, 'columns', lambda *args, **kwargs: [DummyCol(), DummyCol(), DummyCol()])
    # prepare fake book
    book = {
        'id': 5,
        'title': 'X',
        'authors': ['A'],
        'excerpt': 'E',
        'cover_url': 'http://img',
        'popularity': 42
    }
    # track callback
    callback_called = {}
    def cb(bid):
        callback_called['id'] = bid

    render_book_card(book, on_click=cb)
    assert callback_called.get('id') == 5
