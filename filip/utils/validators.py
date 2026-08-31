"""
Helper functions to prohibit boiler plate code
"""

import logging
import re
import warnings
from aenum import Enum
from typing import Dict, Any, List, Union
from pydantic import AnyHttpUrl, validate_call
from pydantic_core import PydanticCustomError
from filip.custom_types import AnyMqttUrl, AnyKafkaUrl
from pyjexl.jexl import JEXL
from pyjexl.parser import Transform
from pyjexl.exceptions import ParseError

logger = logging.getLogger(name=__name__)


class FiwareRegex(str, Enum):
    """
    Collection of Regex expression used to check if the value of a Pydantic
    field, can be used in the related Fiware field. The regexes here are primarily
    defined based on the identifiers syntax restriction:
    https://fiware-orion.readthedocs.io/en/stable/orion-api.html#identifiers-syntax-restrictions
    """

    _init_ = "value __doc__"
    #  Identifiers syntax restriction
    standard = (
        r"(^((?![?&#/\"' ])[\x00-\x7F])*$)",
        "Prevents any string that contains at least one of the "
        "symbols: ? & # / ' \" or a whitespace",
    )
    string_protect = (
        r"(?!^id$)(?!^type$)(?!^geo:json$)(^((?![?&#/\"' ])[\x00-\x7F])*$)",
        "Prevents any string that contains at least one of "
        "the symbols: ? & # / ' \" or a whitespace."
        "AND the strings: id, type, geo:json",
    )
    attribute_name = (
        r"(?!^id$)(?!^type$)(?!^geo:json$)(^((?![\"'<>()=; §&/#?])[\x00-\x7F])*$)",
        "Prevents any string that contains at least one of the "
        "symbols: ( ) < > \" ' = ; § & / # ?",
    )
    attribute_value = (
        r"(^((?![\"'<>()=;]).)*$)",
        "Prevents any string that contains at least one of the "
        "symbols: ( ) < > \" ' = ; ",
    )


class KafkaSaslMechanism(str, Enum):
    """
    SASL mechanisms that Orion supports for Kafka notifications
    """

    _init_ = "value __doc__"

    PLAIN = "PLAIN", "Credentials are sent as plain text"
    SCRAM_SHA_256 = "SCRAM-SHA-256", "Salted challenge response using SHA-256"
    SCRAM_SHA_512 = "SCRAM-SHA-512", "Salted challenge response using SHA-512"


class KafkaSecurityProtocol(str, Enum):
    """
    Security protocols that Orion supports for Kafka notifications
    """

    _init_ = "value __doc__"

    SASL_PLAINTEXT = "SASL_PLAINTEXT", "SASL authentication over an unencrypted channel"
    SASL_SSL = "SASL_SSL", "SASL authentication over an SSL encrypted channel"


@validate_call
def validate_http_url(url: AnyHttpUrl) -> str:
    """
    Function checks whether the host has "http" added in case of http as
    protocol.

    Args:
        url (AnyHttpUrl): the url for the host / port

    Returns:
        validated url
    """
    url = str(url) if url else url
    if url[-1] != "/":
        # add trailing slash
        url = f"{url}/"
    return url


@validate_call
def validate_mqtt_url(url: AnyMqttUrl) -> str:
    """
    Function that checks whether a url is valid mqtt endpoint

    Args:
        url: the url for the target endpoint

    Returns:
       validated url
    """
    return str(url) if url else url


@validate_call
def validate_kafka_broker_url(url: AnyKafkaUrl) -> str:
    """
    Function that checks whether a url is a valid endpoint of a single kafka
    broker

    Args:
        url: the url for the target broker

    Returns:
       validated url
    """
    return str(url) if url else url


def validate_kafka_url(url: Union[AnyKafkaUrl, str]) -> str:
    """
    Function that checks whether a url is a valid kafka endpoint

    A subscription may address a whole kafka cluster. In that case the url
    contains the endpoints of multiple brokers as a comma separated list,
    where only the leading one carries the scheme, e.g.
    ``kafka://broker1:9092,broker2:9092``.

    Args:
        url: the url for the target endpoint

    Returns:
       validated url
    """
    if not url:
        return url

    brokers = [broker.strip() for broker in str(url).split(",")]
    # all brokers belong to the same cluster, hence they share the scheme of
    # the leading one
    validated = [
        validate_kafka_broker_url(
            url=broker if "://" in broker else f"kafka://{broker}"
        ).removeprefix("kafka://")
        for broker in brokers
    ]
    return f"kafka://{','.join(validated)}"


def validate_escape_character_free(value: Any) -> Any:
    """
    Function that checks whether a value contains a string part that starts
    or end with ' or ".
    the function iterates to break down each complex data-structure to its
    fundamental string parts.
    Each value of a list is examined
    Of dictionaries each value is examined, keys are skipped, as they are ok
    for Fiware

    Args:
        value: the string to check

    Returns:
       validated string
    """

    if not isinstance(value, List):
        values = [value]
    else:
        values = value

    for value in values:
        if isinstance(value, Dict):
            for key, dict_value in value.items():
                validate_escape_character_free(dict_value)
                # it seems Fiware has no problem if the keys contain ' or "
                # validate_escape_character_free(key)
        elif isinstance(value, List):
            for inner_list in value:
                validate_escape_character_free(inner_list)
        else:
            # if a value here is not a string, it will also not contain ' or "
            value = str(value)
            if '"' == value[-1:] or '"' == value[0:1]:
                raise ValueError(f"The value {value} contains " f'the forbidden char "')
            if "'" == value[-1:] or "'" == value[0:1]:
                raise ValueError(f"The value {value} contains " f"the forbidden char '")
    return values


def match_regex(value: str, pattern: str):
    regex = re.compile(pattern)
    if not regex.match(value):
        raise PydanticCustomError(
            "string_pattern_mismatch",
            "String should match pattern '{pattern}', [type='{error_type}', input_value='{value}']",
            {
                "pattern": pattern,
                "error_type": "string_pattern_mismatch",
                "value": value,
            },
        )
    return value


def ignore_none_input(func):
    def wrapper(arg):
        if arg is None:
            return arg
        return func(arg)

    return wrapper


def validate_fiware_standard_regex(vale: str):
    return match_regex(vale, FiwareRegex.standard.value)


def validate_fiware_string_protect_regex(vale: str):
    return match_regex(vale, FiwareRegex.string_protect.value)


def validate_fiware_attribute_value_regex(vale: str):
    return match_regex(vale, FiwareRegex.attribute_value.value)


def validate_fiware_attribute_name_regex(vale: str):
    return match_regex(vale, FiwareRegex.attribute_name.value)


@ignore_none_input
def validate_mqtt_topic(topic: str):
    return match_regex(topic, r"^((?![\'\"#+,])[\x00-\x7F])*$")


@ignore_none_input
def validate_kafka_topic(topic: str):
    """
    Function that checks whether a topic is a valid kafka topic name

    Kafka restricts topic names to the characters ``a-z``, ``A-Z``, ``0-9``,
    ``.``, ``_`` and ``-``. Additionally, a topic must not be named ``.`` or
    ``..``. The maximum length of 249 characters is enforced by the model
    fields.

    Args:
        topic: the topic to validate

    Returns:
       validated topic
    """
    return match_regex(topic, r"^(?!\.{1,2}$)[a-zA-Z0-9._\-]+$")


@ignore_none_input
def validate_kafka_topic_template(topic: str):
    """
    Function that checks whether a topic is a valid kafka topic name template

    In custom notifications, macro replacement based on the syntax
    ``${<JEXL expression>}`` is performed for the topic. Hence, next to the
    characters allowed in a plain kafka topic name, macros are accepted here.
    Note that the resulting topic name is only known at notification time,
    therefore neither its length nor the characters contributed by the macros
    can be checked upfront.

    Args:
        topic: the topic template to validate

    Returns:
       validated topic template
    """
    return match_regex(topic, r"^(?!\.{1,2}$)(?:[a-zA-Z0-9._\-]|\$\{[^{}]+\})+$")


@ignore_none_input
def validate_fiware_datatype_standard(_type):
    from filip.models.base import DataType

    if isinstance(_type, DataType):
        return _type
    elif isinstance(_type, str):
        return validate_fiware_standard_regex(_type)
    else:
        raise TypeError(f"Invalid type {type(_type)}")


@ignore_none_input
def validate_fiware_datatype_string_protect(_type):
    from filip.models.base import DataType

    if isinstance(_type, DataType):
        return _type
    elif isinstance(_type, str):
        return validate_fiware_string_protect_regex(_type)
    else:
        raise TypeError(f"Invalid type {type(_type)}")


@ignore_none_input
def validate_fiware_service_path(service_path):
    return match_regex(service_path, r"^((\/\w*)|(\/\#))*(\,((\/\w*)|(\/\#)))*$")


@ignore_none_input
def validate_fiware_service(service):
    return match_regex(service, r"\w*$")


jexl_transformation_functions = {
    "jsonparse": "(str) => JSON.parse(str)",
    "jsonstringify": "(obj) => JSON.stringify(obj)",
    "indexOf": "(val, char) => String(val).indexOf(char)",
    "length": "(val) => String(val).length",
    "trim": "(val) => String(val).trim()",
    "substr": "(val, int1, int2) => String(val).substr(int1, int2)",
    "addreduce": "(arr) => arr.reduce((i, v) => i + v)",
    "lengtharray": "(arr) => len(arr)",
    "typeof": "(val) => typeof val",
    "isarray": "(arr) => Array.isArray(arr)",
    "isnan": "(val) => isNaN(val)",
    "parseint": "(val) => parseInt(val)",
    "parsefloat": "(val) => parseFloat(val)",
    "toisodate": "(val) => new Date(val).toISOString()",
    "timeoffset": "(isostr) => new Date(isostr).getTimezoneOffset()",
    "tostring": "(val) => str(val)",
    "urlencode": "(val) => encodeURI(val)",
    "urldecode": "(val) => decodeURI(val)",
    "replacestr": "(str, from, to) => str.replace(from, to)",
    "replaceregexp": "(str, reg, to) => str.replace(reg, to)",
    "replaceallstr": "(str, from, to) => str.replace(from, to)",
    "replaceallregexp": "(str, reg, to) => str.replace(reg, to)",
    "split": "(str, ch) => str.split(ch)",
    "mapper": "(val, values, choices) => choices[values.index(val)]",
    "thmapper": "(val, values, choices) => choices[next((i for i, v in enumerate(values) if val <= v), None)]",
    "bitwisemask": "(i, mask, op, shf) => ((int(i) & mask) if op == '&' else ((int(i) | mask) if op == '|' else ((int(i) ^ mask) if op == '^' else int(i))) >> shf)",
    "slice": "(arr, init, end) => arr[init:end]",
    "addset": "(arr, x) => list(set(arr).add(x))",
    "removeset": "(arr, x) => list(set(arr).remove(x))",
    "touppercase": "(val) => str(val).upper()",
    "tolowercase": "(val) => str(val).lower()",
}


def validate_jexl_expression(expression, attribute_name, device_id):
    try:
        jexl_expression = JEXL().parse(expression)
        if isinstance(jexl_expression, Transform):
            if jexl_expression.name not in jexl_transformation_functions.keys():
                warnings.warn(f"{jexl_expression.name} might not supported")
    except ParseError:
        msg = f"Invalid JEXL expression '{expression}' inside the attribute '{attribute_name}' of Device '{device_id}'."
        if "|" in expression:
            msg += " If the expression contains the transform operator '|' you need to remove the spaces around it."
        raise ParseError(msg)
    return expression


def validate_expression_language(cls, expressionLanguage):
    if expressionLanguage == "legacy":
        warnings.warn(
            f"Using 'LEGACY' expression language inside {cls.__name__} is "
            f"deprecated. Use 'JEXL' instead."
        )
    elif expressionLanguage is None:
        expressionLanguage = "jexl"
    return expressionLanguage
