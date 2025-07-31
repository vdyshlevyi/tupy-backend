import jwt
import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.api.authentication import utils
from tests.conftest import TestSettings


def test_get_password_hash_and_verify_password():
    password = "supersecret"
    hashed = utils.get_password_hash(password)
    assert isinstance(hashed, str)
    assert hashed != password
    # Should verify with correct password
    assert utils.verify_password(password, hashed)
    # Should not verify with incorrect password
    assert not utils.verify_password("wrongpassword", hashed)


@pytest.mark.parametrize(
    ("plain", "wrong"),
    [
        ("password123", "password124"),
        ("abcDEF!@#", "abcDEF!@#1"),
        ("", "notempty"),
    ],
)
def test_verify_password_negative(plain, wrong):
    hashed = utils.get_password_hash(plain)
    assert not utils.verify_password(wrong, hashed)


@pytest.mark.anyio
async def test_get_token_payload_valid(test_settings: TestSettings):
    payload = {"user_id": "test123"}
    token_str = jwt.encode(payload, test_settings.SECRET_KEY, algorithm=test_settings.ALGORITHM)

    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str)
    result = utils.get_token_payload(token=token, settings=test_settings)

    assert result == payload
