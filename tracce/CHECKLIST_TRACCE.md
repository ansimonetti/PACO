# ✅ Checklist Rapida - Generazione Tracce BPMN

## 🚀 Setup Iniziale (Una Volta Sola)

- [ ] Python 3.8+ installato
- [ ] Repository clonato
- [ ] Dipendenze installate: `pip install -r requirements.txt`
- [ ] File presenti:
  - [ ] `generate_all_traces.py`
  - [ ] `analyze_traces.py`
  - [ ] `generate_traces.bat` (Windows)
  - [ ] `analyze_traces.bat` (Windows)

## 🔧 Prima di Ogni Esecuzione

- [ ] **Terminale 1:** Simulatore avviato
  ```bash
  cd simulator
  python src/main.py
  ```
  → Verifica su http://127.0.0.1:8001/docs

- [ ] **Terminale 2:** Server PACO avviato
  ```bash
  python -m src.server
  ```
  → Verifica su http://127.0.0.1:8000/docs

- [ ] Porte 8000 e 8001 libere e accessibili

## 📝 Generazione Tracce

### Opzione 1: Script Batch (Windows) ⭐ CONSIGLIATO

- [ ] Prepara il file BPMN (es: `modello.json`)
- [ ] Esegui:
  ```bash
  generate_traces.bat modello.json
  ```
- [ ] Verifica file generati:
  - [ ] `modello_traces.json`
  - [ ] `modello_execution_tree.json`

### Opzione 2: Script Python

- [ ] Esegui:
  ```bash
  python generate_all_traces.py modello.json
  ```
- [ ] Opzionale - Personalizza output:
  ```bash
  python generate_all_traces.py modello.json \
      -o custom_traces.json \
      --execution-tree-output custom_tree.json \
      --max-nodes 5000
  ```

## 📊 Analisi Tracce

### Opzione 1: Script Batch (Windows) ⭐ CONSIGLIATO

- [ ] Esegui:
  ```bash
  analyze_traces.bat modello_traces.json
  ```
- [ ] Verifica file CSV generato:
  - [ ] `modello_traces_summary.csv`

### Opzione 2: Script Python

- [ ] Esegui:
  ```bash
  python analyze_traces.py modello_traces.json
  ```
- [ ] Leggi output nel terminale:
  - [ ] Statistiche descrittive
  - [ ] Tracce ottimali
  - [ ] Frontiera di Pareto

- [ ] Opzionale - Export CSV:
  ```bash
  python analyze_traces.py modello_traces.json --export-csv risultati.csv
  ```

- [ ] Opzionale - Analizza scelte specifiche:
  ```bash
  python analyze_traces.py modello_traces.json --choice-labels C1 C2
  ```

## 📈 Visualizzazione Risultati

### JSON
- [ ] Apri `modello_traces.json` con editor di testo
- [ ] Verifica campo `total_traces`
- [ ] Esamina array `traces`

### CSV
- [ ] Apri `modello_traces_summary.csv` con Excel
- [ ] Crea pivot table per analisi
- [ ] Crea grafici

### Notebook (Avanzato)
- [ ] Apri `example_trace_analysis.ipynb`
- [ ] Modifica nome file input
- [ ] Esegui tutte le celle
- [ ] Visualizza grafici generati

## 🧪 Test Rapido (Prima Volta)

- [ ] Esegui test automatico:
  ```bash
  test_trace_generation.bat
  ```
- [ ] Verifica output:
  - [ ] `test_traces.json` creato
  - [ ] `test_execution_tree.json` creato
  - [ ] `test_summary.csv` creato
- [ ] Messaggio "TEST COMPLETATO CON SUCCESSO!" visualizzato

## 🐛 Troubleshooting Veloce

### Errore "Connection refused"
- [ ] Verifica server simulatore attivo (porta 8001)
- [ ] Verifica server PACO attivo (porta 8000)
- [ ] Riavvia i server se necessario

### Errore "File not found"
- [ ] Verifica percorso file BPMN corretto
- [ ] Usa percorso assoluto se necessario
- [ ] Verifica estensione file `.json`

### "0 tracce generate"
- [ ] Verifica sintassi BPMN valida
- [ ] Controlla log server per errori
- [ ] Testa con `simple_test_model.json`

### Esecuzione lenta
- [ ] Usa `--max-nodes 1000` per limitare
- [ ] Verifica complessità modello (numero scelte parallele)
- [ ] Considera semplificazione modello

## 📋 Output Attesi

### Dopo Generazione
- [x] File tracce JSON creato
- [x] File albero esecuzione creato
- [x] Numero tracce > 0
- [x] Nessun errore nel log

### Dopo Analisi
- [x] Statistiche visualizzate
- [x] Tracce ottimali identificate
- [x] Frontiera Pareto calcolata (se 2+ dimensioni)
- [x] CSV esportato (se richiesto)

## 🎯 Workflow Consigliato

1. **Setup** (una volta):
   - [ ] Installa dipendenze
   - [ ] Testa con modello semplice

2. **Per ogni nuovo modello**:
   - [ ] Avvia server (se non già attivi)
   - [ ] Genera tracce: `generate_traces.bat modello.json`
   - [ ] Analizza: `analyze_traces.bat modello_traces.json`
   - [ ] Esamina risultati in CSV

3. **Analisi avanzata** (opzionale):
   - [ ] Apri notebook `example_trace_analysis.ipynb`
   - [ ] Carica tracce generate
   - [ ] Crea visualizzazioni personalizzate

## 📚 Documentazione Rapida

| Domanda | Documento |
|---------|-----------|
| Come si usa tutto? | `LEGGIMI_TRACCE.md` |
| Dettagli completi | `GENERATE_TRACES_README.md` |
| Riepilogo veloce | `TRACES_SUMMARY.md` |
| Esempio pratico | `example_trace_analysis.ipynb` |

## ⚡ Comandi Più Usati

```bash
# Generazione base
generate_traces.bat modello.json

# Analisi base
analyze_traces.bat modello_traces.json

# Test rapido
test_trace_generation.bat

# Generazione con limiti
python generate_all_traces.py modello.json --max-nodes 1000

# Analisi con export
python analyze_traces.py tracce.json --export-csv output.csv
```

## ✨ Pro Tips

💡 Usa sempre nomi descrittivi per i file  
💡 Inizia con modelli semplici per testare  
💡 Monitora i log dei server in caso di problemi  
💡 Salva i risultati con timestamp: `20260121_tracce.json`  
💡 Usa il notebook per analisi esplorative  
💡 Export in CSV per condividere con altri  

## 🎉 Tutto Pronto!

Se hai completato questa checklist, sei pronto per:
- ✅ Generare tracce da qualsiasi modello BPMN
- ✅ Analizzare i risultati
- ✅ Ottimizzare i processi
- ✅ Identificare le soluzioni migliori

---

**Ultimo aggiornamento:** Gennaio 2026  
**Per supporto:** Vedi `LEGGIMI_TRACCE.md` sezione Troubleshooting
