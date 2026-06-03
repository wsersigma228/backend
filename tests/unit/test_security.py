from backend.security import verify_password, get_password_hash

def test_password_hashing():
    plain_password = "my_super_secret_password"

    hashed_password = get_password_hash(plain_password)

    assert hashed_password != plain_password

    assert verify_password(plain_password, hashed_password) is True

    assert verify_password("wrong_password", hashed_password) is False