import os
import logging
from pathlib import Path
from typing import Dict
import pandas as pd
from pandas_datapackage_reader import read_datapackage
from filip.utils.validators import validate_url

logger = logging.getLogger(__name__)


def load_datapackage(url: str, filename: str) -> Dict[str, pd.DataFrame]:
    """
    Downloads data package from online source and stores it as hdf-file in
    filip.data named by the <filename>.hdf.
    Args:
        url (str): Valid url to where the data package is hosted
        filename (str): name of the cached file.
    Returns:
        Dict of dataframes
    """
    # validate arguments
    validate_url(url=url)
    assert filename.endswith('.hdf'), "Filename must end with '.hdf'"

    # create directory for data if not exists
    validate_url(url=url)
    path = Path(__file__).parent.parent.absolute().joinpath('data')
    path.mkdir(parents=True, exist_ok=True)
    filepath = path.joinpath(filename)


    if os.path.isfile(filepath):
        # read data from filip.data if exists
        logger.info("Found existing data package in 'filip.data'")
        with pd.HDFStore(str(filepath)) as store:
            keys = [k.strip('/') for k in store.keys()]
        data = {k: pd.read_hdf(str(filepath), key=k) for k in keys}
    else:
        # download external data and store data
        logger.info("Could not find data package in 'filip.data'. Will "
                    "try to download from %s", url)
        try:
            data = read_datapackage(url)
            # rename keys
            data = {k.replace('-', '_'): v for k, v in data.items()}

            # store data in filip.data
            for k, v in data.items():
                v.loc[:, :] = v[:].applymap(str)
                v.to_hdf(str(filepath), key=k)
        except:
            logger.error("Failed to load data package!")
            raise
    return data
