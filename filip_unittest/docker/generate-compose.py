import sys
from jinja2 import Environment, FileSystemLoader

orion_version = sys.argv[1]
iot_json_version = sys.argv[2]

env = Environment(loader=FileSystemLoader("."))
template = env.get_template("docker-compose.yml.j2")

config = template.render(orion_version=orion_version, iot_json_version=iot_json_version)

with open("docker-compose.yml", "w") as f:
    f.write(config)
