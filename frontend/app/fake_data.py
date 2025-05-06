# app/fake_data.py
import random

# 10 demo cover URLs
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

# Generate 50 books with random popularity
FAKE_BOOKS = []
for i in range(1, 51):
    FAKE_BOOKS.append({
        'id': i,
        'title': f'Sample Book {i}',
        'authors': [f'Author {i}'],
        'excerpt': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        'cover_url': COVER_URLS[(i - 1) % len(COVER_URLS)],
        'popularity': random.randint(1, 100)
    })

# sort descending by popularity
FAKE_BOOKS.sort(key=lambda b: b['popularity'], reverse=True)

# Detailed info (one per book)
FAKE_DETAILS = {
    b['id']: {
        'id': b['id'],
        'title': b['title'],
        'authors': b['authors'],
        'cover_url': b['cover_url'],
        'description': (
            f'Full description for {b["title"]}. '
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        ),
        'rating': round(random.uniform(1, 5), 1)
    }
    for b in FAKE_BOOKS
}

# Start with 10 random favourites
FAKE_FAV = [FAKE_BOOKS[i] for i in random.sample(range(len(FAKE_BOOKS)), 10)]

# A tiny reading list with mixed statuses
FAKE_RL = [
    {**FAKE_BOOKS[1], 'status': 'Reading'},
    {**FAKE_BOOKS[3], 'status': 'Want'},
    {**FAKE_BOOKS[4], 'status': 'Read'}
]
