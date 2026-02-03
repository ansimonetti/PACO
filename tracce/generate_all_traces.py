"""
Script per generare tutte le possibili tracce di esecuzione da un modello BPMN
usando direttamente le funzioni interne di PACO.

Crea l'execution tree completo (o parziale) con tutti i nodi e impatti.
"""
import json
import sys
import os
from typing import Any, Dict, List

# Aggiungi i path necessari
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'simulator', 'src'))

# Import delle funzioni PACO
from src.paco.parser.bpmn_parser import create_parse_tree
from src.paco.parser.parse_tree import ParseTree
from src.paco.searcher.create_execution_tree import create_execution_tree
from src.paco.execution_tree.execution_tree import ExecutionTree
from src.paco.saturate_execution.states import ActivityState
from src.utils import check_syntax as cs
from src.utils.env import DURATIONS, IMPACTS_NAMES


def extract_traces_from_execution_tree(execution_tree: ExecutionTree, impacts_names: List[str]) -> List[Dict[str, Any]]:
    """
    Estrae tutte le tracce dall'execution tree PACO.
    
    Ogni traccia è un percorso dalla radice a una foglia.
    """
    traces = []
    
    def traverse_tree(node, path_decisions, path_nodes):
        """Attraversa ricorsivamente l'albero."""
        # Se è uno stato finale (foglia), salva la traccia
        if node.is_final_state or not hasattr(node, 'children') or len(node.children) == 0:
            trace = {
                "id": len(traces),
                "node_id": node.id,
                "decisions": [d.name if hasattr(d, 'name') else str(d) for d in path_decisions],
                "impacts": dict(zip(impacts_names, node.impacts)),
                "probability": float(node.probability),
                "is_final": node.is_final_state,
                "cei_top_down": list(node.cei_top_down) if hasattr(node, 'cei_top_down') else [],
                "cei_bottom_up": list(node.cei_bottom_up) if hasattr(node, 'cei_bottom_up') else [],
                "path": path_nodes + [node.id],
                "choices": [c.name if hasattr(c, 'name') else str(c) for c in node.choices] if node.choices else [],
                "natures": [n.name if hasattr(n, 'name') else str(n) for n in node.natures] if node.natures else [],
            }
            traces.append(trace)
            return
        
        # Continua per ogni figlio
        if hasattr(node, 'children'):
            for child_tree in node.children:
                child_node = child_tree.root
                # Aggiungi le decisioni di questo nodo ai path
                new_decisions = list(path_decisions) + list(child_node.decisions)
                traverse_tree(child_node, new_decisions, path_nodes + [node.id])
    
    # Inizia dalla radice
    traverse_tree(execution_tree.root, list(execution_tree.root.decisions), [])
    
    return traces


def count_tree_nodes(execution_tree: ExecutionTree) -> int:
    """Conta tutti i nodi nell'execution tree."""
    def count_recursive(node):
        total = 1
        if hasattr(node, 'children'):
            for child_tree in node.children:
                total += count_recursive(child_tree.root)
        return total
    
    return count_recursive(execution_tree.root)


def analyze_execution_tree(execution_tree: ExecutionTree, impacts_names: List[str]) -> Dict[str, Any]:
    """Analizza l'execution tree e ritorna statistiche."""
    def analyze_node(node, depth=0):
        stats = {
            'total_nodes': 1,
            'final_nodes': 1 if node.is_final_state else 0,
            'max_depth': depth,
            'nodes_with_choices': 1 if node.choices and len(node.choices) > 0 else 0,
            'nodes_with_natures': 1 if node.natures and len(node.natures) > 0 else 0,
        }
        
        if hasattr(node, 'children'):
            for child_tree in node.children:
                child_stats = analyze_node(child_tree.root, depth + 1)
                stats['total_nodes'] += child_stats['total_nodes']
                stats['final_nodes'] += child_stats['final_nodes']
                stats['max_depth'] = max(stats['max_depth'], child_stats['max_depth'])
                stats['nodes_with_choices'] += child_stats['nodes_with_choices']
                stats['nodes_with_natures'] += child_stats['nodes_with_natures']
        
        return stats
    
    return analyze_node(execution_tree.root)


def main():
    """Funzione principale."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera l'execution tree completo da un modello BPMN usando le funzioni interne di PACO"
    )
    parser.add_argument(
        "bpmn_file",
        help="File JSON contenente la definizione BPMN"
    )
    parser.add_argument(
        "-o", "--output",
        default="execution_tree.json",
        help="File di output per l'albero di esecuzione (default: execution_tree.json)"
    )
    parser.add_argument(
        "--traces-output",
        default="all_traces.json",
        help="File di output per le tracce estratte (default: all_traces.json)"
    )
    parser.add_argument(
        "--save-dot",
        action="store_true",
        help="Salva anche la visualizzazione DOT dell'albero"
    )
    
    args = parser.parse_args()
    
    # Carica la definizione BPMN
    print(f"📂 Caricamento BPMN da {args.bpmn_file}...")
    try:
        with open(args.bpmn_file, "r") as f:
            bpmn_definition = json.load(f)
    except Exception as e:
        print(f"✗ Errore nel caricamento del file: {e}")
        return 1
    
    impacts_names = bpmn_definition.get(IMPACTS_NAMES, [])
    expression = bpmn_definition.get('expression', '')
    print(f"✓ BPMN caricato")
    print(f"  Expression: {expression}")
    print(f"  Impacts: {impacts_names}")
    
    # Preprocessa le durations
    print("\n🔧 Preprocessamento BPMN...")
    try:
        bpmn_definition[DURATIONS] = cs.set_max_duration(bpmn_definition.get(DURATIONS, {}))
    except Exception as e:
        print(f"⚠ Warning durante preprocessing durations: {e}")
    
    # Crea il parse tree
    print("\n🌳 Creazione parse tree...")
    try:
        parse_tree, pending_choices, pending_natures, pending_loops = create_parse_tree(bpmn_definition)
        print(f"✓ Parse tree creato")
        print(f"  Pending choices: {len(pending_choices)}")
        print(f"  Pending natures: {len(pending_natures)}")
    except Exception as e:
        print(f"✗ Errore nella creazione del parse tree: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Crea l'execution tree
    print("\n🚀 Creazione execution tree (saturazione completa)...")
    try:
        execution_tree = create_execution_tree(parse_tree, impacts_names, pending_choices, pending_natures)
        print("✓ Execution tree creato")
    except Exception as e:
        print(f"✗ Errore nella creazione dell'execution tree: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Analizza l'albero
    print("\n📊 Analisi execution tree...")
    stats = analyze_execution_tree(execution_tree, impacts_names)
    total_nodes = count_tree_nodes(execution_tree)
    
    print(f"✓ Statistiche albero:")
    print(f"  - Nodi totali: {stats['total_nodes']}")
    print(f"  - Nodi finali (foglie): {stats['final_nodes']}")
    print(f"  - Profondità massima: {stats['max_depth']}")
    print(f"  - Nodi con choices: {stats['nodes_with_choices']}")
    print(f"  - Nodi con natures: {stats['nodes_with_natures']}")
    
    # Verifica se l'albero è completo
    is_complete = stats['final_nodes'] > 0
    if is_complete:
        print(f"\n✅ Albero COMPLETO - Tutti i percorsi sono stati esplorati")
    else:
        print(f"\n⚠️  Albero PARZIALE - Alcuni percorsi potrebbero non essere completi")
    
    # Salva l'execution tree in formato JSON
    print(f"\n💾 Salvataggio execution tree in {args.output}...")
    try:
        tree_dict = execution_tree.to_dict()
        output_data = {
            "bpmn": {
                "expression": expression,
                "impacts_names": impacts_names
            },
            "is_complete": is_complete,
            "statistics": stats,
            "execution_tree": tree_dict
        }
        
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"✓ Execution tree salvato")
    except Exception as e:
        print(f"✗ Errore nel salvataggio: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Salva visualizzazione DOT se richiesto
    if args.save_dot:
        print(f"\n🎨 Salvataggio visualizzazione DOT...")
        try:
            dot_file = args.output.replace('.json', '')
            execution_tree.save_dot(outfile=dot_file, state=True, executed_time=True, diff=True)
            print(f"✓ Visualizzazione salvata in {dot_file}.svg")
        except Exception as e:
            print(f"⚠ Warning: Impossibile salvare visualizzazione DOT: {e}")
    
    # Estrai le tracce
    print(f"\n📋 Estrazione tracce...")
    try:
        traces = extract_traces_from_execution_tree(execution_tree, impacts_names)
        print(f"✓ Estratte {len(traces)} tracce")
        
        # Salva le tracce
        if args.traces_output:
            traces_data = {
                "bpmn": {
                    "expression": expression,
                    "impacts_names": impacts_names
                },
                "is_complete": is_complete,
                "total_traces": len(traces),
                "traces": traces
            }
            
            with open(args.traces_output, "w") as f:
                json.dump(traces_data, f, indent=2)
            print(f"✓ Tracce salvate in {args.traces_output}")
    except Exception as e:
        print(f"⚠ Warning: Errore nell'estrazione tracce: {e}")
        import traceback
        traceback.print_exc()
    
    # Statistiche finali
    print("\n" + "="*60)
    print("📈 RIEPILOGO FINALE")
    print("="*60)
    print(f"BPMN: {expression}")
    print(f"Albero: {'COMPLETO' if is_complete else 'PARZIALE'}")
    print(f"Nodi totali: {stats['total_nodes']}")
    print(f"Tracce estratte: {len(traces) if 'traces' in locals() else 0}")
    print(f"\nFile generati:")
    print(f"  - {args.output} (execution tree)")
    if args.traces_output and 'traces' in locals():
        print(f"  - {args.traces_output} (tracce)")
    if args.save_dot:
        print(f"  - {args.output.replace('.json', '')}.svg (visualizzazione)")
    print("\n✅ Completato con successo!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
