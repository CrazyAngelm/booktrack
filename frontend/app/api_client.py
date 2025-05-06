# app/api_client.py
import requests
from app.config import settings

if settings.USE_FAKE_DATA:
    from app.fake_data import FAKE_BOOKS, FAKE_DETAILS, FAKE_FAV, FAKE_RL


def api_get(path: str, params: dict = None):
    if settings.USE_FAKE_DATA:
        # list /books/
        if path == '/books/' and params is not None:
            page = params.get('page', 1)
            per_page = settings.PER_PAGE
            start, end = (page - 1) * per_page, page * per_page
            total = len(FAKE_BOOKS)
            return {
                'results': FAKE_BOOKS[start:end],
                'total_pages': (total + per_page - 1) // per_page
            }
        # details /books/{id}
        if path.startswith('/books/'):
            bid = int(path.rstrip('/').split('/')[-1])
            return FAKE_DETAILS.get(bid)
        # favourites
        if path == '/favourites/':
            return FAKE_FAV
        # reading list
        if path == '/reading-list/':
            return FAKE_RL

    # fallback to real API
    resp = requests.get(f"{settings.API_BASE_URL}{path}", params=params or {})
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, json: dict = None):
    if settings.USE_FAKE_DATA and path == '/favourites/':
        FAKE_FAV.append(FAKE_DETAILS.get(json['book_id']))
        return True
    resp = requests.post(f"{settings.API_BASE_URL}{path}", json=json or {})
    return resp.ok


def api_put(path: str, json: dict = None):
    if settings.USE_FAKE_DATA and path.startswith('/reading-list/'):
        bid = int(path.rstrip('/').split('/')[-1])
        for item in FAKE_RL:
            if item['id'] == bid:
                item['status'] = json['status']
                return True
        FAKE_RL.append({**FAKE_DETAILS[bid], 'status': json['status']})
        return True
    resp = requests.put(f"{settings.API_BASE_URL}{path}", json=json or {})
    return resp.ok


def api_delete(path: str):
    if settings.USE_FAKE_DATA:
        bid = int(path.rstrip('/').split('/')[-1])
        if path.startswith('/favourites/'):
            FAKE_FAV[:] = [f for f in FAKE_FAV if f['id'] != bid]
            return True
        if path.startswith('/reading-list/'):
            FAKE_RL[:] = [r for r in FAKE_RL if r['id'] != bid]
            return True
    resp = requests.delete(f"{settings.API_BASE_URL}{path}")
    return resp.ok
