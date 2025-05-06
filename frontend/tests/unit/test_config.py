from app import Settings

def test_defaults():
    s = Settings()
    assert s.API_BASE_URL.endswith('/api/v1')
    assert isinstance(s.PER_PAGE, int)
