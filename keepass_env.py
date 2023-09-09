import argparse
import getpass
import os
from collections.abc import Sequence

from pykeepass import PyKeePass
from pykeepass.entry import Entry

__version__ = '0.1.3'

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


class KeepassEnv:
    def __init__(
        self,
        filename: str,
        password: str | None = None,
        keyfile: str | None = None,
        transformed_key: bytes | None = None,
    ) -> None:
        self.kp = PyKeePass(filename, password, keyfile, transformed_key)

    def load_ref(self, ref: str) -> str:
        path, attribute = parse_ref(ref)
        entry = self.kp.find_entries_by_path(path)
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
            return self.load_ref(out)
        return out

    def env_values(
        self,
        entry_path: Sequence[str],
    ) -> dict[str, str]:
        entry = self.kp.find_entries_by_path(entry_path)
        if entry is None:
            raise KeyError(f'Entry {entry_path!r} not found')
        kv = entry.custom_properties
        env = {}
        for k, v in kv.items():
            if v.startswith(REF_PREFIX):
                env[k] = self.load_ref(kp, v)
            else:
                env[k] = v
        return env

    def load_env(
        self,
        entry_path: Sequence[str],
    ) -> None:
        env = self.env_values(entry_path=entry_path)
        for k, v in env.items():
            os.environ[k] = v

    def _create_entry(self, entry_path: Sequence[str]) -> Entry | None:
        entry = self.kp.find_entries_by_path(entry_path)
        if entry is not None:
            return None
        *groups, entry_title = entry_path
        if not groups:
            group = self.kp.root_group
        else:
            for i, _ in enumerate(groups):
                group = self.kp.find_groups_by_path(groups[:i + 1])
                if group is None:
                    if i == 0:
                        destination_group = self.kp.root_group
                    else:
                        destination_group = self.kp.find_groups_by_path(groups[:i])
                    group = self.kp.add_group(destination_group, groups[i])
        return self.kp.add_entry(group, title=entry_title, username='', password='')

    def write_env(
        self,
        entry_path: Sequence[str],
        env: dict[str, str],
        create_if_not_exists: bool = True,
    ) -> None:
        entry = self.kp.find_entries_by_path(entry_path)
        if entry is None:
            if create_if_not_exists:
                entry = self._create_entry(entry_path)
            else:
                raise KeyError(f'Entry {entry_path!r} not found')
        for k, v in env.items():
            entry.set_custom_property(k, v)
        self.kp.save(transformed_key=self.kp.transformed_key)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, help='Path to the database file. Can be set via KEEPASS_DB env var')
    parser.add_argument('--password', type=str, help='Database password. Can be set via KEEPASS_PASSWORD env var')
    parser.add_argument('--format', type=str, help='print format, possible options: env, shell, docker. Can be set via KEEPASS_FORMAT env var')
    parser.add_argument('--entry-path', type=str, help='Entry path. Can be set via KEEPASS_ENTRY_PATH env var. Example: "group1/group2/entry"')
    args = parser.parse_args()

    if args.db is None:
        args.db = os.environ.get('KEEPASS_DB')
    if args.db is None:
        raise ValueError('Database not specified. Use --db or KEEPASS_DB env var')

    if args.password is None:
        args.password = os.environ.get('KEEPASS_PASSWORD')
    if args.password is None:
        args.password = getpass.getpass()

    if args.entry_path is None:
        args.entry_path = os.environ.get('KEEPASS_ENTRY_PATH')
    if args.entry_path is None:
        raise ValueError('Entry path not specified. Use --entry-path or KEEPASS_ENTRY_PATH env var. Example: "group1/group2/entry"')
    args.entry_path = args.entry_path.split('/')

    if args.format is None:
        args.format = os.environ.get('KEEPASS_FORMAT', 'env')
    if args.format not in ('env', 'shell', 'docker'):
        raise ValueError(f'Invalid format: {args.format!r}. Possible options: env, shell, docker')

    return args


def print_env() -> None:
    args = parse_args()
    ke = KeepassEnv(filename=args.db, password=args.password)
    env = ke.env_values(args.entry_path)
    for k, v in env.items():
        if args.format == 'env':
            print(f'{k}={v}')
        elif args.format == 'docker':
            print(f'-e {k}={v}', end=' ')
        elif args.format == 'shell':
            print(f'export {k}={v}')
        else:
            raise ValueError(f'Invalid format: {args.format!r}')
