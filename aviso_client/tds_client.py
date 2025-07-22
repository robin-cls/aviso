import os
import requests

import auth

TDS_HOST = 'tds-odatis.aviso.altimetry.fr'
TDS_BASE_URL = 'https://tds-odatis.aviso.altimetry.fr/thredds/fileServer'

def http_download(url: str, output_dir: str):
    (username, password) = auth.ensure_credentials(TDS_HOST)
    
    # download url and store file in output_dir
    response = requests.get(os.path.join(TDS_BASE_URL, url), auth=(username, password))

    filename = os.path.basename(url)
    local_filepath = os.path.join(output_dir, filename)
    
    if response.status_code == 200:
        with open(local_filepath, "wb") as f:
            f.write(response.content)
    else:
        print(f"Error {response.status_code} : {response.reason}")
    
    return local_filepath
