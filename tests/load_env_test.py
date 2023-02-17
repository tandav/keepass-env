import os

import pytest

import keepass_env


@pytest.mark.parametrize(
    'entry_path', [
        (['main', 'entry-1']),
    ],
)
def test_load_env(entry_path, kp, env):
    keepass_env.load_env(kp.filename, entry_path, transformed_key=kp.transformed_key)
    for k, v in env.items():
        assert os.environ[k] == v
