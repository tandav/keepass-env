import tempfile

import pykeepass
import pytest

import keepass_env


@pytest.fixture(scope='session')
def PASSWORD():
    return 'secure-af'


@pytest.fixture(scope='session')
def env():
    return {f'key-{i}': f'value-{i}' for i in range(10)}


@pytest.fixture(scope='session')
def env2():
    return {f'key-{i}': f'value-{i}' for i in range(100, 110)}


@pytest.fixture(scope='session')
def kp(PASSWORD, env, env2):  # pylint: disable=W0621
    with tempfile.NamedTemporaryFile() as f:
        k = pykeepass.create_database(f.name, password=PASSWORD)
        k.reload()
        k.add_group(k.root_group, 'main')
        g_level0 = k.add_group(k.root_group, 'g_level0')
        k.add_group(g_level0, 'g_level1')
        k.add_entry(g_level0, 'title-1', username='username-1', password='password-1', url='url-1')
        k.add_entry(g_level0, 'title-2', username='ref@main/entry-1:key-0', password='ref@main/entry-1:key-0', url='ref@main/entry-1:key-0')
        k.save(transformed_key=k.transformed_key)

        ke = keepass_env.KeepassEnv(k.filename, transformed_key=k.transformed_key)

        ke.write_env(['main', 'entry-1'], env)
        ke.write_env(['g_level0', 'g_level1', 'entry-2'], env2)
        ke.write_env(
            ['main', 'entry-3'], {
                'key-0': 'value-0',
                'key-1': 'ref@main/entry-1:key-0',
                'key-2': 'ref@g_level0/g_level1/entry-2:key-100',
                'key-3': 'ref@main/entry-3:key-1',
            },
        )
        ke.write_env(
            ['main', 'entry-4'], {
                'key-0': 'ref@main/non-existing-entry:key',
            },
        )
        ke.write_env(
            ['main', 'entry-5'], {
                'key-0': 'ref@main/entry-4:non-existing-attribute',
            },
        )
        ke.write_env(
            ['main', 'entry-6'], {
                'key-0': 'ref@g_level0/title-1:__title__',
                'key-1': 'ref@g_level0/title-1:__username__',
                'key-2': 'ref@g_level0/title-1:__password__',
                'key-3': 'ref@g_level0/title-1:__url__',
            },
        )
        ke.write_env(
            ['main', 'entry-7'], {
                'key-0': 'ref@g_level0/title-2:__title__',
                'key-1': 'ref@g_level0/title-2:__username__',
                'key-2': 'ref@g_level0/title-2:__password__',
                'key-3': 'ref@g_level0/title-2:__url__',
            },
        )
        # k.reload()
        ke.kp.reload()
        yield ke
