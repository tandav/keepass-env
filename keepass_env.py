import os
from collections.abc import Sequence

from pykeepass import PyKeePass

__version__ = '0.0.7'

REF_PREFIX = 'ref@'
REF_SEP = '/'
REF_SEP2 = ':'


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
    out: str = entry.custom_properties[attribute]
    if out.startswith(REF_PREFIX):
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
