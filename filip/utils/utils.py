"""
utility functions
"""
from fuzzywuzzy import fuzz


def create_type(inputstr: str):
    """
    Creating entity type of measurement based on datamodel and substring
    search in given string.
    :param inputstr: input string for processing
    :return: entity_type - the respective entitytype
    """
    datamodel = {"sensor:temperature": ["temp", " t"],
                 "sensor:pressure": ["pres", "druck"],
                 "sensor:volumeflow": [" v", "vol", " v dot"],
                 "sensor:co2": ['co2', "co_2"],
                 "sensor:voc": ['voc', 'volatile organic compounds'],
                 "sensor:humidity": ['hum', 'humidity', 'rh', 'rel_'],
                 "actuator:valve": ['valv', "vent", "ventil"],
                 "actuator:pump": ['pump', 'pumpe'],
                 "actuator:switch": ['switch'],
                 "control:pid": ["pid-"],
                 "actuator:flap": ["flap", "klappe"],
                 "room:window": ["fenster", "jalousie", "window"],
                 "room:door": ["tuer", "door"],
                 "status": ["status"]}
    max_ratio = 0
    max_ratio_entitytype = ""
    max_partial = 0
    max_partial_entitytype = ""
    number_of_max = 0
    inputstr = inputstr.lower()
    for key, value in datamodel.items():
        for elem in value:
            ratio = fuzz.ratio(inputstr, elem)
            partial_ratio = fuzz.partial_ratio(inputstr, elem)
            if ratio > max_ratio:
                max_ratio_entitytype = key
                max_ratio = ratio
            if partial_ratio > max_partial:
                number_of_max += 1
                max_partial_entitytype = key
                max_partial = partial_ratio
    if number_of_max > 1:
        print("max ratio = " + str(max_ratio))
        return max_ratio_entitytype
    print("max partial ratio = " + str(max_partial))
    return max_partial_entitytype

# Todo this hosuld be converted to a regular expresion string
def str2fiware(string: str):
    """
    Fiware does not support all characters.
    Converting provided string according to Fiware specifications. The mapping
    for character replacement can be provided as dict. If no mapping is
    provided the default library mapping will be used. For list of forbidden
    characters see
    https://fiware-orion.readthedocs.io/en/master/user/forbidden_characters/index.html
    :param string: str string for conversion according to Fiware specifications
    :param: dict mapping for character replacement
    :return: str converted string
    """
    chars_to_replace = {"<": "",
                        ">": "",
                        '"': "",
                        "'": "",
                        "=": "_eq_",
                        ";": " ",
                        "(": "",
                        ")": "",
                        "ä": "ae",
                        "ö": "oe",
                        "ü": "ue",
                        "ß": "ss"
                        }
    for char, replacement in chars_to_replace.items():
        string = string.replace(char, replacement).strip()
    return string

#deprecated
#def timeseries_to_pandas(ts_dict: dict,
#                         to_datetime: bool = False,
#                         datetime_format: str = "%Y-%m-%dT%H:%M:%S.%f"):
#    """
#    :param ts_dict: ts_dict: a dictionary with the following structure:
#        {attr_name_0 : { timestamp_0 : value_0, timestamp_1: value_1 },
#        sattr_name_1 : { timestamp_0 : value_0, timestamp_1: value_1 } }
#    :param to_datetime: Whether the "timestamp" column should be converted to
#        a datetime object
#    :param datetime_format: the datetime format which is recived from
#        Quantumleap "%Y-%m-%dT%H:%M:%S.%f"
#    :return: a pandas dataframe object, containting one timestamp column
#        and minimum one attribute column
#    """
#    list_of_dataframes = []
#    column_names = [key for key, value in ts_dict.items()]
#    for attr in column_names:
#        dataframe = pd.DataFrame(ts_dict[attr].items(),
#                                 columns=["timestamp", attr])
#        list_of_dataframes.append(dataframe)
#    df_all = pd.concat(list_of_dataframes, ignore_index=True)
#    df_all.sort_values(by='timestamp', inplace=True)
#    if to_datetime is True:
#        pd.to_datetime(df_all['timestamp'], format=datetime_format)
#    return df_all
