# 🎯 Sistema Generazione Tracce BPMN - Start Here

## 👋 Benvenuto!

Questo sistema ti permette di **generare tutte le possibili tracce di esecuzione** da un modello BPMN e salvarle nel formato JSON usato da PACO.

## 🚀 Quick Start (3 minuti)

### 1️⃣ Verifica i File

```bash
show_files.bat
```

Questo mostra tutti i file disponibili.

### 2️⃣ Avvia i Server

**Terminale 1:**
```bash
cd simulator
python src/main.py
```

**Terminale 2:**
```bash
python -m src.server
```

### 3️⃣ Testa il Sistema

```bash
test_trace_generation.bat
```

Se vedi "TEST COMPLETATO CON SUCCESSO!" sei pronto! 🎉

## 📚 Documentazione

### 🇮🇹 Italiano

- **[LEGGIMI_TRACCE.md](LEGGIMI_TRACCE.md)** ⭐ **INIZIA QUI**
  - Guida completa in italiano
  - Esempi pratici
  - Troubleshooting

- **[CHECKLIST_TRACCE.md](CHECKLIST_TRACCE.md)**
  - Checklist passo-passo
  - Comandi rapidi
  - Pro tips

### 🇬🇧 English

- **[GENERATE_TRACES_README.md](GENERATE_TRACES_README.md)**
  - Complete guide in English
  - Advanced usage
  - API reference

- **[TRACES_SUMMARY.md](TRACES_SUMMARY.md)**
  - Complete summary
  - Use cases
  - Examples

## 🛠️ Tool e Script

### Script Principali

| Script | Uso | Comando |
|--------|-----|---------|
| `generate_traces.bat` | Genera tracce | `generate_traces.bat modello.json` |
| `analyze_traces.bat` | Analizza tracce | `analyze_traces.bat tracce.json` |
| `test_trace_generation.bat` | Test rapido | `test_trace_generation.bat` |
| `show_files.bat` | Mostra file | `show_files.bat` |

### Script Python (Avanzato)

```bash
# Genera tracce
python generate_all_traces.py modello.json

# Analizza tracce
python analyze_traces.py tracce.json --export-csv risultati.csv
```

### Notebook Jupyter

```bash
jupyter notebook example_trace_analysis.ipynb
```

## 📖 Guide Rapide

### Per Principianti 🟢

1. Leggi [LEGGIMI_TRACCE.md](LEGGIMI_TRACCE.md) (sezione "Utilizzo Rapido")
2. Esegui `test_trace_generation.bat`
3. Prova con il tuo modello: `generate_traces.bat tuo_modello.json`

### Per Utenti Intermedi 🟡

1. Consulta [CHECKLIST_TRACCE.md](CHECKLIST_TRACCE.md)
2. Usa gli script batch per generazione e analisi
3. Esplora i risultati in CSV con Excel

### Per Utenti Avanzati 🔴

1. Studia [GENERATE_TRACES_README.md](GENERATE_TRACES_README.md)
2. Usa gli script Python con opzioni personalizzate
3. Analizza con il notebook Jupyter

## 🎓 Tutorial Video (Concettuale)

### Tutorial 1: Primo Test (5 min)
```
1. Avvia i server
2. Esegui: test_trace_generation.bat
3. Verifica i file generati
```

### Tutorial 2: Tuo Primo Modello (10 min)
```
1. Prepara un file BPMN
2. Esegui: generate_traces.bat modello.json
3. Esegui: analyze_traces.bat modello_traces.json
4. Apri risultati in Excel
```

### Tutorial 3: Analisi Avanzata (20 min)
```
1. Genera tracce da modello complesso
2. Apri example_trace_analysis.ipynb
3. Modifica per caricare le tue tracce
4. Esplora visualizzazioni e grafici
```

## 🆘 Problemi Comuni

### ❌ "Connection refused"
→ **Soluzione:** Avvia i server (vedi step 2️⃣)

### ❌ "File not found"
→ **Soluzione:** Verifica il percorso del file BPMN

### ❌ "0 tracce generate"
→ **Soluzione:** Testa con `simple_test_model.json`

### 📖 Più soluzioni: [LEGGIMI_TRACCE.md](LEGGIMI_TRACCE.md#troubleshooting)

## 📂 Struttura File

```
PACO/
├── generate_all_traces.py          ← Script generazione
├── analyze_traces.py               ← Script analisi
├── generate_traces.bat             ← Batch generazione (Windows)
├── analyze_traces.bat              ← Batch analisi (Windows)
├── test_trace_generation.bat       ← Test rapido
├── show_files.bat                  ← Mostra file
│
├── LEGGIMI_TRACCE.md              ← 📖 GUIDA PRINCIPALE (italiano)
├── CHECKLIST_TRACCE.md            ← Checklist rapida
├── GENERATE_TRACES_README.md      ← Guida completa (inglese)
├── TRACES_SUMMARY.md              ← Riepilogo
├── START_HERE.md                  ← Questo file
│
├── simple_test_model.json         ← Modello test
└── example_trace_analysis.ipynb   ← Notebook esempio
```

## 💡 Esempi Pratici

### Esempio 1: Test Velocissimo
```bash
test_trace_generation.bat
```
✅ 2 minuti - Verifica che tutto funzioni

### Esempio 2: Genera e Analizza
```bash
generate_traces.bat simple_test_model.json
analyze_traces.bat simple_test_model_traces.json
```
✅ 5 minuti - Vedi risultati completi

### Esempio 3: Il Tuo Modello
```bash
generate_traces.bat tuo_modello.json
analyze_traces.bat tuo_modello_traces.json
```
✅ Dipende dalla complessità

## 🎯 Workflow Consigliato

```
1. Test iniziale
   ↓
2. Genera tracce dal tuo modello
   ↓
3. Analizza i risultati
   ↓
4. Visualizza in Excel/Notebook
   ↓
5. Identifica tracce ottimali
   ↓
6. Applica al processo reale
```

## 📞 Supporto

- **Documentazione completa:** [LEGGIMI_TRACCE.md](LEGGIMI_TRACCE.md)
- **Troubleshooting:** [LEGGIMI_TRACCE.md#troubleshooting](LEGGIMI_TRACCE.md#troubleshooting)
- **FAQ:** [LEGGIMI_TRACCE.md#domande-frequenti-faq](LEGGIMI_TRACCE.md#domande-frequenti-faq)

## 🎁 Bonus

### Comandi Utili

```bash
# Mostra tutti i file del sistema
show_files.bat

# Test completo
test_trace_generation.bat

# Generazione personalizzata
python generate_all_traces.py modello.json --max-nodes 5000

# Analisi con scelte specifiche
python analyze_traces.py tracce.json --choice-labels C1 C2
```

### File Pronti

- ✅ `simple_test_model.json` - Per test immediati
- ✅ `example_trace_analysis.ipynb` - Analisi avanzate
- ✅ Script batch - Uso semplificato su Windows

## ✨ Prossimi Passi

1. ✅ Hai letto questo file
2. ⬜ Esegui `test_trace_generation.bat`
3. ⬜ Leggi [LEGGIMI_TRACCE.md](LEGGIMI_TRACCE.md)
4. ⬜ Genera tracce dal tuo modello
5. ⬜ Analizza i risultati
6. ⬜ 🎉 Celebra il successo!

---

## 📌 Link Veloci

| Cosa Vuoi Fare? | Vai A |
|-----------------|-------|
| **Iniziare subito** | [LEGGIMI_TRACCE.md](LEGGIMI_TRACCE.md) |
| **Checklist passo-passo** | [CHECKLIST_TRACCE.md](CHECKLIST_TRACCE.md) |
| **Guida dettagliata (EN)** | [GENERATE_TRACES_README.md](GENERATE_TRACES_README.md) |
| **Test rapido** | `test_trace_generation.bat` |
| **Analisi avanzata** | `example_trace_analysis.ipynb` |
| **Risolvi problemi** | [Troubleshooting](LEGGIMI_TRACCE.md#troubleshooting) |

---

**🎉 Sei pronto per iniziare!**

Esegui `test_trace_generation.bat` per il primo test! 🚀

---

*Ultima modifica: Gennaio 2026*  
*Versione: 1.0*
