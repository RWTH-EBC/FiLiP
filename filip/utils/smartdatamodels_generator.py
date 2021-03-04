import os
import shutil
import requests
from pathlib import Path
from tempfile import TemporaryDirectory
from datamodel_code_generator import InputFileType, generate

json_schema: str = """{
    "type": "object",
    "properties": {
        "number": {"type": "number"},
        "street_name": {"type": "string"},
        "street_type": {"type": "string",
                        "enum": ["Street", "Avenue", "Boulevard"]
                        }
    }
}"""

if __name__ == '__main__':
    path = Path(os.getcwd()).joinpath("../datamodels")
    path.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as temp:
        temp = Path(temp)
        url = 'https://json.schemastore.org/grafana-dashboard-5.x'
        r = requests.get(url)
        with open(temp.joinpath('schema.json'), 'wb') as f:
            f.write(r.content)
        output = Path(temp).joinpath('model.py')
        #input = Path(os.getcwd())
        input = temp.joinpath('schema.json')
        generate(
            input_=input,
            input_file_type=InputFileType.JsonSchema,
            #input_filename="schema-example.json",
            output=output,
            class_name='Grafana_Dashboard_5x'
        )
        filename = path.joinpath('grafana_dashboard.py')
        shutil.move(str(output), str(filename))

