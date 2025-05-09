from hypothesis import given, strategies as st
import pytest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from util.token import create_access_token, decode_access_token


@given(user_id=st.uuids())
def test_jwt_roundtrip(user_id):
    db = MagicMock(spec=Session)
    token = create_access_token(db, {"id": str(user_id)})
    data = decode_access_token(token["access_token"])
    assert data["id"] == str(user_id)
