import os
from collections.abc import Sequence

from pykeepass import PyKeePass
from pykeepass.entry import Entry

__version__ = '0.0.7'

REF_PREFIX = 'ref@'
REF_SEP = '/'
REF_SEP2 = ':'
ATTR_TITLE = '__title__'
ATTR_USERNAME = '__username__'
ATTR_PASSWORD = '__password__'
ATTR_URL = '__url__'


def validate_ref(ref: str) -> None:
    if not ref:
        raise ValueError('Empty ref')
    if not ref.startswith(REF_PREFIX):
        raise ValueError(f'Invalid ref: {ref}, prefix {REF_PREFIX!r} expected')
    if ref.removeprefix(REF_PREFIX).count(REF_SEP) < 1:
        raise ValueError(
            f'Invalid ref: {ref}, at least 1 separator {REF_SEP!r} expected',
        )
    if ref.removeprefix(REF_PREFIX).count(REF_SEP2) != 1:
        raise ValueError(
            f'Invalid ref: {ref}, exactly 1 separator {REF_SEP2!r} expected',
        )


def parse_ref(ref: str) -> tuple[list[str], str]:
    validate_ref(ref)
    ref = ref.removeprefix(REF_PREFIX)
    _path, attribute = ref.rsplit(REF_SEP2, maxsplit=1)
    path = _path.split(REF_SEP)
    return path, attribute


def load_ref(kp: PyKeePass, ref: str) -> str:
    path, attribute = parse_ref(ref)
    entry = kp.find_entries_by_path(path)
    if entry is None:
        raise KeyError(f'Entry {path!r} not found')
    if attribute == ATTR_TITLE:
        out: str = entry.title
    elif attribute == ATTR_USERNAME:
        out = entry.username
    elif attribute == ATTR_PASSWORD:
        out = entry.password
    elif attribute == ATTR_URL:
        out = entry.url
    else:
        out = entry.custom_properties[attribute]
    if out.startswith(REF_PREFIX):
        if attribute == ATTR_TITLE:
            raise ValueError(f'Invalid ref: {ref}, title cannot be a ref')
        return load_ref(kp, out)
    return out


def env_values(
    filename: str,
    entry_path: Sequence[str],
    password: str | None = None,
    keyfile: str | None = None,
    transformed_key: bytes | None = None,
) -> dict[str, str]:
    kp = PyKeePass(filename, password, keyfile, transformed_key)
    entry = kp.find_entries_by_path(entry_path)
    if entry is None:
        raise KeyError(f'Entry {entry_path!r} not found')
    kv = entry.custom_properties
    env = {}
    for k, v in kv.items():
        if v.startswith(REF_PREFIX):
            v = load_ref(kp, v)
        env[k] = v
    return env


def load_env(
    filename: str,
    entry_path: Sequence[str],
    password: str | None = None,
    keyfile: str | None = None,
    transformed_key: bytes | None = None,
) -> None:
    env = env_values(
        filename=filename,
        entry_path=entry_path,
        password=password,
        keyfile=keyfile,
        transformed_key=transformed_key,
    )
    for k, v in env.items():
        os.environ[k] = v


def _create_entry(kp: PyKeePass, entry_path: Sequence[str]) -> Entry | None:
    entry = kp.find_entries_by_path(entry_path)
    if entry is not None:
        return None
    *groups, entry_title = entry_path
    if not groups:
        group = kp.root_group
    else:
        for i in range(len(groups)):
            group = kp.find_groups_by_path(groups[:i + 1])
            if group is None:
                if i == 0:
                    destination_group = kp.root_group
                else:
                    destination_group = kp.find_groups_by_path(groups[:i])
                group = kp.add_group(destination_group, groups[i])
    return kp.add_entry(group, title=entry_title, username='', password='')


def write_env(
    filename: str,
    entry_path: Sequence[str],
    env: dict[str, str],
    password: str | None = None,
    keyfile: str | None = None,
    transformed_key: bytes | None = None,
    create_if_not_exists: bool = True,
) -> None:
    kp = PyKeePass(filename, password, keyfile, transformed_key)
    entry = kp.find_entries_by_path(entry_path)
    if entry is None:
        if create_if_not_exists:
            entry = _create_entry(kp, entry_path)
        else:
            raise KeyError(f'Entry {entry_path!r} not found')
    for k, v in env.items():
        entry.set_custom_property(k, v)
    kp.save(transformed_key=kp.transformed_key)
