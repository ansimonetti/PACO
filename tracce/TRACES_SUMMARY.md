# Generazione e Analisi Tracce BPMN - Riepilogo

## 📁 File Creati

### Script Principali

1. **`generate_all_traces.py`**
   - Script Python per generare tutte le possibili tracce di esecuzione
   - Usa il simulatore per esplorare tutti i percorsi
   - Salva le tracce nel formato JSON usato da PACO

2. **`analyze_traces.py`**
   - Script Python per analizzare le tracce generate
   - Calcola statistiche, trova tracce ottimali, identifica la frontiera di Pareto
   - Può esportare i risultati in formato CSV

3. **`generate_traces.bat`** (Windows)
   - Script batch per facilitare la generazione delle tracce
   - Gestisce automaticamente i nomi dei file di output

4. **`analyze_traces.bat`** (Windows)
   - Script batch per facilitare l'analisi delle tracce
   - Esporta automaticamente i risultati in CSV

### Documentazione

5. **`GENERATE_TRACES_README.md`**
   - Guida completa all'uso degli script
   - Esempi di utilizzo
   - Risoluzione problemi comuni

### Notebook di Esempio

6. **`example_trace_analysis.ipynb`**
   - Esempio completo in Jupyter Notebook
   - Mostra come usare tutti gli strumenti
   - Include visualizzazioni e analisi avanzate

## 🚀 Quick Start

### 1. Avvia i Server

**Terminale 1 - Simulatore:**
```bash
cd simulator
python src/main.py
```

**Terminale 2 - PACO:**
```bash
python -m src.server
```

### 2. Genera le Tracce

**Windows:**
```bash
generate_traces.bat bpmn_fig8_bound_135_15.json
```

**Linux/Mac:**
```bash
python generate_all_traces.py bpmn_fig8_bound_135_15.json
```

### 3. Analizza le Tracce

**Windows:**
```bash
analyze_traces.bat bpmn_fig8_bound_135_15_traces.json
```

**Linux/Mac:**
```bash
python analyze_traces.py bpmn_fig8_bound_135_15_traces.json --export-csv results.csv
```

## 📊 Formato Output

### File delle Tracce (JSON)

```json
{
  "bpmn": {
    "expression": "T1, (T2 / [C1] T3)",
    "impacts_names": ["cost", "time"]
  },
  "total_traces": 2,
  "traces": [
    {
      "id": 0,
      "decisions": ["t1", "t2"],
      "impacts": {
        "cost": 10.0,
        "time": 15.0
      },
      "probability": 1.0,
      "execution_time": 15.0,
      "is_final": true
    }
  ]
}
```

### File CSV (esportato da analyze_traces)

| trace_id | decisions | probability | execution_time | cost | time |
|----------|-----------|-------------|----------------|------|------|
| 0        | t1 -> t2  | 1.0         | 15.0           | 10.0 | 15.0 |
| 1        | t1 -> t3  | 1.0         | 20.0           | 12.0 | 20.0 |

## 📖 Casi d'Uso

### 1. Ottimizzazione dei Processi
Identifica le tracce con costo minimo, tempo minimo o altri obiettivi.

```bash
python analyze_traces.py traces.json
```

### 2. Analisi di Pareto
Trova le tracce non dominate (ottimali su tutte le dimensioni).

```python
# Nel notebook o script Python
from analyze_traces import find_pareto_frontier
find_pareto_frontier(traces, ['cost', 'time'])
```

### 3. Confronto Decisioni
Analizza l'impatto di scelte specifiche.

```bash
python analyze_traces.py traces.json --choice-labels C1 C2
```

### 4. Export per Analisi Esterne
Esporta in CSV per usare con Excel, R, o altri strumenti.

```bash
python analyze_traces.py traces.json --export-csv output.csv
```

## 🔧 Configurazione

### Modifica la Porta del Simulatore

In `generate_all_traces.py`:
```python
SIMULATOR_PORT = 8001  # Cambia qui
SOLVER_PORT = 8000     # Cambia qui
```

### Limita il Numero di Nodi

Per modelli molto grandi:
```bash
python generate_all_traces.py large_model.json --max-nodes 5000
```

## 🐛 Troubleshooting

### Errore: "Connection refused"
**Causa:** Server non in esecuzione
**Soluzione:** Avvia simulatore e server PACO

### Errore: "Maximum nodes reached"
**Causa:** Modello troppo complesso
**Soluzione:** Aumenta `--max-nodes` o semplifica il modello

### Output: "0 tracce"
**Causa:** Modello BPMN non valido o senza percorsi completi
**Soluzione:** Verifica la sintassi del modello BPMN

## 📚 Documentazione Correlata

- [GENERATE_TRACES_README.md](GENERATE_TRACES_README.md) - Documentazione dettagliata
- [tree_expansion.ipynb](tree_expansion.ipynb) - Notebook originale (più complesso)
- [example_trace_analysis.ipynb](example_trace_analysis.ipynb) - Esempio di analisi completa
- [docs/](docs/) - Documentazione PACO generale

## 💡 Esempi Rapidi

### Esempio 1: Generazione Base
```bash
# Genera tracce
python generate_all_traces.py model.json

# Output: all_traces.json, complete_execution_tree.json
```

### Esempio 2: Con Nome Personalizzato
```bash
python generate_all_traces.py model.json -o my_traces.json
```

### Esempio 3: Analisi Completa
```bash
# Genera
python generate_all_traces.py model.json -o traces.json

# Analizza
python analyze_traces.py traces.json --export-csv summary.csv
```

### Esempio 4: Nel Notebook
```python
# Apri example_trace_analysis.ipynb
jupyter notebook example_trace_analysis.ipynb

# Esegui tutte le celle per un'analisi completa
```

## 🎯 Prossimi Sviluppi

Possibili estensioni:
- [ ] Supporto per analisi temporale (evoluzione nel tempo)
- [ ] Integrazione con tool di visualizzazione BPMN
- [ ] Export in formati aggiuntivi (XML, Excel)
- [ ] Analisi di sensibilità automatica
- [ ] Confronto tra diverse versioni del modello
- [ ] Suggerimenti automatici per l'ottimizzazione

## 📞 Supporto

Per problemi o domande:
1. Controlla [GENERATE_TRACES_README.md](GENERATE_TRACES_README.md)
2. Verifica che i server siano in esecuzione
3. Controlla i log dei server per errori dettagliati

## ✅ Checklist Utilizzo

- [ ] Server simulatore avviato (`cd simulator && python src/main.py`)
- [ ] Server PACO avviato (`python -m src.server`)
- [ ] File BPMN valido e accessibile
- [ ] Python e dipendenze installate
- [ ] Spazio su disco sufficiente per i risultati

## 🎉 Successo!

Una volta completati questi passaggi, avrai:
- ✅ Tutte le tracce possibili generate
- ✅ Analisi statistiche complete
- ✅ Visualizzazioni dei risultati
- ✅ Export in formati utilizzabili
- ✅ Identificazione delle tracce ottimali

Buon lavoro con PACO! 🚀
