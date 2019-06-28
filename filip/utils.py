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

