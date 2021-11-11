import os
import importlib
import logging
from pathlib import Path
import pickle
from typing import Dict
import pandas as pd
from pandas_datapackage_reader import read_datapackage
from filip.utils.validators import validate_http_url

logger = logging.getLogger(__name__)


class PickleProtocolManager:
    """
    Context Manager for pickle protocol
    https://stackoverflow.com/questions/60067953/is-it-possible-to-specify-the-pickle-protocol-when-writing-pandas-to-hdf5
    """
    def __init__(self, level: int):
        """
        Initilize with protocol level
        Args:
            level: level of pickle portocol
        """
        self.previous = pickle.HIGHEST_PROTOCOL
        assert level <= self.previous, f"According to your python version " \
                                       f"the max protocol level is: " \
                                       f"{self.previous}"
        self.level = level

    def __enter__(self):
        importlib.reload(pickle)
        pickle.HIGHEST_PROTOCOL = self.level

    def __exit__(self, *exc):
        importlib.reload(pickle)
        pickle.HIGHEST_PROTOCOL = self.previous


def pickle_protocol(level: int) -> PickleProtocolManager:
    """
    Caller for pickle protocol handler

    Args:
        level: int

    Returns:
        Protocol Handler
    """
    return PickleProtocolManager(level)


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
    validate_http_url(url=url)
    assert filename.endswith('.hdf'), "Filename must end with '.hdf'"

    # create directory for data if not exists
    validate_http_url(url=url)
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
                with pickle_protocol(4):
                    v.to_hdf(str(filepath), key=k)
        except:
            logger.error("Failed to load data package!")
            raise
    return data
