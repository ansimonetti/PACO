#!/usr/bin/env python3
"""
Script per generare execution tree e tracce per tutti i pattern di test.
Processa tutti i file JSON nella cartella simulator/tests/spin/output/
Usa direttamente il simulatore SPIN per esplorare i percorsi.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import copy

# Aggiungi paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simulator', 'src'))

# Import SPIN simulator
from model.region import RegionModel
from model.context import NetContext
from model.extree import ExecutionTree
from strategy.execution import get_choices
from utils.net_utils import is_final_marking

# Import per visualizzazione
try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

IMPACTS_NAMES = "impacts_names"


def is_region_model(data):
    """Verifica se il JSON è un RegionModel (formato SPIN)."""
    if 'id' in data and 'type' in data:
        return True
    return False


def explore_all_paths_spin(region_model, max_steps=10000):
    """Esplora tutti i possibili percorsi usando il simulatore SPIN."""
    from strategy.base import execute_transition
    from strategy.execution import get_choices, add_impacts
    from model.extree.node import Snapshot
    
    # Crea il context dal region model
    ctx = NetContext.from_region(region_model)
    
    # Crea l'execution tree iniziale
    extree = ExecutionTree.from_context(ctx, region_model)
    
    # Esplora tutti i percorsi con BFS
    nodes_to_explore = [extree.root]
    explored_count = 0
    visited = set()
    
    while nodes_to_explore and explored_count < max_steps:
        current = nodes_to_explore.pop(0)
        explored_count += 1
        
        # Crea una chiave per evitare cicli
        marking_key = str(sorted([(str(p), str(current.snapshot.marking[p])) for p in current.snapshot.marking]))
        if marking_key in visited:
            continue
        visited.add(marking_key)
        
        # Verifica se è uno stato finale
        if is_final_marking(ctx, current.snapshot.marking):
            continue
        
        # Ottieni le scelte possibili (transizioni abilitate)
        choice_dict = get_choices(ctx, current.snapshot.marking)
        
        if not choice_dict:
            continue
        
        # Esplora ogni transizione abilitata
        all_transitions = []
        for place, transitions in choice_dict.items():
            all_transitions.extend(transitions)
        
        for transition in all_transitions:
            try:
                # Esegui la transizione
                new_marking, probability, impacts = execute_transition(ctx, transition, current.snapshot.marking)
                
                # Calcola nuovi impatti cumulativi
                current_impacts = current.snapshot.impacts or []
                new_impacts = add_impacts(current_impacts, impacts)
                
                # Calcola probabilità cumulativa
                new_probability = current.snapshot.probability * probability
                
                # Crea il nome della decisione
                decision_name = getattr(transition, 'label', None) or getattr(transition, 'name', str(transition))
                
                # Crea nuovo snapshot
                new_snapshot = Snapshot(
                    marking=new_marking,
                    probability=new_probability,
                    impacts=new_impacts,
                    time=current.snapshot.time,
                    status=current.snapshot.status.copy() if current.snapshot.status else {},
                    decisions=current.snapshot.decisions + [decision_name],
                    choices=[]
                )
                
                # Aggiungi il nuovo snapshot all'albero
                extree.current_node = current
                new_node = extree.add_snapshot(ctx, new_snapshot, set_as_current=False)
                
                if new_node:
                    nodes_to_explore.append(new_node)
                    
            except Exception as e:
                print(f"    ⚠ Errore esecuzione transition: {e}")
                continue
    
    return extree, explored_count


def analyze_execution_tree(execution_tree, impacts_names=None):
    """Analizza l'execution tree SPIN e restituisce statistiche."""
    # ExecutionTree SPIN usa anytree, quindi i nodi hanno .children
    all_nodes = execution_tree.get_nodes()
    
    stats = {
        'total_nodes': len(all_nodes),
        'final_nodes': 0,
        'max_depth': 0,
    }
    
    # Crea context per verificare marking finali
    ctx = None
    
    for node in all_nodes:
        # Calcola profondità
        depth = node.depth
        stats['max_depth'] = max(stats['max_depth'], depth)
        
        # Verifica se è finale
        if hasattr(node.snapshot, 'marking'):
            if ctx is None and hasattr(execution_tree, 'context'):
                ctx = execution_tree.context
            if ctx and is_final_marking(ctx, node.snapshot.marking):
                stats['final_nodes'] += 1
    
    return stats


def extract_traces_from_execution_tree(execution_tree, impacts_names):
    """Estrae tutte le tracce (percorsi) dall'execution tree SPIN."""
    traces = []
    
    # ExecutionTree SPIN usa anytree
    def traverse_anytree(node, path_decisions=None):
        if path_decisions is None:
            path_decisions = []
        
        # Ottieni dati dal snapshot
        snapshot = node.snapshot
        current_decisions = path_decisions + snapshot.decisions
        
        # Converti impacts list in dict
        impacts_dict = {}
        if impacts_names and snapshot.impacts:
            for i, imp_name in enumerate(impacts_names):
                if i < len(snapshot.impacts):
                    impacts_dict[imp_name] = float(snapshot.impacts[i])
        
        # Verifica se è finale (nodo senza figli o marking finale)
        is_final = not node.children
        if hasattr(execution_tree, 'context'):
            ctx = execution_tree.context
            if hasattr(snapshot, 'marking') and is_final_marking(ctx, snapshot.marking):
                is_final = True
        
        if is_final:
            traces.append({
                'decisions': current_decisions,
                'impacts': impacts_dict,
                'probability': float(snapshot.probability),
                'node_id': getattr(node, 'id', str(node))
            })
        
        # Ricorri sui figli (anytree usa .children)
        for child in node.children:
            traverse_anytree(child, current_decisions)
    
    # Inizia dal root
    traverse_anytree(execution_tree.root)
    
    return traces


def execution_tree_to_dict(execution_tree):
    """Converte ExecutionTree SPIN in dizionario serializzabile."""
    def node_to_dict(node):
        snapshot = node.snapshot
        
        # Converti marking in formato serializzabile
        marking_dict = {}
        if hasattr(snapshot, 'marking'):
            marking = snapshot.marking
            # TimeMarking ha keys() e __getitem__
            if hasattr(marking, 'keys'):
                for place in marking.keys():
                    place_key = f"P{getattr(place, 'id', str(place))}"
                    marking_item = marking[place]
                    marking_dict[place_key] = {
                        'token': getattr(marking_item, 'token', 0),
                        'age': getattr(marking_item, 'age', 0),
                        'visit_count': getattr(marking_item, 'visit_count', 0)
                    }
        
        node_dict = {
            'id': getattr(node, 'id', str(node)),
            'name': getattr(node, 'name', 'Node'),
            'snapshot': {
                'probability': float(snapshot.probability),
                'impacts': list(snapshot.impacts) if snapshot.impacts else [],
                'execution_time': float(snapshot.execution_time),
                'decisions': list(snapshot.decisions),
                'choices': list(snapshot.choices),
                'marking': marking_dict
            },
            'children': []
        }
        
        # Ricorsivamente converti i figli
        for child in node.children:
            node_dict['children'].append(node_to_dict(child))
        
        return node_dict
    
    return node_to_dict(execution_tree.root)


def save_execution_tree_dot(execution_tree, outfile, state=True, executed_time=True):
    """Salva l'ExecutionTree SPIN come SVG usando graphviz (metodologia PACO)."""
    if not HAS_GRAPHVIZ:
        raise ImportError("graphviz non installato. Installa con: pip install graphviz")
    
    # Crea il dot graph
    dot_content = execution_tree_to_dot(execution_tree, state=state, executed_time=executed_time)
    
    # Crea directory se non esiste
    directory = os.path.dirname(outfile)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    # Salva come SVG
    svg_path = outfile if outfile.endswith('.svg') else outfile + '.svg'
    with open(svg_path, "wb") as f:
        f.write(graphviz.Source(dot_content).pipe(format="svg"))
    
    return svg_path


def execution_tree_to_dot(execution_tree, state=True, executed_time=True):
    """Converte ExecutionTree SPIN in formato DOT per graphviz."""
    lines = ["digraph executionTree {"]
    lines.append('    node [shape=box, style=rounded];')
    
    def node_to_dot(node, parent_id=None):
        node_id = getattr(node, 'id', str(id(node)))
        snapshot = node.snapshot
        
        # Crea label del nodo
        label_parts = [f"Node {node_id}"]
        
        if state and hasattr(snapshot, 'decisions') and snapshot.decisions:
            decisions_str = ", ".join(str(d) for d in snapshot.decisions)
            label_parts.append(f"Decisions: {decisions_str}")
        
        if hasattr(snapshot, 'impacts') and snapshot.impacts:
            impacts_str = ", ".join(f"{v:.2f}" for v in snapshot.impacts)
            label_parts.append(f"Impacts: [{impacts_str}]")
        
        if hasattr(snapshot, 'probability'):
            label_parts.append(f"Prob: {snapshot.probability:.4f}")
        
        if executed_time and hasattr(snapshot, 'execution_time'):
            label_parts.append(f"Time: {snapshot.execution_time:.2f}")
        
        label = "\\n".join(label_parts)
        lines.append(f'    "{node_id}" [label="{label}"];')
        
        # Connessione dal parent
        if parent_id is not None:
            lines.append(f'    "{parent_id}" -> "{node_id}";')
        
        # Ricorsione sui figli
        for child in node.children:
            node_to_dot(child, node_id)
    
    # Aggiungi nodo start
    lines.append('    __start0 [label="", shape=none];')
    root_id = getattr(execution_tree.root, 'id', str(id(execution_tree.root)))
    lines.append(f'    __start0 -> "{root_id}";')
    
    # Genera grafo dall'albero
    node_to_dot(execution_tree.root)
    
    lines.append("}")
    return "\n".join(lines)


def process_bpmn_file(bpmn_file, output_dir):
    """Processa un singolo file RegionModel e genera execution tree usando SPIN."""
    file_name = Path(bpmn_file).stem
    print(f"\n{'='*70}")
    print(f"📂 Processamento: {file_name}")
    print(f"{'='*70}")
    
    # Carica JSON
    try:
        with open(bpmn_file, "r") as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"  ✗ Errore nel caricamento: {e}")
        return False
    
    # Verifica che sia RegionModel
    if not is_region_model(json_data):
        print(f"  ⊘ SALTATO - Non è un RegionModel")
        return None
    
    print(f"  🔄 Formato: RegionModel (SPIN)")
    
    # Valida e crea RegionModel
    try:
        region_model = RegionModel.model_validate(json_data)
        print(f"  ✓ RegionModel validato")
        print(f"  Type: {region_model.type}")
        print(f"  Label: {region_model.label}")
    except Exception as e:
        print(f"  ✗ Errore validazione RegionModel: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Determina impacts_names
    def find_impacts(node):
        if node.is_task():
            if node.impacts and isinstance(node.impacts, list):
                return len(node.impacts)
        if node.children:
            for child in node.children:
                result = find_impacts(child)
                if result:
                    return result
        return 0
    
    num_impacts = find_impacts(region_model)
    impacts_names = [f"I{i+1}" for i in range(num_impacts)] if num_impacts > 0 else []
    print(f"  Impacts: {impacts_names}")
    
    # Esplora tutti i percorsi con SPIN
    print(f"  🚀 Esplorazione percorsi con SPIN...")
    try:
        execution_tree, explored_count = explore_all_paths_spin(region_model, max_steps=10000)
        print(f"  ✓ Esplorazione completata ({explored_count} nodi esplorati)")
    except Exception as e:
        print(f"  ✗ Errore esplorazione: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Analizza l'albero
    print(f"  📊 Analisi execution tree...")
    try:
        all_nodes = execution_tree.get_nodes()
        total_nodes = len(all_nodes)
        final_nodes = sum(1 for node in all_nodes if hasattr(node.snapshot, 'marking') and 
                         is_final_marking(NetContext.from_region(region_model), node.snapshot.marking))
        
        max_depth = 0
        for node in all_nodes:
            depth = node.depth
            max_depth = max(max_depth, depth)
        
        is_complete = final_nodes > 0
        
        stats = {
            'total_nodes': total_nodes,
            'final_nodes': final_nodes,
            'max_depth': max_depth,
            'explored_count': explored_count
        }
        
        print(f"  ✓ Statistiche:")
        print(f"     - Nodi totali: {stats['total_nodes']}")
        print(f"     - Nodi finali: {stats['final_nodes']}")
        print(f"     - Profondità max: {stats['max_depth']}")
        print(f"     - Stato: {'COMPLETO ✅' if is_complete else 'PARZIALE ⚠️'}")
    except Exception as e:
        print(f"  ⚠ Warning analisi: {e}")
        stats = {'total_nodes': 0, 'final_nodes': 0, 'max_depth': 0, 'explored_count': explored_count}
        is_complete = False
    
    # Salva execution tree
    tree_output = os.path.join(output_dir, f"{file_name}_execution_tree.json")
    try:
        tree_dict = execution_tree_to_dict(execution_tree)
        output_data = {
            "bpmn": {
                "label": region_model.label,
                "impacts_names": impacts_names,
                "source_file": os.path.basename(bpmn_file)
            },
            "is_complete": is_complete,
            "statistics": stats,
            "execution_tree": tree_dict
        }
        
        with open(tree_output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"  💾 Tree salvato: {os.path.basename(tree_output)}")
    except Exception as e:
        print(f"  ✗ Errore salvataggio tree: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Salva visualizzazione SVG usando metodologia PACO
    svg_output = os.path.join(output_dir, f"{file_name}_execution_tree.svg")
    print(f"  🎨 Generazione visualizzazione SVG...")
    try:
        save_execution_tree_dot(execution_tree, svg_output, state=True, executed_time=True)
        print(f"  ✓ Visualizzazione salvata: {os.path.basename(svg_output)}")
    except ImportError as e:
        print(f"  ⊘ Saltato SVG: {e}")
    except Exception as e:
        if "dot" in str(e) or "Graphviz" in str(e):
            print(f"  ⊘ Saltato SVG: Graphviz non installato sul sistema")
        else:
            print(f"  ⚠ Warning SVG: {e}")
    
    # Estrai tracce
    try:
        traces = extract_traces_from_execution_tree(execution_tree, impacts_names)
        print(f"  📋 Tracce estratte: {len(traces)}")
        
        traces_output = os.path.join(output_dir, f"{file_name}_traces.json")
        traces_data = {
            "bpmn": {
                "label": region_model.label,
                "impacts_names": impacts_names,
                "source_file": os.path.basename(bpmn_file)
            },
            "is_complete": is_complete,
            "total_traces": len(traces),
            "traces": traces
        }
        
        with open(traces_output, "w") as f:
            json.dump(traces_data, f, indent=2)
        print(f"  💾 Tracce salvate: {os.path.basename(traces_output)}")
    except Exception as e:
        print(f"  ⚠ Warning estrazione tracce: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"  ✅ Completato!")
    return True


def main():
    """Funzione principale."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera execution tree e tracce per tutti i pattern di test"
    )
    parser.add_argument(
        "-i", "--input-dir",
        default="simulator/tests/spin/output",
        help="Directory contenente i file JSON BPMN (default: simulator/tests/spin/output)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="generated_patterns",
        help="Directory di output per i risultati (default: generated_patterns)"
    )
    parser.add_argument(
        "--pattern",
        help="Processa solo il pattern con questo nome (opzionale)"
    )
    
    args = parser.parse_args()
    
    # Crea directory di output
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Trova tutti i file JSON
    input_dir = args.input_dir
    if not os.path.exists(input_dir):
        print(f"✗ Directory di input non trovata: {input_dir}")
        print(f"\n💡 Suggerimento: Esegui prima i test per generare i file:")
        print(f"   cd simulator/tests/spin")
        print(f"   pytest exhaustiveness_test.py")
        return 1
    
    json_files = list(Path(input_dir).glob("*.json"))
    
    if args.pattern:
        # Filtra per pattern specifico
        json_files = [f for f in json_files if args.pattern in f.stem]
    
    if not json_files:
        print(f"✗ Nessun file JSON trovato in {input_dir}")
        return 1
    
    skipped_count = 0
    success_count = 0
    fail_count = 0
    for bpmn_file in sorted(json_files):
        try:
            result = process_bpmn_file(bpmn_file, output_dir)
            if result is True:
                success_count += 1
            elif result is False:
                fail_count += 1
            else:  # None = saltato
                skipped_count += 1
        except Exception as e:
            print(f"\n✗ Errore inaspettato processando {bpmn_file.name}: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
    
    print(f"\n{'='*70}")
    print(f"📈 RIEPILOGO FINALE")
    print(f"{'='*70}")
    print(f"Totale file processati: {len(json_files)}")
    print(f"✅ Successi: {success_count}")
    print(f"⊘ Saltati: {skipped_count}")
    print(f"✗ Fallimenti: {fail_count}")
    print(f"\n📁 Risultati salvati in: {output_dir}/")
    print(f"{'='*70}")
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
