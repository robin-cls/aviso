import os
from pathlib import Path
import netrc
import getpass

import logging

logger = logging.getLogger(__name__)

NETRC_PATH = Path.home() / ".netrc"

def ensure_credentials(host: str):
    creds = _get_credentials(host)
    if creds:
        return creds
    else:
        return _prompt_and_save_credentials(host)

def _get_credentials(host: str):
    if not NETRC_PATH.exists():
        return None

    try:
        auth_data = netrc.netrc(NETRC_PATH)
        login, _, password = auth_data.authenticators(host)
        if login and password:
            return login, password
    except Exception as e:
        logging.error(f"Error reading .netrc : {e}")
    
    return None

def _prompt_and_save_credentials(host: str):
    logging.info(f"Credentials required for {host}")
    login = input("Username : ")
    password = getpass.getpass("Password : ")

    with open(NETRC_PATH, "a") as f:
        f.write(f"\nmachine {host} login {login} password {password}\n")

    os.chmod(NETRC_PATH, 0o600)

    return login, password