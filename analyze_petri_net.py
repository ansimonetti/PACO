#!/usr/bin/env python3
import json
import sys
sys.path.append('simulator/src')
sys.path.append('src')
import requests

URL = "0.0.0.0"
SIMULATOR_PORT = 8001
SOLVER_PORT = 8000
HEADERS = {"Content-Type": "application/json"}

# Load BPMN
with open("bpmn_fig8_bound_135_15.json", "r") as f:
    bpmn_definition = json.load(f)

# Create parse tree
resp = requests.get(f"http://{URL}:{SOLVER_PORT}/create_parse_tree", 
                  json={'bpmn': bpmn_definition}, headers=HEADERS)
resp.raise_for_status()
parse_tree = resp.json()['parse_tree']

# Bootstrap simulator
request_json = {"bpmn": parse_tree}
response = requests.post(f"http://{URL}:{SIMULATOR_PORT}/execute", headers=HEADERS, json=request_json)
response_json = response.json()

petri_net = response_json['petri_net']
transitions = petri_net.get("transitions", [])

print("=" * 60)
print("PETRI NET TRANSITIONS ANALYSIS")
print("=" * 60)
print(f"\nTotal transitions: {len(transitions)}")

if isinstance(transitions, list):
    for i, trans in enumerate(transitions):
        trans_name = trans.get("name", f"t_{i}")
        has_stop = trans.get("stop", False)
        inputs = trans.get("inputs", [])
        outputs = trans.get("outputs", [])
        print(f"\n{trans_name}:")
        print(f"  stop: {has_stop}")
        print(f"  inputs: {inputs}")
        print(f"  outputs: {outputs}")
        if has_stop:
            print(f"  >>> CHOICE/NATURE TRANSITION <<<")
else:
    for trans_name, trans_data in transitions.items():
        has_stop = trans_data.get("stop", False)
        inputs = trans_data.get("inputs", [])
        outputs = trans_data.get("outputs", [])
        print(f"\n{trans_name}:")
        print(f"  stop: {has_stop}")
        print(f"  inputs: {inputs}")
        print(f"  outputs: {outputs}")
        if has_stop:
            print(f"  >>> CHOICE/NATURE TRANSITION <<<")

print("\n" + "=" * 60)
