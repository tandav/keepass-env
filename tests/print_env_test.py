import os
import subprocess
from unittest import mock

import pytest


@pytest.mark.parametrize('format', ['env', 'shell', 'docker'])
def test_print_env_args(kp, env, PASSWORD, format):
    cmd = ['keepass-env', '--db', kp.filename, '--password', PASSWORD, '--entry-path', 'main/entry-1', '--format', format]
    stdout = subprocess.check_output(cmd, text=True)
    if format == 'env':
        assert stdout == ''.join(f'{k}={v}\n' for k, v in env.items())
    elif format == 'shell':
        assert stdout == ''.join(f'export {k}={v}\n' for k, v in env.items())
    elif format == 'docker':
        assert stdout == ''.join(f'-e {k}={v} ' for k, v in env.items())


@pytest.mark.parametrize('format', ['env', 'shell', 'docker'])
def test_print_env_env(kp, env, PASSWORD, format):
    environ = {'KEEPASS_DB': kp.filename, 'KEEPASS_PASSWORD': PASSWORD, 'KEEPASS_ENTRY_PATH': 'main/entry-1', 'KEEPASS_FORMAT': format}
    with mock.patch.dict(os.environ, environ):
        stdout = subprocess.check_output(['keepass-env'], text=True)
    if format == 'env':
        assert stdout == ''.join(f'{k}={v}\n' for k, v in env.items())
    elif format == 'shell':
        assert stdout == ''.join(f'export {k}={v}\n' for k, v in env.items())
    elif format == 'docker':
        assert stdout == ''.join(f'-e {k}={v} ' for k, v in env.items())
