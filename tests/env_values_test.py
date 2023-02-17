import pytest

import keepass_env


@pytest.mark.parametrize(
    'entry_path', [
        (['main', 'entry-1']),
    ],
)
def test_env_values(entry_path, kp, env):
    assert keepass_env.env_values(kp.filename, entry_path, transformed_key=kp.transformed_key) == env


@pytest.mark.parametrize(
    'entry_path', [
        (['g_level0', 'g_level1', 'entry-2']),
    ],
)
def test_env_values_nested(entry_path, kp, env2):
    assert keepass_env.env_values(kp.filename, entry_path, transformed_key=kp.transformed_key) == env2


@pytest.mark.parametrize(
    'entry_path, expected', [
        (
            ['main', 'entry-3'], {
                'key-0': 'value-0',
                'key-1': 'value-0',
                'key-2': 'value-100',
                'key-3': 'value-0',
            },
        ),
        (
            ['main', 'entry-6'], {
                'key-0': 'title-1',
                'key-1': 'username-1',
                'key-2': 'password-1',
                'key-3': 'url-1',
            },
        ),
        (
            ['main', 'entry-7'], {
                'key-0': 'title-2',
                'key-1': 'value-0',
                'key-2': 'value-0',
                'key-3': 'value-0',
            },
        ),
    ],
)
def test_refs(entry_path, expected, kp):
    assert keepass_env.env_values(kp.filename, entry_path, transformed_key=kp.transformed_key) == expected


@pytest.mark.parametrize(
    'entry_path', [
        (['main', 'non-existing-entry']),
        (['main', 'entry-4']),
    ],
)
def test_entry_not_found(kp, entry_path):
    with pytest.raises(KeyError):
        keepass_env.env_values(kp.filename, entry_path, transformed_key=kp.transformed_key)


def test_attribute_not_found(kp):
    with pytest.raises(KeyError):
        keepass_env.env_values(kp.filename, ['main', 'entry-5'], transformed_key=kp.transformed_key)
