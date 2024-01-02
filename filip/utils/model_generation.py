"""
Code generator for data models from schema.json descriptions
"""
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union, Dict, Any, Type
from urllib import parse
from uuid import uuid4
from datamodel_code_generator import InputFileType, generate, ParseResult
from pydantic import create_model

from filip.models.ngsi_v2.context import ContextAttribute, ContextEntity


def create_data_model_file(*,
                           path: Union[Path, str],
                           url: str = None,
                           schema: Union[Path, str, ParseResult] = None,
                           schema_type: Union[str, InputFileType] =
                     InputFileType.JsonSchema,
                           class_name: str = None
                           ) -> None:
    """
    This will create a data model from data model definitions. The schemas
    can either downloaded from a url or passed as str or dict. Allowed input
    types are defined but the underlying toolbox.

    Many data models suited for FIWARE are located here:
    https://github.com/smart-data-models/data-models

    Args:
        path:
            path where the generated code should saved
        url:
            url to download the definition from
        schema_type (str):
            `auto`, `openapi`, `jsonschema`, `json`, `yaml`, `dict`, `csv`
        class_name:
            classname for the model class

    Returns:
        None

    Examples::

        {
            "type": "object",
            "properties": {
                "number": {
                    "type": "number"
                    },
                "street_name": {
                    "type": "string"
                   },
                "street_type": {
                    "type": "string",
                    "enum": ["Street", "Avenue", "Boulevard"]
                }
            }
        }
    """
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(schema_type, str):
        schema_type = InputFileType(schema_type)

    with TemporaryDirectory() as temp:
        temp = Path(temp)
        output = Path(temp).joinpath(f'{uuid4()}.py')

        if url:
            schema = parse.urlparse(url)
        if not schema:
            raise ValueError("Missing argument! Either 'url' or 'schema' "
                             "must be provided")

        generate(
            input_=schema,
            input_file_type=schema_type,
            output=output,
            class_name=class_name)

        # move temporary file to output directory
        shutil.move(str(output), str(path))


def create_context_entity_model(name: str = None,
                                data: Dict = None,
                                validators: Dict[str, Any] = None,
                                path: Union[Path, str] = None) -> \
        Type['ContextEntity']:
    r"""
    Creates a ContextEntity-Model from a dict:

    Args:
        name:
            name of the model
        data:
            dictionary containing the data structure
        validators (optional):
            validators for the new model
        path:
            if present the model will written to *.py file if file ending
            *.py is used and to json-schema if *.json is used.

    Example:

        >>> def username_alphanumeric(cls, value):
                assert v.value.isalnum(), 'must be numeric'
                return value

        >>> model = create_context_entity_model(
                        name='MyModel',
                        data={
                            'id': 'MyId',
                            'type':'MyType',
                            'temp': 'MyProperty'}
                        {'validate_test': validator('temperature')(
                            username_alphanumeric)})

    Returns:
        ContextEntity

    """
    properties = {key: (ContextAttribute, ...) for key in data.keys() if
                  key not in ContextEntity.model_fields}
    model = create_model(
        __model_name=name or 'GeneratedContextEntity',
        __base__=ContextEntity,
        __validators__=validators or {},
        **properties
    )

    # if path exits a file will be generated that contains the model
    if path:
        if isinstance(path, str):
            path=Path(path)

        with TemporaryDirectory() as temp:
            temp = Path(temp)
            output = Path(temp).joinpath(f'{uuid4()}.json')
            output.touch(exist_ok=True)
            with output.open('w') as f:
                json.dump(model.model_json_schema(), f, indent=2)
            if path.suffix == '.json':
                # move temporary file to output directory
                shutil.move(str(output), str(path))
            elif path.suffix == '.py':
                create_data_model_file(path=path,
                                       schema=output,
                                       class_name=name)
    return model
