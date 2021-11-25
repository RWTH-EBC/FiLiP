"""
Code generator for data models from schema.json descriptions
"""
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union, Dict
from urllib import parse
from datamodel_code_generator import InputFileType, generate


def create_datamodel(*,
                     output_path: Union[str, Path],
                     filename: str,
                     url: str = None,
                     schema: Union[str, Dict] = None,
                     schema_type: Union[str, InputFileType] =
                     InputFileType.JsonSchema,
                     class_name: str = None
                     ) -> None:
    """
    This will create a data model from data model definitions. The schemas
    can either downloaded from a url or passed as str or dict. Allowed input
    types are defined but the underlying toolbox.

    Many datamodels suited for FIWARE are located here:
    https://github.com/smart-data-models/data-models

    Args:
        output_path: path where the generated code should saved
        filename: package_name for the generated code
        url: url to download the definition from
        schema_type (str): auto, openapi, 'jsonschema', 'json', 'yaml',
            'dict', 'csv'
        class_name: dummy

    Returns:
        None

    Examples::

        {"type": "object",
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
    if isinstance(output_path, str):
        output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    if isinstance(schema_type, str):
        schema_type = InputFileType(schema_type)

    with TemporaryDirectory() as temp:
        temp = Path(temp)
        output = Path(temp).joinpath('model.py')
        #with open(temp.joinpath('schema.json'), 'wb') as f:
        #    f.write(r.content)

        #input = temp.joinpath('schema.json')
        if url:
            schema=parse.urlparse(url)
        if not schema:
            raise ValueError("Missing argument! Either 'url' or 'schema' "
                             "must be provided")

        generate(
            input_=schema,
            input_file_type=schema_type,
            output=output,
            class_name=class_name)

        # move temporary file to output directory
        filepath = path.joinpath(filename)
        shutil.move(str(output), str(filepath))

if __name__ == '__main__':
    path = Path(os.getcwd()).joinpath("../models")
    create_datamodel(output_path=path,
                     filename='commons.py',
                     url='https://smart-data-models.github.io/data-models/'
                         'common-schema.json#/definitions/GSMA-Commons')
