#!/usr/bin/python3.6

import sys
import requests

#pip install ruamel.yaml
from ruamel.yaml import YAML

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

with open("eu.tiliado.NuvolaSdk.yaml") as fh:
  manifest = yaml.load(fh) 
  modules = manifest["modules"]

ENDPOINT = "https://release-monitoring.org/api/"

def get_project(session, project_id: int):
  response = session.get(f'{ENDPOINT}/project/{project_id}')
  response.raise_for_status()
  return response.json()

session = requests.Session()
needs_update = False

for module in modules:
  name = module["name"]
  project_id = module.get("x-anitya-id")
  module_version = module.get("x-version")
  if project_id:
    project = get_project(session, project_id)
    latest_version = project["version"]
    if latest_version != module_version:
      needs_update = True
      updated = False
      print(f'{name}: {module_version} → {latest_version}')
      for source in module["sources"]:
        url_pattern = source.get("x-url-pattern")
        if url_pattern:
          source["url"] = url_pattern.format(version=latest_version)
          updated = True
      if updated:
        module["x-version"] = latest_version


with open("eu.tiliado.NuvolaSdk.yaml~", "wt") as fh:
  yaml.default_flow_style = False
  yaml.dump(manifest, fh)

sys.exit(9 if needs_update else 0)
