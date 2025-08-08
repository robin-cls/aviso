import logging
import os
import pathlib as pl

import requests

from .auth import ensure_credentials

logger = logging.getLogger(__name__)

TDS_HOST = 'tds-odatis.aviso.altimetry.fr'
TDS_FILE_SERVER_BASE_URL = 'https://tds-odatis.aviso.altimetry.fr/thredds/fileServer'


def http_download(url: str, output_dir: str | pl.Path) -> str:
    """Download a granule from AVISO's Thredds Data Server using HTTPS
    protocol.

    Parameters
    ----------
    url: str
        the url to download
    output_dir: str | pl.Path
        directory to store the downloaded file

    Returns
    -------
    str
        the local path to the downloaded file
    """
    (username, password) = ensure_credentials(TDS_HOST)

    # download url and store file in output_dir
    logger.debug(f'Downloading {url}...')
    response = requests.get(os.path.join(TDS_FILE_SERVER_BASE_URL, url),
                            auth=(username, password))

    filename = os.path.basename(url)
    local_filepath = os.path.join(str(output_dir), filename)

    if response.status_code == 200:
        with open(local_filepath, 'wb') as f:
            f.write(response.content)
    else:
        logger.error(f'Error {response.status_code} : {response.reason}')

    logger.info(f'File {local_filepath} downloaded.')
    return local_filepath
