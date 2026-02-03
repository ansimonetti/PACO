# Sistema di Generazione e Analisi Tracce BPMN

Sistema completo per generare tutte le possibili tracce di esecuzione da modelli BPMN e analizzarle nel formato JSON usato da PACO.

## 📋 Indice

1. [Cos'è](#cosè)
2. [Installazione](#installazione)
3. [Utilizzo Rapido](#utilizzo-rapido)
4. [File e Script](#file-e-script)
5. [Esempi](#esempi)
6. [Formato Dati](#formato-dati)
7. [Troubleshooting](#troubleshooting)

## Cos'è

Questo sistema permette di:

✅ **Generare** tutte le possibili tracce di esecuzione da un modello BPMN  
✅ **Analizzare** le tracce con statistiche e metriche  
✅ **Visualizzare** i risultati con grafici e tabelle  
✅ **Esportare** i dati in formati utilizzabili (JSON, CSV)  
✅ **Ottimizzare** identificando le tracce migliori (frontiera di Pareto)

## Installazione

### Prerequisiti

- Python 3.8 o superiore
- Server PACO in esecuzione
- Simulatore in esecuzione

### Setup

1. **Clona il repository** (se non l'hai già fatto)
   ```bash
   cd c:\Users\Emanuele\GithubRepo\PACO
   ```

2. **Installa le dipendenze Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verifica che i file siano presenti**
   - `generate_all_traces.py`
   - `analyze_traces.py`
   - `GENERATE_TRACES_README.md`

## Utilizzo Rapido

### Passo 1: Avvia i Server

**Terminale 1 - Simulatore:**
```bash
cd simulator
python src/main.py
```
→ Server in esecuzione su `http://127.0.0.1:8001`

**Terminale 2 - PACO:**
```bash
python -m src.server
```
→ Server in esecuzione su `http://127.0.0.1:8000`

### Passo 2: Genera le Tracce

**Opzione A - Script Batch (Windows):**
```bash
generate_traces.bat tuo_modello.json
```

**Opzione B - Script Python:**
```bash
python generate_all_traces.py tuo_modello.json
```

Questo crea:
- `tuo_modello_traces.json` - Tutte le tracce
- `tuo_modello_execution_tree.json` - Albero di esecuzione completo

### Passo 3: Analizza le Tracce

**Opzione A - Script Batch (Windows):**
```bash
analyze_traces.bat tuo_modello_traces.json
```

**Opzione B - Script Python:**
```bash
python analyze_traces.py tuo_modello_traces.json --export-csv risultati.csv
```

### Passo 4: Visualizza i Risultati

- **JSON**: Apri il file con un editor di testo
- **CSV**: Apri con Excel o LibreOffice
- **Notebook**: Usa `example_trace_analysis.ipynb` per analisi avanzate

## File e Script

### Script Principali

| File | Descrizione |
|------|-------------|
| `generate_all_traces.py` | Genera tutte le tracce possibili |
| `analyze_traces.py` | Analizza le tracce generate |
| `generate_traces.bat` | Script batch per generazione (Windows) |
| `analyze_traces.bat` | Script batch per analisi (Windows) |
| `test_trace_generation.bat` | Test rapido del sistema |

### File di Esempio

| File | Descrizione |
|------|-------------|
| `simple_test_model.json` | Modello BPMN semplice per test |
| `example_trace_analysis.ipynb` | Notebook con esempio completo |

### Documentazione

| File | Descrizione |
|------|-------------|
| `GENERATE_TRACES_README.md` | Guida dettagliata (inglese) |
| `TRACES_SUMMARY.md` | Riepilogo completo |
| `LEGGIMI_TRACCE.md` | Questa guida (italiano) |

## Esempi

### Esempio 1: Test Rapido

Usa il modello di test incluso:

```bash
# Windows
test_trace_generation.bat

# Linux/Mac
python generate_all_traces.py simple_test_model.json
python analyze_traces.py test_traces.json
```

### Esempio 2: Modello Semplice con Scelta

Modello: `T1, (T2 / [C1] T3)`

```bash
python generate_all_traces.py simple_choice.json
```

Risultato: 2 tracce
- Traccia 1: T1 → T2
- Traccia 2: T1 → T3

### Esempio 3: Modello con Parallelismo

Modello: `(T1 / [C1] T2) || (T3 / [C2] T4)`

```bash
python generate_all_traces.py parallel_model.json --max-nodes 1000
```

Risultato: 4 tracce
- T1 || T3
- T1 || T4
- T2 || T3
- T2 || T4

### Esempio 4: Analisi Avanzata con Notebook

```bash
jupyter notebook example_trace_analysis.ipynb
```

Il notebook mostra:
- Caricamento dati
- Statistiche descrittive
- Grafici e visualizzazioni
- Frontiera di Pareto
- Export risultati

## Formato Dati

### Input: Modello BPMN (JSON)

```json
{
  "expression": "T1, (T2 / [C1] T3)",
  "impacts_names": ["cost", "time"],
  "impacts": {
    "T1": {"cost": 5.0, "time": 10.0},
    "T2": {"cost": 3.0, "time": 5.0},
    "T3": {"cost": 4.0, "time": 8.0}
  },
  "durations": {
    "T1": [10, 10],
    "T2": [5, 5],
    "T3": [8, 8]
  },
  "delays": {"C1": 0},
  "probabilities": {},
  "loop_probability": {},
  "loop_round": {}
}
```

### Output: Tracce (JSON)

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
      "impacts": {"cost": 8.0, "time": 15.0},
      "probability": 1.0,
      "execution_time": 15.0,
      "is_final": true
    },
    {
      "id": 1,
      "decisions": ["t1", "t3"],
      "impacts": {"cost": 9.0, "time": 18.0},
      "probability": 1.0,
      "execution_time": 18.0,
      "is_final": true
    }
  ]
}
```

### Output: CSV

```csv
trace_id,decisions,probability,execution_time,cost,time
0,t1 -> t2,1.0,15.0,8.0,15.0
1,t1 -> t3,1.0,18.0,9.0,18.0
```

## Troubleshooting

### ❌ Errore: "Connection refused"

**Problema:** Server non in esecuzione

**Soluzione:**
```bash
# Terminale 1
cd simulator
python src/main.py

# Terminale 2
python -m src.server
```

### ❌ Errore: "File not found"

**Problema:** File BPMN non trovato

**Soluzione:**
```bash
# Verifica che il file esista
dir tuo_modello.json

# Usa il percorso completo
python generate_all_traces.py C:\path\to\tuo_modello.json
```

### ❌ Errore: "Maximum nodes reached"

**Problema:** Modello troppo complesso

**Soluzione:**
```bash
# Aumenta il limite di nodi
python generate_all_traces.py modello.json --max-nodes 10000
```

### ❌ Output: "0 tracce generate"

**Problema:** Modello non valido o senza percorsi completi

**Soluzione:**
1. Verifica la sintassi del modello BPMN
2. Controlla che ci siano percorsi completi
3. Verifica i log dei server per errori

### ⚠️ Server non risponde

**Problema:** Timeout o errore di connessione

**Soluzione:**
1. Verifica che i server siano avviati
2. Controlla che le porte 8000 e 8001 siano libere
3. Riavvia i server

### 🐌 Generazione molto lenta

**Problema:** Modello con molte combinazioni

**Soluzione:**
1. Usa `--max-nodes` per limitare l'esplorazione
2. Semplifica il modello se possibile
3. Considera di processare solo parti del modello

## Opzioni Avanzate

### Limitare il Numero di Nodi

Per modelli molto grandi:

```bash
python generate_all_traces.py modello.json --max-nodes 5000
```

### Personalizzare i Nomi dei File

```bash
python generate_all_traces.py modello.json \
    -o mie_tracce.json \
    --execution-tree-output mio_albero.json
```

### Analizzare Scelte Specifiche

```bash
python analyze_traces.py tracce.json --choice-labels C1 C2 N1
```

### Esportare in CSV

```bash
python analyze_traces.py tracce.json --export-csv output.csv
```

## Best Practices

### 1. Test Incrementale

Inizia con modelli semplici e aumenta gradualmente la complessità:

```bash
# 1. Modello semplice
python generate_all_traces.py simple_test_model.json

# 2. Modello medio
python generate_all_traces.py medium_model.json --max-nodes 1000

# 3. Modello complesso
python generate_all_traces.py complex_model.json --max-nodes 10000
```

### 2. Verifica i Risultati

Dopo ogni generazione, verifica che le tracce siano corrette:

```bash
python analyze_traces.py tracce.json
```

### 3. Salva i Risultati

Usa nomi descrittivi per i file:

```bash
python generate_all_traces.py modello.json \
    -o "$(date +%Y%m%d)_modello_traces.json"
```

### 4. Monitora le Performance

Per modelli grandi, monitora:
- Numero di nodi generati
- Tempo di esecuzione
- Memoria utilizzata

## Domande Frequenti (FAQ)

### Q: Quante tracce posso generare?

**A:** Dipende dal modello. Con scelte parallele, il numero cresce esponenzialmente. Usa `--max-nodes` per limitare.

### Q: Posso usare questo con modelli BPMN da altre fonti?

**A:** Sì, purché siano nel formato JSON di PACO. Consulta la documentazione per il formato richiesto.

### Q: Come identifico la traccia migliore?

**A:** Usa `analyze_traces.py` per trovare:
- Tracce con costo minimo
- Tracce con tempo minimo
- Tracce sulla frontiera di Pareto (ottimali su tutte le dimensioni)

### Q: Posso modificare le tracce generate?

**A:** Sì, il file JSON è modificabile. Mantieni la struttura originale per compatibilità.

### Q: Come visualizzo l'albero di esecuzione?

**A:** Usa il file `*_execution_tree.json` con tool di visualizzazione JSON o il notebook di esempio.

## Supporto e Contributi

### Hai trovato un bug?

1. Verifica con il test rapido: `test_trace_generation.bat`
2. Controlla i log dei server
3. Consulta la sezione Troubleshooting

### Vuoi contribuire?

Possibili miglioramenti:
- Supporto per più formati di output
- Ottimizzazioni per modelli grandi
- Visualizzazioni interattive
- Integrazione con altri tool BPMN

## Riferimenti

- [GENERATE_TRACES_README.md](GENERATE_TRACES_README.md) - Documentazione dettagliata
- [TRACES_SUMMARY.md](TRACES_SUMMARY.md) - Riepilogo completo
- [tree_expansion.ipynb](tree_expansion.ipynb) - Notebook originale
- [docs/](docs/) - Documentazione generale PACO

## Licenza

Vedi [LICENSE.txt](LICENSE.txt) per i dettagli.

---

**Versione:** 1.0  
**Ultima modifica:** Gennaio 2026  
**Autore:** Basato su tree_expansion.ipynb e adattato per uso generale

🎉 **Buon lavoro con PACO!**
