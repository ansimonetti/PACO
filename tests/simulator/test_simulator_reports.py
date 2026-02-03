"""
Test report generator for simulator tests.
Generates markdown files with BPMN and Petri Net visualizations at each step.
Uses EXISTING API endpoint /create_bpmn for BPMN rendering (as shown in tutorial.ipynb).
"""
import pytest
import os
import subprocess
import requests
from pathlib import Path

from fastapi.testclient import TestClient
from lark import Lark
from main import api

# Import paco utilities
from src.utils.env import EXPRESSION, IMPACTS, DURATIONS, IMPACTS_NAMES, PROBABILITIES, DELAYS, LOOP_PROBABILITY, LOOP_ROUND

REPORTS_DIR = Path(__file__).parent.parent / "reports" / "simulator_steps"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# API URL for BPMN generation
API_URL = "http://127.0.0.1:8000/"

sese_diagram_grammar = r'''
?start: xor
?xor: parallel | xor "/" "[" NAME "]" parallel -> choice | xor "^" "[" NAME "]" parallel -> natural
?parallel: sequential | parallel "||" sequential  -> parallel
?sequential: region | sequential "," region -> sequential    
?region: NAME -> task | "<" xor ">" -> loop | "<" "[" NAME "]"  xor ">" -> loop_probability | "(" xor ")"
%import common.CNAME -> NAME
%import common.WS_INLINE
%ignore WS_INLINE
'''

SESE_PARSER = Lark(sese_diagram_grammar, parser='lalr')
client = TestClient(api)


def petri_net_to_dot(petri_net, marking=None, title="Petri Net"):
    places = petri_net.get("places", [])
    transitions = petri_net.get("transitions", [])
    arcs = petri_net.get("arcs", [])
    
    mark_dict = {}
    if marking:
        for pid, info in marking.items():
            if info.get("token", 0) > 0:
                mark_dict[str(pid)] = info.get("token", 0)
    
    lines = ['digraph G {', '  rankdir=LR;', f'  label="{title}";', '  labelloc=t;', '  node [fontsize=10];', '']
    
    for p in places:
        pid = str(p["id"])
        label = p.get("label", pid)
        ptype = p.get("region_type", "")
        tokens = mark_dict.get(pid, 0)
        token_str = "●" * tokens if tokens > 0 else ""
        
        if ptype in ("choice", "nature"):
            color = "orange" if ptype == "choice" else "lightgreen"
            lines.append(f'  p{pid} [shape=circle, label="{label}\\n{token_str}", style=filled, fillcolor={color}];')
        elif ptype == "task":
            color = "yellow" if tokens > 0 else "lightblue"
            lines.append(f'  p{pid} [shape=circle, label="{label}\\n{token_str}", style=filled, fillcolor={color}];')
        else:
            lines.append(f'  p{pid} [shape=circle, label="{label}\\n{token_str}"];')
    
    for t in transitions:
        tid = str(t["id"])
        label = t.get("label", tid)
        stop = t.get("stop", False)
        color = "red" if stop else "black"
        lines.append(f'  t{tid} [shape=box, label="{label}", color={color}];')
    
    lines.append('')
    
    for a in arcs:
        src, tgt = str(a["source"]), str(a["target"])
        is_src_place = any(str(p["id"]) == src for p in places)
        if is_src_place:
            lines.append(f'  p{src} -> t{tgt};')
        else:
            lines.append(f'  t{src} -> p{tgt};')
    
    lines.append('}')
    return '\n'.join(lines)


def dot_to_png(dot_content, output_path):
    try:
        subprocess.run(['dot', '-Tpng', '-o', str(output_path)], input=dot_content.encode(), capture_output=True, timeout=10)
        return True
    except:
        return False


class ReportGenerator:
    def __init__(self, test_name, expression, forced_decisions, config):
        self.test_name = test_name
        self.expression = expression
        self.forced_decisions = forced_decisions
        self.config = config
        self.steps = []
        self.report_dir = REPORTS_DIR / test_name
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.bpmn_generated = False
        
    def generate_bpmn_image(self):
        """Generate BPMN diagram using existing paco methods directly."""
        from src.paco.parser.bpmn_parser import create_parse_tree as paco_create_parse_tree
        from src.paco.parser.dot.bpmn import get_bpmn_dot_from_parse_tree
        
        durations = self.config.get(DURATIONS, {})
        probabilities = self.config.get(PROBABILITIES, {})
        delays = self.config.get(DELAYS, {})
        
        # Build BPMN config for paco parser
        bpmn_config = {
            EXPRESSION: self.expression,
            IMPACTS: {name: [0.0] for name in durations.keys()},
            DURATIONS: durations,
            IMPACTS_NAMES: ['impact'],
            PROBABILITIES: probabilities,
            DELAYS: delays,
            LOOP_PROBABILITY: self.config.get(LOOP_PROBABILITY, {}),
            LOOP_ROUND: self.config.get(LOOP_ROUND, {}),
            'h': 0,  # Required by create_parse_tree
        }
        
        try:
            # Create parse tree and generate BPMN DOT using existing method
            parse_tree, _, _, _ = paco_create_parse_tree(bpmn_config)
            bpmn_dot = get_bpmn_dot_from_parse_tree(parse_tree, bpmn_config[IMPACTS_NAMES], {})
            
            bpmn_dot_path = self.report_dir / "bpmn.dot"
            bpmn_png_path = self.report_dir / "bpmn.png"
            
            with open(bpmn_dot_path, 'w') as f:
                f.write(bpmn_dot)
            dot_to_png(bpmn_dot, bpmn_png_path)
            self.bpmn_generated = True
        except Exception as e:
            print(f"Warning: Could not generate BPMN: {e}")
            import traceback
            traceback.print_exc()
            self.bpmn_generated = False
        
    def add_step(self, step_num, petri_net, snapshot, choices_made=None, pn_dot=None):
        """Generate BPMN diagram with current status AND Petri Net with tokens at each step."""
        from src.paco.parser.bpmn_parser import create_parse_tree as paco_create_parse_tree
        from src.paco.parser.dot.bpmn import get_bpmn_dot_from_parse_tree
        
        exec_time = snapshot.get("execution_time", 0.0) if snapshot else 0.0
        status = snapshot.get("status", {}) if snapshot else {}
        # marking is used by server to generate pn_dot, so we don't need it here if we use pn_dot
        
        step_data = {"step": step_num, "time": exec_time, "choices_made": choices_made}

        # 1. Generate BPMN with status
        try:
            durations = self.config.get(DURATIONS, {})
            probabilities = self.config.get(PROBABILITIES, {})
            delays = self.config.get(DELAYS, {})
            
            bpmn_config = {
                EXPRESSION: self.expression,
                IMPACTS: {name: [0.0] for name in durations.keys()},
                DURATIONS: durations,
                IMPACTS_NAMES: ['impact'],
                PROBABILITIES: probabilities,
                DELAYS: delays,
                LOOP_PROBABILITY: self.config.get(LOOP_PROBABILITY, {}),
                LOOP_ROUND: self.config.get(LOOP_ROUND, {}),
                'h': 0,
            }
            
            parse_tree, _, _, _ = paco_create_parse_tree(bpmn_config)
            bpmn_dot = get_bpmn_dot_from_parse_tree(parse_tree, bpmn_config[IMPACTS_NAMES], status)
            
            bpmn_dot_path = self.report_dir / f"step_{step_num}_bpmn.dot"
            bpmn_png_path = self.report_dir / f"step_{step_num}_bpmn.png"
            
            with open(bpmn_dot_path, 'w') as f:
                f.write(bpmn_dot)
            dot_to_png(bpmn_dot, bpmn_png_path)
            step_data["bpmn_path"] = bpmn_png_path.name
        except Exception as e:
            print(f"Warning: Could not generate step BPMN: {e}")
            import traceback
            traceback.print_exc()

        # 2. Generate Petri Net with tokens (using server DOT if available)
        try:
            if pn_dot:
                # Post-process DOT to highlight active transitions
                # Petri Net from server does not show active transitions (tokens inside), so we color them manually
                # based on BPMN status.
                
                # 1. Identify active labels from status
                active_labels = set()
                # Map region_id to label using petri_net structure if possible, or just use label matching
                # The petri_net JSON has transitions with 'region_id' and 'label'.
                
                pn_transitions = petri_net.get("transitions", [])
                for t in pn_transitions:
                    rid = t.get("region_id") 
                    # status keys from JSON are usually strings, rid is usually int. Try both.
                    r_state = status.get(str(rid))
                    if r_state is None:
                        r_state = status.get(rid)
                    
                    # ActivityState.ACTIVE is 1. JSON might have 1 or "ACTIVE".
                    if r_state == 1 or r_state == "ACTIVE":
                        active_labels.add(t.get("label"))
                
                # 2. Patch the DOT
                import re
                modified_dot = pn_dot
                
                # Highlight Active Transitions
                if active_labels:
                    for label in active_labels:
                        escaped_label = re.escape(label)
                        pattern = r'(\d+)\s*\[.*?label\s*=\s*"?{}\"?[,\s\n\]]'.format(escaped_label)
                        match = re.search(pattern, modified_dot, re.DOTALL)
                        if match:
                            node_id = match.group(1)
                            style_line = f'\t{node_id} [style=filled, fillcolor=lightsalmon];\n'
                            modified_dot = modified_dot.rstrip()[:-1] + style_line + "}"
                
                pn_dot_path = self.report_dir / f"step_{step_num}_petri.dot"
                pn_png_path = self.report_dir / f"step_{step_num}_petri.png"
                
                with open(pn_dot_path, 'w') as f:
                    f.write(modified_dot)
                dot_to_png(modified_dot, pn_png_path)
                step_data["petri_path"] = pn_png_path.name
            else:
                pass # No DOT provided
        except Exception as e:
            print(f"Warning: Could not generate step Petri Net: {e}")
            import traceback
            traceback.print_exc()
            
        self.steps.append(step_data)
    
    def generate_report(self, final_time, expected_time, passed):
        md_path = self.report_dir / "report.md"
        with open(md_path, 'w') as f:
            f.write(f"# Test Report: {self.test_name}\n\n")
            f.write(f"**Expression:** `{self.expression}`\n\n")
            f.write(f"**Forced Decisions:** `{self.forced_decisions}`\n\n")
            f.write(f"**Expected Time:** {expected_time}  |  **Final Time:** {final_time}\n\n")
            f.write(f"**Result:** {'✅ PASSED' if passed else '❌ FAILED'}\n\n---\n\n")
            
            # BPMN Diagram section (Initial)
            if self.bpmn_generated:
                f.write(f"## Initial BPMN Diagram\n\n")
                f.write(f"![BPMN](bpmn.png)\n\n---\n\n")
            
            # Simulation steps
            f.write(f"## Simulation Steps\n\n")
            for s in self.steps:
                f.write(f"### Step {s['step']} (t={s['time']})\n")
                if s['choices_made']:
                    f.write(f"**Choices:** `{s['choices_made']}`\n\n")
                
                # Display nicely in a table or side-by-side if markdown supports it, or just sequentially
                f.write("| BPMN State | Petri Net Tokens |\n")
                f.write("| :---: | :---: |\n")
                
                bpmn_img = f"![BPMN]({s.get('bpmn_path', '')})" if s.get('bpmn_path') else "N/A"
                petri_img = f"![Petri]({s.get('petri_path', '')})" if s.get('petri_path') else "N/A"
                
                f.write(f"| {bpmn_img} | {petri_img} |\n\n")
        return md_path


class TestSimulatorReports:

    def get_bpmn_region(self, config):
        expression = config.get(EXPRESSION)
        durations = config.get(DURATIONS, {})
        delays = config.get(DELAYS, {})
        probabilities = config.get(PROBABILITIES, {})
        
        tree = SESE_PARSER.parse(expression)
        id_counter = [0]
        
        def norm_dur(val):
            return float(val[-1]) if isinstance(val, list) else float(val)
        
        def build(node, idx=0):
            nid = id_counter[0]
            id_counter[0] += 1
            
            if node.data == 'task':
                name = node.children[0].value
                return {"id": nid, "type": "task", "label": name, "index_in_parent": idx,
                        "duration": norm_dur(durations.get(name, 0)), "impacts": [0.0]}
            if node.data == 'sequential':
                return {"id": nid, "type": "sequential", "index_in_parent": idx,
                        "children": [build(node.children[0], 0), build(node.children[1], 1)]}
            if node.data == 'parallel':
                return {"id": nid, "type": "parallel", "index_in_parent": idx,
                        "children": [build(node.children[0], 0), build(node.children[1], 1)]}
            if node.data == 'choice':
                name = node.children[1].value
                return {"id": nid, "type": "choice", "label": name, "index_in_parent": idx,
                        "max_delay": float(delays.get(name, 0)),
                        "children": [build(node.children[0], 0), build(node.children[2], 1)]}
            if node.data == 'natural':
                name = node.children[1].value
                prob = probabilities.get(name, 0.5)
                return {"id": nid, "type": "nature", "label": name, "index_in_parent": idx,
                        "distribution": [float(prob), 1.0 - float(prob)],
                        "children": [build(node.children[0], 0), build(node.children[2], 1)]}
            if node.data == 'loop_probability':
                name = node.children[0].value
                return {"id": nid, "type": "loop", "label": name, "index_in_parent": idx,
                        "distribution": float(config.get(LOOP_PROBABILITY, {}).get(name, 0.5)),
                        "bound": int(config.get(LOOP_ROUND, {}).get(name, 3)),
                        "children": [build(node.children[1], 0)]}
            raise ValueError(f"Unknown: {node.data}")
        
        return build(tree)

    def find_choices(self, pn, snapshot, forced):
        arcs = pn.get("arcs", [])
        trans = {str(t["id"]): t for t in pn.get("transitions", [])}
        places = {str(p["id"]): p for p in pn.get("places", [])}
        marking = snapshot.get("marking", {})
        choices = []
        
        for pid, info in marking.items():
            if info.get("token", 0) <= 0:
                continue
            place = places.get(str(pid))
            if not place or place.get("region_type") not in ("choice", "nature"):
                continue
            label = place.get("label")
            if label not in forced:
                continue
            target = forced[label]
            for arc in arcs:
                if str(arc["source"]) != str(pid):
                    continue
                tid = str(arc["target"])
                if tid not in trans:
                    continue
                for arc2 in arcs:
                    if str(arc2["source"]) != tid:
                        continue
                    out = places.get(str(arc2["target"]))
                    if out and out.get("label") == target:
                        choices.append(tid)
                        break
        return choices

    def run_scenario(self, config, forced, expected, name):
        bpmn = self.get_bpmn_region(config)
        report = ReportGenerator(name, config.get(EXPRESSION), forced, config)
        
        # Generate BPMN image using existing API
        report.generate_bpmn_image()
        
        req = {"bpmn": bpmn, "time_step": 1.0}
        final = 0.0
        last = -1.0
        pending = []

        for step in range(50):
            if pending:
                req["choices"] = pending
            elif "choices" in req:
                del req["choices"]
            
            resp = client.post("/execute", json=req)
            assert resp.status_code == 200
            result = resp.json()
            
            pn = result.get("petri_net")
            pn_dot = result.get("petri_net_dot")  # Get server-generated DOT
            et = result.get("execution_tree")
            req["petri_net"] = pn
            req["execution_tree"] = et
            
            snapshot = None
            if et:
                curr = et.get("current_node")
                def find(n):
                    if n["id"] == curr: return n["snapshot"]
                    for c in n.get("children", []): 
                        r = find(c)
                        if r: return r
                    return None
                snapshot = find(et["root"])
            
            if snapshot:
                time = snapshot.get("execution_time", 0.0)
                # Pass server-generated DOT
                report.add_step(step, pn, snapshot, pending if pending else None, pn_dot=pn_dot)
                pending = self.find_choices(pn, snapshot, forced)
            else:
                time = 0.0
            
            if not pending:
                if time == last and time > 0:
                    final = time
                    break
                if time >= expected:
                    final = time
                    break
            last = time

        passed = final == expected
        report.generate_report(final, expected, passed)
        assert passed, f"Expected {expected}, got {final}"

    # ===== All Test Scenarios =====

    def test_01_sequential_tasks(self):
        self.run_scenario({EXPRESSION: "T1, T2", DURATIONS: {"T1": [0,1], "T2": [0,2]}}, {}, 3.0, "01_sequential_tasks")

    def test_02_seq_nature_task_T1(self):
        self.run_scenario({EXPRESSION: "(T1 ^ [N1] T2), T3", DURATIONS: {"T1": [0,1], "T2": [0,2], "T3": [0,2]}, PROBABILITIES: {"N1": 0.6}}, {"N1": "T1"}, 3.0, "02_seq_nature_T1")

    def test_02_seq_nature_task_T2(self):
        self.run_scenario({EXPRESSION: "(T1 ^ [N1] T2), T3", DURATIONS: {"T1": [0,1], "T2": [0,2], "T3": [0,2]}, PROBABILITIES: {"N1": 0.6}}, {"N1": "T2"}, 4.0, "02_seq_nature_T2")

    def test_03_seq_task_nature_T2(self):
        self.run_scenario({EXPRESSION: "T1, (T2 ^ [N1] T3)", DURATIONS: {"T1": [0,1], "T2": [0,2], "T3": [0,2]}, PROBABILITIES: {"N1": 0.5}}, {"N1": "T2"}, 3.0, "03_seq_task_nature_T2")

    def test_03_seq_task_nature_T3(self):
        self.run_scenario({EXPRESSION: "T1, (T2 ^ [N1] T3)", DURATIONS: {"T1": [0,1], "T2": [0,2], "T3": [0,2]}, PROBABILITIES: {"N1": 0.5}}, {"N1": "T3"}, 3.0, "03_seq_task_nature_T3")

    def test_04_seq_choice_task_T1(self):
        self.run_scenario({EXPRESSION: "(T1 / [C1] T2), T3", DURATIONS: {"T1": [0,1], "T2": [0,2], "T3": [0,2]}, DELAYS: {"C1": 1}}, {"C1": "T1"}, 4.0, "04_seq_choice_T1")

    def test_04_seq_choice_task_T2(self):
        self.run_scenario({EXPRESSION: "(T1 / [C1] T2), T3", DURATIONS: {"T1": [0,1], "T2": [0,2], "T3": [0,2]}, DELAYS: {"C1": 1}}, {"C1": "T2"}, 5.0, "04_seq_choice_T2")

    def test_05_seq_task_choice_T2(self):
        self.run_scenario({EXPRESSION: "T1, (T2 / [C1] T3)", DURATIONS: {"T1": [0,1], "T2": [0,2], "T3": [0,2]}, DELAYS: {"C1": 0}}, {"C1": "T2"}, 3.0, "05_seq_task_choice_T2")

    def test_05_seq_task_choice_T3(self):
        self.run_scenario({EXPRESSION: "T1, (T2 / [C1] T3)", DURATIONS: {"T1": [0,1], "T2": [0,2], "T3": [0,2]}, DELAYS: {"C1": 0}}, {"C1": "T3"}, 3.0, "05_seq_task_choice_T3")

    def test_06_seq_seq_nature_T3(self):
        self.run_scenario({EXPRESSION: "T1, T2, (T3 ^ [N1] T4)", DURATIONS: {"T1": [0,0], "T2": [0,1], "T3": [0,2], "T4": [0,3]}, PROBABILITIES: {"N1": 0.5}}, {"N1": "T3"}, 3.0, "06_seq_seq_nature_T3")

    def test_06_seq_seq_nature_T4(self):
        self.run_scenario({EXPRESSION: "T1, T2, (T3 ^ [N1] T4)", DURATIONS: {"T1": [0,0], "T2": [0,1], "T3": [0,2], "T4": [0,3]}, PROBABILITIES: {"N1": 0.5}}, {"N1": "T4"}, 4.0, "06_seq_seq_nature_T4")

    def test_07_seq_seq_choice_T3_d0(self):
        self.run_scenario({EXPRESSION: "T1, T2, (T3 / [C1] T4)", DURATIONS: {"T1": [0,0], "T2": [0,1], "T3": [0,2], "T4": [0,3]}, DELAYS: {"C1": 0}}, {"C1": "T3"}, 3.0, "07_seq_seq_choice_T3_d0")

    def test_07_seq_seq_choice_T4_d0(self):
        self.run_scenario({EXPRESSION: "T1, T2, (T3 / [C1] T4)", DURATIONS: {"T1": [0,0], "T2": [0,1], "T3": [0,2], "T4": [0,3]}, DELAYS: {"C1": 0}}, {"C1": "T4"}, 4.0, "07_seq_seq_choice_T4_d0")

    def test_07_seq_seq_choice_T3_d1(self):
        self.run_scenario({EXPRESSION: "T1, T2, (T3 / [C1] T4)", DURATIONS: {"T1": [0,0], "T2": [0,1], "T3": [0,2], "T4": [0,3]}, DELAYS: {"C1": 1}}, {"C1": "T3"}, 4.0, "07_seq_seq_choice_T3_d1")

    def test_07_seq_seq_choice_T4_d1(self):
        self.run_scenario({EXPRESSION: "T1, T2, (T3 / [C1] T4)", DURATIONS: {"T1": [0,0], "T2": [0,1], "T3": [0,2], "T4": [0,3]}, DELAYS: {"C1": 1}}, {"C1": "T4"}, 5.0, "07_seq_seq_choice_T4_d1")

    def test_08_parallel_tasks_eq(self):
        self.run_scenario({EXPRESSION: "T1 || T2", DURATIONS: {"T1": [0,1], "T2": [0,1]}}, {}, 1.0, "08_parallel_eq")

    def test_08_parallel_tasks_t1_lt_t2(self):
        self.run_scenario({EXPRESSION: "T1 || T2", DURATIONS: {"T1": [0,1], "T2": [0,2]}}, {}, 2.0, "08_parallel_t1_lt_t2")

    def test_08_parallel_tasks_t1_gt_t2(self):
        self.run_scenario({EXPRESSION: "T1 || T2", DURATIONS: {"T1": [0,2], "T2": [0,1]}}, {}, 2.0, "08_parallel_t1_gt_t2")

    def test_09_parallel_choice_T2(self):
        self.run_scenario({EXPRESSION: "(T2 / [C1] T3) || T1", DURATIONS: {"T1": [0,1], "T2": [0,10], "T3": [0,20]}, DELAYS: {"C1": 1}}, {"C1": "T2"}, 11.0, "09_par_choice_T2")

    def test_09_parallel_choice_T3(self):
        self.run_scenario({EXPRESSION: "(T2 / [C1] T3) || T1", DURATIONS: {"T1": [0,1], "T2": [0,10], "T3": [0,20]}, DELAYS: {"C1": 1}}, {"C1": "T3"}, 21.0, "09_par_choice_T3")

    def test_10_parallel_natures_1(self):
        self.run_scenario({EXPRESSION: "(T1A ^ [N1] T1B) || (T2A ^ [N2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, PROBABILITIES: {"N1": 0.5, "N2": 0.5}}, {"N1": "T1A", "N2": "T2A"}, 3.0, "10_par_natures_T1A_T2A")

    def test_10_parallel_natures_2(self):
        self.run_scenario({EXPRESSION: "(T1A ^ [N1] T1B) || (T2A ^ [N2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, PROBABILITIES: {"N1": 0.5, "N2": 0.5}}, {"N1": "T1A", "N2": "T2B"}, 4.0, "10_par_natures_T1A_T2B")

    def test_10_parallel_natures_3(self):
        self.run_scenario({EXPRESSION: "(T1A ^ [N1] T1B) || (T2A ^ [N2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, PROBABILITIES: {"N1": 0.5, "N2": 0.5}}, {"N1": "T1B", "N2": "T2A"}, 3.0, "10_par_natures_T1B_T2A")

    def test_10_parallel_natures_4(self):
        self.run_scenario({EXPRESSION: "(T1A ^ [N1] T1B) || (T2A ^ [N2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, PROBABILITIES: {"N1": 0.5, "N2": 0.5}}, {"N1": "T1B", "N2": "T2B"}, 4.0, "10_par_natures_T1B_T2B")

    def test_11_parallel_choices_1(self):
        self.run_scenario({EXPRESSION: "(T1A / [C1] T1B) || (T2A / [C2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, DELAYS: {"C1": 1, "C2": 1}}, {"C1": "T1A", "C2": "T2A"}, 4.0, "11_par_choices_T1A_T2A")

    def test_11_parallel_choices_2(self):
        self.run_scenario({EXPRESSION: "(T1A / [C1] T1B) || (T2A / [C2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, DELAYS: {"C1": 1, "C2": 1}}, {"C1": "T1A", "C2": "T2B"}, 5.0, "11_par_choices_T1A_T2B")

    def test_11_parallel_choices_3(self):
        self.run_scenario({EXPRESSION: "(T1A / [C1] T1B) || (T2A / [C2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, DELAYS: {"C1": 1, "C2": 1}}, {"C1": "T1B", "C2": "T2A"}, 4.0, "11_par_choices_T1B_T2A")

    def test_11_parallel_choices_4(self):
        self.run_scenario({EXPRESSION: "(T1A / [C1] T1B) || (T2A / [C2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, DELAYS: {"C1": 1, "C2": 1}}, {"C1": "T1B", "C2": "T2B"}, 5.0, "11_par_choices_T1B_T2B")

    def test_12_parallel_nature_choice_1(self):
        self.run_scenario({EXPRESSION: "(T1A ^ [N1] T1B) || (T2A / [C2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, PROBABILITIES: {"N1": 0.5}, DELAYS: {"C2": 0}}, {"N1": "T1A", "C2": "T2A"}, 3.0, "12_par_nat_ch_T1A_T2A")

    def test_12_parallel_nature_choice_2(self):
        self.run_scenario({EXPRESSION: "(T1A ^ [N1] T1B) || (T2A / [C2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, PROBABILITIES: {"N1": 0.5}, DELAYS: {"C2": 0}}, {"N1": "T1A", "C2": "T2B"}, 4.0, "12_par_nat_ch_T1A_T2B")

    def test_12_parallel_nature_choice_3(self):
        self.run_scenario({EXPRESSION: "(T1A ^ [N1] T1B) || (T2A / [C2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, PROBABILITIES: {"N1": 0.5}, DELAYS: {"C2": 0}}, {"N1": "T1B", "C2": "T2A"}, 3.0, "12_par_nat_ch_T1B_T2A")

    def test_12_parallel_nature_choice_4(self):
        self.run_scenario({EXPRESSION: "(T1A ^ [N1] T1B) || (T2A / [C2] T2B)", DURATIONS: {"T1A": [0,1], "T1B": [0,2], "T2A": [0,3], "T2B": [0,4]}, PROBABILITIES: {"N1": 0.5}, DELAYS: {"C2": 0}}, {"N1": "T1B", "C2": "T2B"}, 4.0, "12_par_nat_ch_T1B_T2B")

    def test_13_parallel_choice_nature_nature_1(self):
        self.run_scenario({EXPRESSION: "(T1A / [C1] T1B) || (T2A ^ [N2] T2B) || (T3A ^ [N3] T3B)", DURATIONS: {"T1A": 1, "T1B": 2, "T2A": 3, "T2B": 4, "T3A": 5, "T3B": 6}, PROBABILITIES: {"N2": 0.5, "N3": 0.5}, DELAYS: {"C1": 0}}, {"C1": "T1A", "N2": "T2A", "N3": "T3A"}, 5.0, "13_par_ch_nat_nat_1")

    def test_13_parallel_choice_nature_nature_2(self):
        self.run_scenario({EXPRESSION: "(T1A / [C1] T1B) || (T2A ^ [N2] T2B) || (T3A ^ [N3] T3B)", DURATIONS: {"T1A": 1, "T1B": 2, "T2A": 3, "T2B": 4, "T3A": 5, "T3B": 6}, PROBABILITIES: {"N2": 0.5, "N3": 0.5}, DELAYS: {"C1": 0}}, {"C1": "T1B", "N2": "T2B", "N3": "T3B"}, 6.0, "13_par_ch_nat_nat_2")

    def test_14_parallel_sequential_nature_T3(self):
        self.run_scenario({EXPRESSION: "T1 || T2, (T3 ^ [N1] T4)", DURATIONS: {"T1": 1, "T2": 1, "T3": 2, "T4": 3}, PROBABILITIES: {"N1": 0.5}}, {"N1": "T3"}, 3.0, "14_par_seq_nature_T3")

    def test_14_parallel_sequential_nature_T4(self):
        self.run_scenario({EXPRESSION: "T1 || T2, (T3 ^ [N1] T4)", DURATIONS: {"T1": 1, "T2": 1, "T3": 2, "T4": 3}, PROBABILITIES: {"N1": 0.5}}, {"N1": "T4"}, 4.0, "14_par_seq_nature_T4")
