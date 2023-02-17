import tempfile

import pykeepass


def test_unencrypt_with_password(PASSWORD):
    with tempfile.NamedTemporaryFile() as f:
        pykeepass.create_database(f.name, password=PASSWORD)
        pykeepass.PyKeePass(f.name, password=PASSWORD)


def test_unencrypt_with_transformed_key(PASSWORD):
    with tempfile.NamedTemporaryFile() as f:
        kp = pykeepass.create_database(f.name, password=PASSWORD)
        kp.reload()  # reload to get transformed_key (or it will be default and equal between databases)
        pykeepass.PyKeePass(f.name, transformed_key=kp.transformed_key)
