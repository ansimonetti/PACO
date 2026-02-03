"""
Script di esempio per analizzare le tracce generate.

Mostra come:
- Caricare le tracce
- Calcolare statistiche
- Trovare tracce ottimali
- Analizzare le scelte
"""
import json
import sys
from collections import defaultdict
from typing import List, Dict, Any


def load_traces(filename: str) -> Dict[str, Any]:
    """Carica le tracce da un file JSON."""
    with open(filename, 'r') as f:
        return json.load(f)


def print_summary(data: Dict[str, Any]):
    """Stampa un riepilogo delle tracce."""
    traces = data['traces']
    impacts_names = data['bpmn']['impacts_names']
    
    print("=" * 60)
    print("RIEPILOGO TRACCE")
    print("=" * 60)
    print(f"\nModello BPMN: {data['bpmn']['expression']}")
    print(f"Numero totale di tracce: {len(traces)}")
    print(f"Dimensioni impatto: {', '.join(impacts_names)}")
    
    # Statistiche sulle probabilità
    total_prob = sum(t['probability'] for t in traces)
    print(f"\nProbabilità totale: {total_prob:.4f}")
    
    # Lunghezza media delle tracce
    avg_decisions = sum(len(t['decisions']) for t in traces) / len(traces)
    print(f"Numero medio di decisioni per traccia: {avg_decisions:.2f}")
    
    # Tempo medio di esecuzione
    avg_time = sum(t['execution_time'] for t in traces) / len(traces)
    print(f"Tempo medio di esecuzione: {avg_time:.2f}")


def find_optimal_traces(traces: List[Dict], impacts_names: List[str]):
    """Trova le tracce ottimali per ogni dimensione di impatto."""
    print("\n" + "=" * 60)
    print("TRACCE OTTIMALI PER DIMENSIONE")
    print("=" * 60)
    
    for impact_name in impacts_names:
        # Trova traccia con impatto minimo
        min_trace = min(traces, key=lambda t: t['impacts'][impact_name])
        
        # Trova traccia con impatto massimo
        max_trace = max(traces, key=lambda t: t['impacts'][impact_name])
        
        print(f"\n{impact_name.upper()}:")
        print(f"  Minimo: {min_trace['impacts'][impact_name]:.2f}")
        print(f"    Decisioni: {' -> '.join(min_trace['decisions'])}")
        print(f"    Probabilità: {min_trace['probability']:.4f}")
        print(f"  Massimo: {max_trace['impacts'][impact_name]:.2f}")
        print(f"    Decisioni: {' -> '.join(max_trace['decisions'])}")
        print(f"    Probabilità: {max_trace['probability']:.4f}")


def analyze_by_decision(traces: List[Dict], impacts_names: List[str]):
    """Analizza l'impatto di ogni decisione."""
    print("\n" + "=" * 60)
    print("ANALISI PER DECISIONE")
    print("=" * 60)
    
    # Raggruppa tracce per decisione
    by_decision = defaultdict(list)
    for trace in traces:
        for decision in trace['decisions']:
            by_decision[decision].append(trace)
    
    # Analizza ogni decisione
    for decision in sorted(by_decision.keys()):
        related_traces = by_decision[decision]
        print(f"\nDecisione: {decision}")
        print(f"  Numero di tracce: {len(related_traces)}")
        
        for impact_name in impacts_names:
            values = [t['impacts'][impact_name] for t in related_traces]
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            
            print(f"  {impact_name}:")
            print(f"    Media: {avg:.2f}")
            print(f"    Min: {min_val:.2f}, Max: {max_val:.2f}")


def find_pareto_frontier(traces: List[Dict], impacts_names: List[str]):
    """
    Trova la frontiera di Pareto (tracce non dominate).
    
    Una traccia domina un'altra se è migliore o uguale in tutte le dimensioni
    e strettamente migliore in almeno una.
    """
    print("\n" + "=" * 60)
    print("FRONTIERA DI PARETO")
    print("=" * 60)
    
    def dominates(trace1, trace2):
        """Verifica se trace1 domina trace2 (assumendo che minore è meglio)."""
        better_in_all = True
        strictly_better_in_one = False
        
        for impact_name in impacts_names:
            val1 = trace1['impacts'][impact_name]
            val2 = trace2['impacts'][impact_name]
            
            if val1 > val2:
                better_in_all = False
                break
            if val1 < val2:
                strictly_better_in_one = True
        
        return better_in_all and strictly_better_in_one
    
    # Trova tracce non dominate
    pareto_traces = []
    for trace in traces:
        is_dominated = False
        for other in traces:
            if other != trace and dominates(other, trace):
                is_dominated = True
                break
        
        if not is_dominated:
            pareto_traces.append(trace)
    
    print(f"\nTracce sulla frontiera di Pareto: {len(pareto_traces)} su {len(traces)}")
    
    # Mostra le tracce Pareto-ottimali
    print("\nTracce non dominate:")
    for i, trace in enumerate(pareto_traces, 1):
        print(f"\n{i}. Decisioni: {' -> '.join(trace['decisions'])}")
        print(f"   Impatti:", end="")
        for impact_name in impacts_names:
            print(f" {impact_name}={trace['impacts'][impact_name]:.2f}", end="")
        print(f"\n   Probabilità: {trace['probability']:.4f}")
        print(f"   Tempo: {trace['execution_time']:.2f}")


def compare_choice_outcomes(traces: List[Dict], choice_labels: List[str], impacts_names: List[str]):
    """
    Confronta gli esiti di scelte specifiche.
    
    Args:
        traces: Lista di tracce
        choice_labels: Liste di label di scelte da confrontare (es. ['C1', 'C2'])
        impacts_names: Nome delle dimensioni di impatto
    """
    print("\n" + "=" * 60)
    print("CONFRONTO SCELTE")
    print("=" * 60)
    
    # Per ogni scelta, raggruppa le tracce per l'alternativa presa
    for choice_label in choice_labels:
        print(f"\n{choice_label}:")
        
        # Identifica le decisioni associate a questa scelta
        choice_decisions = set()
        for trace in traces:
            for decision in trace['decisions']:
                if choice_label.lower() in decision.lower():
                    choice_decisions.add(decision)
        
        if not choice_decisions:
            print(f"  Nessuna decisione trovata per {choice_label}")
            continue
        
        # Analizza ogni alternativa
        for decision in sorted(choice_decisions):
            related_traces = [t for t in traces if decision in t['decisions']]
            
            if not related_traces:
                continue
            
            print(f"\n  Alternativa: {decision}")
            print(f"    Tracce: {len(related_traces)}")
            
            for impact_name in impacts_names:
                values = [t['impacts'][impact_name] for t in related_traces]
                avg = sum(values) / len(values)
                print(f"    {impact_name} medio: {avg:.2f}")
            
            avg_prob = sum(t['probability'] for t in related_traces) / len(related_traces)
            print(f"    Probabilità media: {avg_prob:.4f}")


def export_trace_summary(traces: List[Dict], impacts_names: List[str], output_file: str):
    """Esporta un riepilogo delle tracce in CSV."""
    import csv
    
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['trace_id', 'decisions', 'probability', 'execution_time'] + impacts_names
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for trace in traces:
            row = {
                'trace_id': trace['id'],
                'decisions': ' -> '.join(trace['decisions']),
                'probability': trace['probability'],
                'execution_time': trace['execution_time']
            }
            row.update(trace['impacts'])
            writer.writerow(row)
    
    print(f"\n✓ Riepilogo esportato in {output_file}")


def main():
    """Funzione principale."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analizza le tracce di esecuzione generate"
    )
    parser.add_argument(
        "traces_file",
        help="File JSON contenente le tracce (generato da generate_all_traces.py)"
    )
    parser.add_argument(
        "--export-csv",
        help="Esporta un riepilogo in formato CSV"
    )
    parser.add_argument(
        "--choice-labels",
        nargs="+",
        help="Label delle scelte da confrontare (es. C1 C2)"
    )
    
    args = parser.parse_args()
    
    # Carica le tracce
    print(f"Caricamento tracce da {args.traces_file}...")
    try:
        data = load_traces(args.traces_file)
    except Exception as e:
        print(f"Errore nel caricamento del file: {e}")
        return 1
    
    traces = data['traces']
    impacts_names = data['bpmn']['impacts_names']
    
    if not traces:
        print("Nessuna traccia trovata nel file!")
        return 1
    
    # Analisi
    print_summary(data)
    find_optimal_traces(traces, impacts_names)
    analyze_by_decision(traces, impacts_names)
    find_pareto_frontier(traces, impacts_names)
    
    # Confronta scelte specifiche se richiesto
    if args.choice_labels:
        compare_choice_outcomes(traces, args.choice_labels, impacts_names)
    
    # Esporta CSV se richiesto
    if args.export_csv:
        export_trace_summary(traces, impacts_names, args.export_csv)
    
    print("\n" + "=" * 60)
    print("Analisi completata!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
