import os
import tempfile

import pykeepass
import pytest
from pykeepass import PyKeePass
from pykeepass.group import Group

import keepass_env

TEST_VALUE = 'test-value'


def _add_entry_with_attributes(
    kp: PyKeePass,
    group: Group,
    title: str,
    username: str,
    password: str,
    kv: dict[str, str],
) -> None:
    entry = kp.add_entry(group, title, username, password)
    for k, v in kv.items():
        entry.set_custom_property(k, v)


@pytest.fixture(scope='session')
def env():
    return {f'key-{i}': f'value-{i}' for i in range(10)}


@pytest.fixture(scope='session')
def env2():
    return {f'key-{i}': f'value-{i}' for i in range(100, 110)}


@pytest.fixture(scope='session')
def env_with_refs():
    return {
        'key-0': 'value-0',
        'key-1': 'ref@main/entry-1:key-0',
        'key-2': 'ref@g_level0/g_level1/entry-2:key-100',
    }


@pytest.fixture(scope='session')
def kp(env, env2, env_with_refs):
    with tempfile.NamedTemporaryFile() as f:
        kp = pykeepass.create_database(f.name)
        g_main = kp.add_group(kp.root_group, 'main')
        g_level0 = kp.add_group(kp.root_group, 'g_level0')
        g_level1 = kp.add_group(g_level0, 'g_level1')
        _add_entry_with_attributes(
            kp, g_main, 'entry-1', TEST_VALUE, TEST_VALUE, env,
        )
        _add_entry_with_attributes(
            kp, g_level1, 'entry-2', TEST_VALUE, TEST_VALUE, env2,
        )
        _add_entry_with_attributes(
            kp, g_main, 'entry-3', TEST_VALUE, TEST_VALUE, env_with_refs,
        )
        kp.save()
        yield kp


@pytest.mark.parametrize(
    'entry_path', [
        (['main', 'entry-1']),
    ],
)
def test_env_values(entry_path, kp, env):
    assert keepass_env.env_values(kp.filename, entry_path) == env


@pytest.mark.parametrize(
    'entry_path', [
        (['g_level0', 'g_level1', 'entry-2']),
    ],
)
def test_env_values_nested(entry_path, kp, env2):
    assert keepass_env.env_values(kp.filename, entry_path) == env2


@pytest.mark.parametrize(
    'entry_path', [
        (['main', 'entry-3']),
    ],
)
def test_env_values_with_refs(entry_path, kp, env_with_refs):
    assert keepass_env.env_values(kp.filename, entry_path) == {
        'key-0': 'value-0',
        'key-1': 'value-0',
        'key-2': 'value-100',
    }


@pytest.mark.parametrize(
    'entry_path', [
        (['main', 'entry-1']),
    ],
)
def test_load_env(entry_path, kp, env):
    keepass_env.load_env(kp.filename, entry_path)
    for k, v in env.items():
        assert os.environ[k] == v


@pytest.mark.parametrize(
    'ref', [
        '',
        'main/entry-1:key-0',
        'ref@main',
        'ref@main/entry-1',
        'ref@main/entry-1:key-0:extra',
    ],
)
def test_validate_ref(ref):
    with pytest.raises(ValueError):
        keepass_env.validate_ref(ref, prefix='ref@', sep='/', sep2=':')
