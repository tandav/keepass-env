import os
import subprocess
from unittest import mock

import pytest


@pytest.mark.parametrize('export', [False, True])
def test_print_env_args(kp, env, PASSWORD, export):
    cmd = ['keepass-env', '--db', kp.filename, '--password', PASSWORD, '--entry-path', 'main/entry-1']
    if export:
        cmd.append('--export')
    stdout = subprocess.check_output(cmd, text=True)
    if export:
        assert stdout == ''.join(f'export {k}={v}\n' for k, v in env.items())
    else:
        assert stdout == ''.join(f'{k}={v}\n' for k, v in env.items())


@pytest.mark.parametrize('export', [False, True])
def test_print_env_env(kp, env, PASSWORD, export):
    environ = {'KEEPASS_DB': kp.filename, 'KEEPASS_PASSWORD': PASSWORD, 'KEEPASS_ENTRY_PATH': 'main/entry-1'}
    if export:
        environ['KEEPASS_EXPORT'] = '1'
    with mock.patch.dict(os.environ, environ):
        stdout = subprocess.check_output(['keepass-env'], text=True)
    if export:
        assert stdout == ''.join(f'export {k}={v}\n' for k, v in env.items())
    else:
        assert stdout == ''.join(f'{k}={v}\n' for k, v in env.items())
