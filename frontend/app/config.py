import os

class Settings:
    API_BASE_URL: str = os.getenv('API_BASE_URL', 'http://localhost:8000/api/v1')
    BYPASS_AUTH: bool = os.getenv('BYPASS_AUTH', 'false').lower() == 'true'
    USE_FAKE_DATA: bool = os.getenv('USE_FAKE_DATA', 'false').lower() == 'true'
    PER_PAGE: int = int(os.getenv('PER_PAGE', '20'))

settings = Settings()
