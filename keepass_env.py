import os
from collections.abc import Sequence

from pykeepass import PyKeePass

__version__ = '0.0.1'


# def parse_ref(ref: str) -> tuple[str, str]:
#     pass


def load_ref(ref: str, sep: str) -> list[str]:
    *path, key = ref.split(sep)
    return ['dummy']


def env_values(
    filename: str,
    entry_path: Sequence[str],
    password: str | None = None,
    keyfile: str | None = None,
    transformed_key: bytes | None = None,
    ref_prefix: str = 'ref:',
    ref_sep: str = '/',
) -> dict[str, str]:
    kp = PyKeePass(filename, password, keyfile, transformed_key)
    entry = kp.find_entries_by_path(entry_path)
    kv = entry.custom_properties
    env = {}
    for k, v in kv.items():
        if v.startswith(ref_prefix):
            v = load_ref(v.removeprefix(ref_prefix), ref_sep)
        env[k] = v
    return env


def load_env(
    filename: str,
    entry_path: Sequence[str],
    password: str | None = None,
    keyfile: str | None = None,
    transformed_key: bytes | None = None,
    ref_prefix: str = 'ref:',
    ref_sep: str = '/',
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
