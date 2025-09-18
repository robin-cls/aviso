import logging
import os
import pathlib as pl

import requests

from .auth import ensure_credentials

logger = logging.getLogger(__name__)

TDS_HOST = 'tds-odatis.aviso.altimetry.fr'


def http_download(url: str, output_dir: str | pl.Path) -> str:
    """Download a granule from AVISO's Thredds Data Server using HTTPS
    protocol.

    Parameters
    ----------
    url: str
        the url to download
    output_dir: str | pl.Path
        existing directory to store the downloaded file.

    Returns
    -------
    str
        the local path to the downloaded file
    """
    (username, password) = ensure_credentials(TDS_HOST)

    logger.debug(f'Downloading {url}...')

    filename = os.path.basename(url)
    local_filepath = os.path.join(str(output_dir), filename)

    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()

        with open(local_filepath, 'wb') as f:
            f.write(response.content)

        logger.info(f'File {local_filepath} downloaded.')

        return local_filepath

    except requests.exceptions.HTTPError as e:
        logger.error(f'HTTP error : {e}')

    except requests.exceptions.RequestException as e:
        logger.error(f'Error : {e}')

    return
