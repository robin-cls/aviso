import logging
import os
import pathlib as pl
import time
import warnings
from concurrent.futures import as_completed, ThreadPoolExecutor
from typing import Generator, Iterable

import requests

from .auth import ensure_credentials

logger = logging.getLogger(__name__)

TDS_HOST = 'tds-odatis.aviso.altimetry.fr'


def http_single_download(url: str, output_dir: str | pl.Path) -> str:
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

    logger.debug('Downloading %s...', url)

    filename = os.path.basename(url)
    local_filepath = os.path.join(str(output_dir), filename)

    response = requests.get(url, auth=(username, password))
    response.raise_for_status()

    with open(local_filepath, 'wb') as f:
        f.write(response.content)

    logger.info('File %s downloaded.', local_filepath)

    return local_filepath


def http_single_download_with_retries(url: str,
                                      output_dir: str | pl.Path,
                                      retries: int = 3,
                                      backoff: float = 1.0) -> str:
    """Download a granule from AVISO's Thredds Data Server using HTTPS
    protocol. Retries if the download fails.

    Parameters
    ----------
    url: str
        the url to download
    output_dir: str | pl.Path
        existing directory to store the downloaded file.
    retries: int
        number of retries
    backoff: float
        waiting time between two tries. Increases exponentially.

    Returns
    -------
    str
        the local path to the downloaded file
    """
    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            return http_single_download(url, output_dir)

        except requests.exceptions.HTTPError as e:
            warnings.warn('Attempt %d failed for %s: HTTP Error: %s' %
                          (attempt, url, e))

        except requests.exceptions.RequestException as e:
            warnings.warn('Attempt %d failed for %s: %s' % (attempt, url, e))

            last_exception = e
            if attempt < retries:
                time.sleep(backoff * (2**(attempt - 1)))

    logger.error('All %d attempts failed for %s.', retries, url)
    raise last_exception


def http_bulk_download(urls: list[str],
                       output_dir: str | pl.Path,
                       retries: int = 3,
                       backoff: float = 1.0) -> Generator[str, None, None]:
    """Loop on a list of urls to download each granule from AVISO's Thredds
    Data Server using HTTPS protocol. Each download as retries if it fails.

    Parameters
    ----------
    urls: list[str]
        the urls to download
    output_dir: str | pl.Path
        existing directory to store the downloaded file.
    retries: int
        number of retries
    backoff: float
        waiting time between two tries. Increases exponentially.

    Returns
    -------
    Iterator
        an iterator over the downloaded paths, one for each download that have succeeded
    """
    output_dir = pl.Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"No such file or directory '{output_dir}'.")

    for url in urls:
        try:
            local_path = http_single_download_with_retries(url,
                                                           output_dir,
                                                           retries=retries,
                                                           backoff=backoff)
            yield local_path
        except Exception as e:
            warnings.warn(f'Failed to download {url}: {e}')


def http_bulk_download_parallel(
        urls: Iterable[str],
        output_dir: str | pl.Path,
        retries: int = 3,
        backoff: float = 1.0,
        max_workers: int = 4) -> Generator[str, None, None]:
    """Parallel download of granules from AVISO's Thredds Data Server using
    HTTPS protocol.

    Parameters
    ----------
    urls: list[str]
        the urls to download
    output_dir: str | pl.Path
        existing directory to store the downloaded file.
    retries: int
        number of retries
    backoff: float
        waiting time between two tries. Increases exponentially.
    max_workers: int
        Maximum number of workers

    Returns
    -------
    Iterator
        an iterator over the downloaded paths, one for each download that have succeeded
    """

    def download_one(url):
        try:
            return http_single_download_with_retries(url, output_dir, retries,
                                                     backoff)
        except Exception as e:
            warnings.warn(f'Failed to download {url}: {e}')
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(download_one, url): url
            for url in urls
        }

        for future in as_completed(future_to_url):
            result = future.result()
            if result:
                yield result
