import getpass
import logging
import netrc
import os
from pathlib import Path

NETRC_PATH = Path.home() / '.netrc'


def ensure_credentials(host: str):
    """Ensure credentials are present in a .netrc, and prompt otherwise.

    Args:
        host (str):
            host for which credentials are needed

    Returns:
        tuple(str, str):
            (username, password) tuple
    """
    creds = _get_credentials(host)
    if creds:
        return creds
    else:
        return _prompt_and_save_credentials(host)


def _get_credentials(host: str):
    """Get credentials stored in .netrc."""
    if not NETRC_PATH.exists():
        return None

    try:
        auth_data = netrc.netrc(NETRC_PATH)
        login, _, password = auth_data.authenticators(host)
        if login and password:
            return login, password
    except netrc.NetrcParseError as e:
        logging.error('Syntax error in .netrc file: %s', e)
    except (TypeError, AttributeError) as e:
        logging.error('Error reading credentials for %s', e)
    except Exception as e:
        logging.error('Error reading .netrc : %s', e)

    return None


def _prompt_and_save_credentials(host: str):
    """Prompt and save credentials."""
    logging.info(f'Credentials required for {host}')
    login = input('Username : ')
    password = getpass.getpass('Password : ')

    with open(NETRC_PATH, 'a') as f:
        f.write(f'\nmachine {host} login {login} password {password}\n')

    os.chmod(NETRC_PATH, 0o600)

    return login, password
