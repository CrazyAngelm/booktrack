import streamlit as st


def render_book_card(book: dict, on_click):
    cols = st.columns([1, 4, 1])
    cols[0].image(book['cover_url'], width=140)
    cols[1].markdown(f"**{book['title']}**  by {', '.join(book['authors'])}")
    cols[1].markdown(
        f"Popularity: {book.get('popularity', 'N/A')}"
    )
    cols[1].markdown(
        f"Excerpt: {book.get('excerpt', '')}"
    )
    if cols[2].button(
        'Details',
        key=f"detail_{book['id']}",
        on_click=on_click,
        args=(book['id'],)
    ):
        st.experimental_rerun()
