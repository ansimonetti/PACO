# Generatore di Tracce BPMN

Script per generare tutte le possibili tracce di esecuzione da un modello BPMN e salvarle nel formato JSON usato da PACO.

## Prerequisiti

1. **Avviare il server del simulatore**:
   ```bash
   cd simulator
   python src/main.py
   ```
   Il server dovrebbe essere in esecuzione su `http://127.0.0.1:8001`

2. **Avviare il server PACO** (in un altro terminale):
   ```bash
   python -m src.server
   ```
   Il server dovrebbe essere in esecuzione su `http://127.0.0.1:8000`

## Utilizzo

### Uso Base

```bash
python generate_all_traces.py bpmn_fig8_bound_135_15.json
```

Questo comando:
- Legge il file BPMN specificato
- Genera tutte le possibili tracce di esecuzione
- Salva le tracce in `all_traces.json` (default)
- Salva l'albero di esecuzione completo in `complete_execution_tree.json` (default)

### Opzioni Avanzate

```bash
python generate_all_traces.py bpmn_file.json \
    -o my_traces.json \
    --execution-tree-output my_execution_tree.json \
    --max-nodes 5000
```

**Opzioni disponibili:**

- `-o, --output`: Nome del file di output per le tracce (default: `all_traces.json`)
- `--execution-tree-output`: Nome del file per l'albero di esecuzione completo (default: `complete_execution_tree.json`)
- `--max-nodes`: Numero massimo di nodi da espandere, utile per limitare il tempo di calcolo (default: 10000)

## Formato Output

### File delle Tracce (`all_traces.json`)

```json
{
  "bpmn": {
    "expression": "T0, (T1 / [C1] T2), (T3 ^ [N1] T4)",
    "impacts_names": ["cost", "time"]
  },
  "total_traces": 4,
  "traces": [
    {
      "id": 0,
      "decisions": ["t1", "t5", "t8"],
      "impacts": {
        "cost": 15.5,
        "time": 120.0
      },
      "probability": 0.6,
      "execution_time": 120.0,
      "status": {...},
      "path": ["0", "1", "2"],
      "is_final": true
    },
    ...
  ]
}
```

**Campi della traccia:**
- `id`: Identificatore univoco della traccia
- `decisions`: Sequenza di decisioni (transizioni) prese
- `impacts`: Impatti finali per ogni dimensione (costo, tempo, ecc.)
- `probability`: Probabilità della traccia (per nodi Nature)
- `execution_time`: Tempo totale di esecuzione
- `status`: Stato delle attività
- `path`: Percorso dei nodi attraversati
- `is_final`: Indica se la traccia raggiunge uno stato finale

### File dell'Albero di Esecuzione (`complete_execution_tree.json`)

Contiene l'albero di esecuzione completo nel formato usato dal simulatore, con:
- Struttura gerarchica di tutti i nodi
- Stati intermedi
- Scelte e decisioni a ogni punto
- Marking della rete di Petri per ogni stato

## Esempi

### Esempio 1: Processo semplice con scelte

```bash
# File BPMN con espressione: "T1, (T2 / [C1] T3)"
python generate_all_traces.py simple_choice.json

# Output: 2 tracce (una per T2, una per T3)
```

### Esempio 2: Processo con parallelismo e scelte multiple

```bash
# File BPMN con espressione: "(T1 / [C1] T2) || (T3 / [C2] T4)"
python generate_all_traces.py parallel_choices.json

# Output: 4 tracce (tutte le combinazioni di scelte)
```

### Esempio 3: Processo con nodi Nature (probabilistici)

```bash
# File BPMN con espressione: "T1, (T2 ^ [N1] T3)"
python generate_all_traces.py nature_node.json

# Output: 2 tracce con probabilità diverse
```

## Utilizzo delle Tracce Generate

Le tracce generate possono essere usate per:

1. **Analisi delle Performance**: Confrontare impatti e tempi di esecuzione delle diverse tracce

2. **Ottimizzazione**: Identificare le tracce che minimizzano costi o tempi

3. **Analisi di Pareto**: Trovare le tracce non dominate (frontiera di Pareto)

4. **Validazione del Modello**: Verificare che tutte le tracce attese siano generate

5. **Machine Learning**: Usare le tracce come dataset per addestrare modelli predittivi

## Esempio di Analisi delle Tracce

```python
import json

# Carica le tracce
with open("all_traces.json") as f:
    data = json.load(f)

traces = data["traces"]

# Trova la traccia con costo minimo
min_cost_trace = min(traces, key=lambda t: t["impacts"]["cost"])
print(f"Traccia con costo minimo: {min_cost_trace['decisions']}")
print(f"Costo: {min_cost_trace['impacts']['cost']}")

# Trova la traccia con tempo minimo
min_time_trace = min(traces, key=lambda t: t["impacts"]["time"])
print(f"Traccia con tempo minimo: {min_time_trace['decisions']}")
print(f"Tempo: {min_time_trace['impacts']['time']}")

# Calcola la probabilità totale
total_prob = sum(t["probability"] for t in traces)
print(f"Probabilità totale: {total_prob}")

# Tracce per ogni scelta
from collections import defaultdict
by_choice = defaultdict(list)
for trace in traces:
    for decision in trace["decisions"]:
        by_choice[decision].append(trace)

for decision, related_traces in by_choice.items():
    print(f"\nDecisione {decision}: {len(related_traces)} tracce")
    avg_cost = sum(t["impacts"]["cost"] for t in related_traces) / len(related_traces)
    print(f"  Costo medio: {avg_cost:.2f}")
```

## Limitazioni

- **Complessità Computazionale**: Il numero di tracce cresce esponenzialmente con il numero di scelte parallele
- **Memoria**: L'albero di esecuzione completo può diventare molto grande per processi complessi
- **Tempo**: L'espansione completa può richiedere molto tempo per modelli grandi

**Suggerimento**: Usa l'opzione `--max-nodes` per limitare l'espansione in caso di modelli molto complessi.

## Troubleshooting

### Errore: "Connection refused"

**Problema**: Il server del simulatore o PACO non è in esecuzione.

**Soluzione**: Verifica che entrambi i server siano avviati:
```bash
# Terminale 1: Simulatore
cd simulator
python src/main.py

# Terminale 2: PACO
python -m src.server

# Terminale 3: Genera tracce
python generate_all_traces.py bpmn_file.json
```

### Errore: "Maximum nodes reached"

**Problema**: Il limite di nodi è stato raggiunto prima di completare l'espansione.

**Soluzione**: Aumenta il limite con `--max-nodes`:
```bash
python generate_all_traces.py bpmn_file.json --max-nodes 50000
```

### Output: "0 tracce estratte"

**Problema**: Il modello BPMN potrebbe avere errori o non raggiungere stati finali.

**Soluzione**: Verifica che:
1. Il file BPMN sia valido
2. Il modello abbia almeno un percorso completo
3. I server siano in esecuzione correttamente

## Riferimenti

- [PACO Documentation](docs/index.md)
- [Simulator README](simulator/README.md)
- [BPMN+CPI Specification](docs/installation_and_usage.md)
- [tree_expansion.ipynb](tree_expansion.ipynb) - Notebook originale su cui si basa questo script
