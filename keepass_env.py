import os
from collections.abc import Sequence

from pykeepass import PyKeePass

__version__ = '0.0.4'


def validate_ref(ref: str, prefix: str, sep: str, sep2: str) -> None:
    if not ref:
        raise ValueError('Empty ref')
    if not ref.startswith(prefix):
        raise ValueError(f'Invalid ref: {ref}, prefix {prefix!r} expected')
    if ref.count(sep) < 1:
        raise ValueError(
            f'Invalid ref: {ref}, at least 1 separator {sep!r} expected',
        )
    if ref.removeprefix(prefix).count(sep2) != 1:
        raise ValueError(
            f'Invalid ref: {ref}, exactly 1 separator {sep2!r} expected',
        )


def parse_ref(
    ref: str,
    prefix: str,
    sep: str,
    sep2: str,
) -> tuple[list[str], str]:
    validate_ref(ref, prefix, sep, sep2)
    ref = ref.removeprefix(prefix)
    _path, attribute = ref.split(sep2)
    path = _path.split(sep)
    return path, attribute


def load_ref(
    kp: PyKeePass,
    ref: str,
    prefix: str,
    sep: str,
    sep2: str,
) -> str:
    path, attribute = parse_ref(ref, prefix, sep, sep2)
    entry = kp.find_entries_by_path(path)
    out: str = entry.custom_properties[attribute]
    if out.startswith(prefix):
        return load_ref(kp, out, prefix, sep, sep2)
    return out


def env_values(
    filename: str,
    entry_path: Sequence[str],
    password: str | None = None,
    keyfile: str | None = None,
    transformed_key: bytes | None = None,
    ref_prefix: str = 'ref@',
    ref_sep: str = '/',
    ref_sep2: str = ':',
) -> dict[str, str]:
    kp = PyKeePass(filename, password, keyfile, transformed_key)
    entry = kp.find_entries_by_path(entry_path)
    kv = entry.custom_properties
    env = {}
    for k, v in kv.items():
        if v.startswith(ref_prefix):
            v = load_ref(kp, v, ref_prefix, ref_sep, ref_sep2)
        env[k] = v
    return env


def load_env(
    filename: str,
    entry_path: Sequence[str],
    password: str | None = None,
    keyfile: str | None = None,
    transformed_key: bytes | None = None,
    ref_prefix: str = 'ref@',
    ref_sep: str = '/',
    ref_sep2: str = ':',
) -> None:
    env = env_values(
        filename=filename,
        entry_path=entry_path,
        password=password,
        keyfile=keyfile,
        transformed_key=transformed_key,
        ref_prefix=ref_prefix,
        ref_sep=ref_sep,
    )
    for k, v in env.items():
        os.environ[k] = v
