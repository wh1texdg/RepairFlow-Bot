from app.core.security import create_access_token, decode_access_token


def test_jwt_roundtrip():
    token = create_access_token("42", "ADMIN")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "ADMIN"
