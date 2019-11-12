from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def create_type(inputstr: str):
    """ 
    Creating entity type of measurement based on datamodel and substring
    search in given string.
    :param string: input string for processing
    :return: entity_type
    """
    datamodel={"sensor:temperature":["temp"," t"],
               "sensor:pressure":["pres","druck"],
               "sensor:volumeflow":[" v","vol"," v dot"],
               "sensor:co2":['co2', "co_2"],
               "sensor:voc":['voc','volatile organic compounds'],
               "sensor:humidity":['hum','humidity','rh','rel_'],
               "actuator:valve":['valv',"vent","ventil"],
               "actuator:pump":['pump','pumpe'],
               "actuator:switch":['switch'],
               "control:pid":["pid-"],
               "actuator:flap":["flap","klappe"],
               "room:window":["fenster","jalousie", "window"],
               "room:door":["tuer","door"],
               "status":["status"]}
    max_ratio = 0
    max_ratio_entitytype = ""
    max_partial = 0
    max_partial_entitytype = ""
    number_of_max = 0
    inputstr = inputstr.lower()
    for key in datamodel.keys():
        for elem in datamodel[key]:
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
    else:
        print("max partial ratio = " + str(max_partial))
        return max_partial_entitytype


def str2fiware(string:str):
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
    chars_to_replace = {"<":"",
                        ">":"",
                        '"':"",
                        "'":"",
                        "=":"_eq_",
                        ";":" ",
                        "(":"",
                        ")":""}
    for char, replacement in chars_to_replace.items():
        string = string.replace(char, replacement).strip()
    return string
