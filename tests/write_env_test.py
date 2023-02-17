import tempfile

import pykeepass
import pytest

import keepass_env


def test_write_env(PASSWORD):
    with tempfile.NamedTemporaryFile() as f:
        kp = pykeepass.create_database(f.name, password=PASSWORD)
        kp.reload()
        keepass_env.write_env(
            filename=f.name,
            entry_path=['test'],
            env={'key': 'value'},
            transformed_key=kp.transformed_key,
        )
        kp.reload()
        assert kp.find_entries_by_path(['test']) is not None
        assert kp.find_entries_by_path(['test']).custom_properties == {'key': 'value'}


def test_write_env_create_if_not_exists():
    with tempfile.NamedTemporaryFile() as f:
        pykeepass.create_database(f.name)
        with pytest.raises(KeyError):
            keepass_env.write_env(
                filename=f.name,
                entry_path=['test3'],
                env={'key': 'value'},
                create_if_not_exists=False,
            )
