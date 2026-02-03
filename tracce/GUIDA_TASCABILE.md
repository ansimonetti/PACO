# 📋 Guida Tascabile - Generazione Tracce BPMN

**Sistema per generare e analizzare tutte le tracce di esecuzione da modelli BPMN**

---

## ⚡ Quick Reference

### Comandi Essenziali

```bash
# Test sistema
test_trace_generation.bat

# Genera tracce
generate_traces.bat modello.json

# Analizza tracce
analyze_traces.bat modello_traces.json

# Mostra file disponibili
show_files.bat
```

---

## 🔧 Setup (Prima Volta)

**1. Avvia Server (2 terminali):**

Terminale 1:
```bash
cd simulator
python src/main.py
```

Terminale 2:
```bash
python -m src.server
```

**2. Test:**
```bash
test_trace_generation.bat
```

Aspetta: "TEST COMPLETATO CON SUCCESSO!" ✅

---

## 📝 Workflow Standard

```
1. Avvia server → 2. Genera tracce → 3. Analizza → 4. Visualizza
```

**1. Avvia Server:**
- Simulatore (porta 8001)
- PACO (porta 8000)

**2. Genera Tracce:**
```bash
generate_traces.bat tuo_modello.json
```
Output: `tuo_modello_traces.json`

**3. Analizza:**
```bash
analyze_traces.bat tuo_modello_traces.json
```
Output: `tuo_modello_traces_summary.csv`

**4. Visualizza:**
- JSON: Editor di testo
- CSV: Excel
- Avanzato: `example_trace_analysis.ipynb`

---

## 🛠️ Script Python (Opzioni)

### Generazione

```bash
# Base
python generate_all_traces.py modello.json

# Con limiti
python generate_all_traces.py modello.json --max-nodes 1000

# Output personalizzato
python generate_all_traces.py modello.json \
    -o custom_traces.json \
    --execution-tree-output custom_tree.json
```

### Analisi

```bash
# Base
python analyze_traces.py tracce.json

# Con export CSV
python analyze_traces.py tracce.json --export-csv output.csv

# Analizza scelte specifiche
python analyze_traces.py tracce.json --choice-labels C1 C2
```

---

## 📊 Formato File

### Input (BPMN JSON)

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
  }
}
```

### Output (Tracce JSON)

```json
{
  "total_traces": 2,
  "traces": [
    {
      "id": 0,
      "decisions": ["t1", "t2"],
      "impacts": {"cost": 8.0, "time": 15.0},
      "probability": 1.0,
      "execution_time": 15.0
    }
  ]
}
```

---

## 🐛 Troubleshooting Veloce

| Errore | Causa | Soluzione |
|--------|-------|-----------|
| Connection refused | Server non attivo | Avvia server |
| File not found | Percorso errato | Verifica percorso |
| 0 tracce | Modello non valido | Usa `simple_test_model.json` |
| Max nodes reached | Modello complesso | Usa `--max-nodes` |

---

## 📚 Documentazione

| Documento | Contenuto |
|-----------|-----------|
| **START_HERE.md** | Punto di partenza |
| **LEGGIMI_TRACCE.md** | Guida completa IT |
| **CHECKLIST_TRACCE.md** | Checklist passo-passo |
| **GENERATE_TRACES_README.md** | Guida dettagliata EN |

---

## 🎯 Casi d'Uso Comuni

### 1. Trova Traccia con Costo Minimo
```bash
python analyze_traces.py tracce.json
```
Cerca nella sezione "TRACCE OTTIMALI PER DIMENSIONE"

### 2. Identifica Frontiera di Pareto
Leggi output di `analyze_traces.py` sezione "FRONTIERA DI PARETO"

### 3. Confronta Scelte
```bash
python analyze_traces.py tracce.json --choice-labels C1 C2
```

### 4. Export per Excel
```bash
analyze_traces.bat tracce.json
```
Apri file CSV generato

---

## 💡 Tips

✅ Inizia con modelli semplici  
✅ Usa nomi descrittivi per i file  
✅ Monitora i log dei server  
✅ Salva risultati con timestamp  
✅ Usa `--max-nodes` per modelli grandi  

---

## 📞 Aiuto Rapido

**Problema?** → Consulta [LEGGIMI_TRACCE.md](LEGGIMI_TRACCE.md#troubleshooting)

**Test non passa?** →
1. Verifica server attivi
2. Controlla porte 8000/8001 libere
3. Esegui: `test_trace_generation.bat`

**Serve esempio?** →
- File test: `simple_test_model.json`
- Notebook: `example_trace_analysis.ipynb`

---

## ⚙️ Configurazione Avanzata

### Cambia Porte Server

In `generate_all_traces.py`:
```python
SIMULATOR_PORT = 8001
SOLVER_PORT = 8000
```

### Aumenta Limite Nodi

```bash
python generate_all_traces.py modello.json --max-nodes 10000
```

### Export Personalizzato

```bash
python analyze_traces.py tracce.json \
    --export-csv risultati_$(date +%Y%m%d).csv
```

---

## 📦 File Inclusi

**Script:**
- `generate_all_traces.py`
- `analyze_traces.py`
- `generate_traces.bat` (Windows)
- `analyze_traces.bat` (Windows)
- `test_trace_generation.bat`

**Esempi:**
- `simple_test_model.json`
- `example_trace_analysis.ipynb`

**Docs:**
- `START_HERE.md` ← Inizio
- `LEGGIMI_TRACCE.md` ← Guida completa
- `CHECKLIST_TRACCE.md` ← Checklist
- `GUIDA_TASCABILE.md` ← Questo file

---

## 🚀 Inizia Ora

```bash
# 1. Test
test_trace_generation.bat

# 2. Il tuo modello
generate_traces.bat modello.json

# 3. Analizza
analyze_traces.bat modello_traces.json

# 4. 🎉 Fatto!
```

---

**Per stampare:** Salva come PDF → Stampa → Tieni a portata di mano! 📄

---

*Ultima modifica: Gennaio 2026 | v1.0*  
*© PACO - Process Analysis and Constraint Optimization*
