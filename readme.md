Collecting workspace information# Job Matcher con ChromaDB

Benvenuto nel **Job Matcher**, un'applicazione web basata su Streamlit che utilizza **ChromaDB** per abbinare descrizioni di lavoro a curriculum. Questo progetto consente di caricare dataset di job post e curriculum, indicizzarli in un database vettoriale, e trovare i migliori match tra job post e curriculum utilizzando modelli di embedding.

---

## Caratteristiche principali

- **Indicizzazione di job post e curriculum**: Carica dataset di job post e curriculum e indicizzali in un database vettoriale persistente.
- **Ricerca basata su embedding**: Trova job post simili a una descrizione fornita dall'utente e abbina i migliori curriculum a quel job post.
- **Supporto per diversi tipi di file**: Curriculum in formato `.docx`, immagini (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`) e file `.ini` sono supportati.
- **Interfaccia utente intuitiva**: Un'app Streamlit per interagire con il sistema.

---

## Requisiti di sistema

- Python 3.8 o superiore
- Librerie Python elencate in `requirements.txt`
- Tesseract OCR (per estrarre testo da immagini)

---

## Installazione

1. **Clona il repository**
   ```bash
   git clone https://github.com/tuo-repo/job-matcher.git
   cd job-matcher
   ```

2. **Crea un ambiente virtuale**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Installa Tesseract OCR**
   - Su Ubuntu:
     ```bash
     sudo apt install tesseract-ocr
     ```
   - Su macOS:
     ```bash
     brew install tesseract
     ```
   - Su Windows:
     Scarica e installa Tesseract da [qui](https://github.com/tesseract-ocr/tesseract).

---

## Inserimento dei dati

### 1. **Scarica i dataset**
Il progetto utilizza dataset di job post e curriculum. Puoi scaricarli automaticamente utilizzando lo script download_data.py.

Esegui il comando:
```bash
python src/utils/download_data.py
```

Questo script scaricherà i seguenti dataset:
- **Job Posts**: Dataset di job post da Kaggle.
- **Resumes**: Dataset di curriculum in vari formati.

I file scaricati saranno salvati nella directory data.

---

### 2. **Inserisci i job post nel database**
Per indicizzare i job post nel database ChromaDB, esegui il seguente comando:
```bash
python main_ingestion.py
```

Questo script:
- Legge il dataset di job post da job_posts.
- Pulisce e normalizza i dati.
- Genera embedding per ogni job post utilizzando il modello `all-mpnet-base-v2`.
- Inserisce i dati nel database ChromaDB nella collezione `job_posts`.

---

### 3. **Inserisci i curriculum nel database**
Lo script main_ingestion.py si occupa anche di indicizzare i curriculum. Assicurati che i file di curriculum siano presenti nella directory `data/Resumes Datasets/`.

---

## Esecuzione dell'applicazione web

1. **Avvia l'app Streamlit**
   ```bash
   streamlit run main.py
   ```

2. **Interfaccia utente**
   - **Inserisci una descrizione di lavoro**: Incolla una descrizione di lavoro nel campo di testo.
   - **Trova il match**: Clicca sul pulsante "🚀 Trova match" per avviare la ricerca.
   - **Visualizza i risultati**: L'app mostrerà il job post più simile e i 5 curriculum migliori.

---

## Struttura del progetto

```
job-matcher/
├── chroma_db/                # Database vettoriale persistente
├── data/                     # Dataset di job post e curriculum
│   ├── job_posts/            # Dataset di job post
│   └── Resumes Datasets/     # Dataset di curriculum
├── src/                      # Codice sorgente
│   ├── insertion/            # Script per l'inserimento dei dati
│   └── utils/                # Utility per la gestione dei dati
├── main.py                   # Applicazione Streamlit
├── main_ingestion.py         # Script per l'inserimento dei dati
├── requirements.txt          # Dipendenze del progetto
└── README.md                 # Documentazione
```

---

## Dipendenze principali

- **Streamlit**: Per l'interfaccia utente.
- **ChromaDB**: Per il database vettoriale.
- **SentenceTransformers**: Per generare embedding.
- **Tesseract OCR**: Per estrarre testo da immagini.

---

## Debugging e risoluzione dei problemi

1. **Errore durante la connessione a ChromaDB**
   - Assicurati che la directory chroma_db esista e sia scrivibile.
   - Verifica che il percorso del database sia corretto.

2. **File non supportato**
   - Assicurati che i file di curriculum abbiano estensioni supportate (`.docx`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.ini`).

3. **Problemi con Tesseract OCR**
   - Verifica che Tesseract sia installato correttamente.
   - Aggiungi il percorso di Tesseract alle variabili di ambiente, se necessario.

---

## Contributi

Se vuoi contribuire al progetto, sentiti libero di aprire una pull request o segnalare problemi nella sezione Issues.

---

## Licenza

Questo progetto è distribuito sotto la licenza MIT.