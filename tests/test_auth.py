import netrc
from pathlib import Path
from unittest.mock import mock_open

import pytest

import aviso_client.auth
from aviso_client.auth import (
    _get_credentials,
    _prompt_and_save_credentials,
    ensure_credentials,
)


@pytest.fixture
def fake_netrc_path(tmp_path, mocker):
    path = tmp_path / '.netrc'
    mocker.patch.object(aviso_client.auth, 'NETRC_PATH', path)
    return path


def test_get_credentials(fake_netrc_path, mocker):
    fake_netrc_path.write_text("""
        machine example.com login testuser password testpass
    """)
    mock_netrc = mocker.patch('aviso_client.auth.netrc.netrc')
    mock_netrc.return_value.authenticators.return_value = ('testuser', None,
                                                           'testpass')

    creds = _get_credentials('example.com')
    assert creds == ('testuser', 'testpass')


def test_get_credentials_netrc_not_exist(mocker):
    mocker.patch.object(Path, 'exists', return_value=False)

    creds = _get_credentials('example.com')
    assert creds is None


def test_get_credentials_netrc_invalid(mocker, caplog):
    mocker.patch('aviso_client.auth.netrc.netrc',
                 side_effect=netrc.NetrcParseError('Invalid netrc'))

    creds = _get_credentials('example.com')
    assert creds is None
    assert 'Syntax error' in caplog.text


def test_prompt_and_save_credentials(mocker, fake_netrc_path):
    mocker.patch('builtins.input', return_value='user2')
    mocker.patch('getpass.getpass', return_value='pass2')
    m_open = mocker.patch('builtins.open', mock_open())
    mocker.patch('os.chmod')

    creds = _prompt_and_save_credentials('example.org')
    assert creds == ('user2', 'pass2')

    m_open().write.assert_called_with(
        '\nmachine example.org login user2 password pass2\n')


def test_ensure_credentials_from_netrc(mocker):
    mock_get = mocker.patch('aviso_client.auth._get_credentials',
                            return_value=('user3', 'pass3'))

    creds = ensure_credentials('example.com')
    assert creds == ('user3', 'pass3')
    mock_get.assert_called_once_with('example.com')


def test_ensure_credentials_prompt(mocker):
    mock_get = mocker.patch('aviso_client.auth._get_credentials',
                            return_value=None)
    mock_prompt = mocker.patch(
        'aviso_client.auth._prompt_and_save_credentials',
        return_value=('user4', 'pass4'))

    creds = ensure_credentials('example.com')
    assert creds == ('user4', 'pass4')
    mock_get.assert_called_once_with('example.com')
    mock_prompt.assert_called_once_with('example.com')
