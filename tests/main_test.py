import os
import tempfile

import pykeepass
import pytest

import keepass_env


@pytest.mark.parametrize(
    'entry_path', [
        ['entry_title'],
        ['group0', 'entry_title'],
        ['group0', 'group1', 'group2', 'entry_title'],
    ],
)
def test_create_entry(entry_path):
    with tempfile.NamedTemporaryFile() as f:
        kp = pykeepass.create_database(f.name)
        e = keepass_env._create_entry(kp, entry_path)
        assert kp.find_entries_by_path(entry_path) == e


def test_write_env():
    with tempfile.NamedTemporaryFile() as f:
        kp = pykeepass.create_database(f.name)
        keepass_env.write_env(
            filename=f.name,
            entry_path=['test'],
            env={'key': 'value'},
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


@pytest.fixture(scope='session')
def env():
    return {f'key-{i}': f'value-{i}' for i in range(10)}


@pytest.fixture(scope='session')
def env2():
    return {f'key-{i}': f'value-{i}' for i in range(100, 110)}


@pytest.fixture(scope='session')
def kp(env, env2):
    with tempfile.NamedTemporaryFile() as f:
        kp = pykeepass.create_database(f.name)
        kp.add_group(kp.root_group, 'main')
        g_level0 = kp.add_group(kp.root_group, 'g_level0')
        kp.add_group(g_level0, 'g_level1')
        kp.save()
        keepass_env.write_env(f.name, ['main', 'entry-1'], env)
        keepass_env.write_env(f.name, ['g_level0', 'g_level1', 'entry-2'], env2)
        keepass_env.write_env(
            f.name, ['main', 'entry-3'], {
                'key-0': 'value-0',
                'key-1': 'ref@main/entry-1:key-0',
                'key-2': 'ref@g_level0/g_level1/entry-2:key-100',
                'key-3': 'ref@main/entry-3:key-1',
            },
        )
        keepass_env.write_env(
            f.name, ['main', 'entry-4'], {
                'key-0': 'ref@main/non-existing-entry:key',
            },
        )
        keepass_env.write_env(
            f.name, ['main', 'entry-5'], {
                'key-0': 'ref@main/entry-4:non-existing-attribute',
            },
        )
        kp.reload()
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
def test_env_values_with_refs(entry_path, kp):
    assert keepass_env.env_values(kp.filename, entry_path) == {
        'key-0': 'value-0',
        'key-1': 'value-0',
        'key-2': 'value-100',
        'key-3': 'value-0',
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
        keepass_env.validate_ref(ref)


@pytest.mark.parametrize(
    'entry_path', [
        (['main', 'non-existing-entry']),
        (['main', 'entry-4']),
    ],
)
def test_entry_not_found(kp, entry_path):
    with pytest.raises(KeyError):
        keepass_env.env_values(kp.filename, entry_path)


def test_attribute_not_found(kp):
    with pytest.raises(KeyError):
        keepass_env.env_values(kp.filename, ['main', 'entry-5'])
