import tempfile

import pykeepass
import pytest

import keepass_env


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
        ['entry_title'],
        ['group0', 'entry_title'],
        ['group0', 'group1', 'group2', 'entry_title'],
    ],
)
def test_create_entry(entry_path):
    with tempfile.NamedTemporaryFile() as f:
        kp = pykeepass.create_database(f.name)
        e = keepass_env._create_entry(kp, entry_path) # pylint: disable=W0212
        assert kp.find_entries_by_path(entry_path) == e
