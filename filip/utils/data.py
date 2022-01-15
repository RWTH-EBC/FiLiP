import os
import importlib
import logging
from pathlib import Path
import pickle
from typing import Dict
import pandas as pd
from pandas import DataFrame
from pandas_datapackage_reader import read_datapackage
from filip.utils.validators import validate_http_url

logger = logging.getLogger(__name__)


def load_datapackage(url: str, package_name: str) -> Dict[str, pd.DataFrame]:
    """
    Downloads data package from online source and stores it as hdf-file in
    filip.data named by the <filename>.hdf.

    Args:
        url (str): Valid url to where the data package is hosted
        package_name (str): name of the cached file.

    Returns:
        Dict of dataframes
    """
    # validate arguments
    validate_http_url(url=url)

    # create directory for data if not exists
    validate_http_url(url=url)
    path = Path(__file__).parent.parent.absolute().joinpath('data')
    path.mkdir(parents=True, exist_ok=True)
    package_path = path.joinpath(package_name)

    if os.path.isdir(package_path):
        # read data from filip.data if exists
        logger.info("Found existing data package in 'filip.data'")

        data = {}
        for file in os.listdir(package_path):
            file_name = file[:-4]
            # read in each file as one dataframe, prevents the deletion of NaN
            # values with na_filter=False
            frame = pd.read_csv(package_path.joinpath(file),
                                index_col=0,
                                header=0,
                                na_filter=False)
            data[file_name] = frame

    else:
        # download external data and store data
        logger.info("Could not find data package in 'filip.data'. Will "
                    "try to download from %s", url)
        try:
            data = read_datapackage(url)
            # rename keys
            data = {k.replace('-', '_'): v for k, v in data.items()}
            os.mkdir(package_path)

            # store data in filip.data
            for k, v in data.items():
                v: DataFrame = v
                v.loc[:, :] = v[:].applymap(str)
                table_filepath = \
                    str(package_path) + f"\\{k.replace('-', '_')}.csv"
                v.to_csv(table_filepath)

        except:
            logger.error("Failed to load data package!")
            raise
    return data
