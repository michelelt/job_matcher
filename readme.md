
# Collecting Workspace Information # Job Matcher with ChromaDB

Welcome to **Job Matcher**, a Streamlit-based web application that uses **ChromaDB** to match job descriptions with resumes. This project allows you to upload datasets of job posts and resumes, index them in a vector database, and find the best matches between job posts and resumes using embedding models.

---

## Main Features

- **Indexing job posts and resumes**: Upload datasets of job posts and resumes and index them in a persistent vector database.  
- **Embedding-based search**: Find job posts similar to a user-provided description and match the best resumes to that job post.  
- **Support for multiple file types**: Resumes in `.docx` format, images (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`), and `.ini` files are supported.  
- **User-friendly interface**: A Streamlit app to interact with the system.

---

## System Requirements

- Python 3.8 or higher  
- Python libraries listed in `requirements.txt`  
- Tesseract OCR (for extracting text from images)

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-repo/job-matcher.git
   cd job-matcher
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**

   - On Ubuntu:
     ```bash
     sudo apt install tesseract-ocr
     ```
   - On macOS:
     ```bash
     brew install tesseract
     ```
   - On Windows:  
     Download and install Tesseract from [here](https://github.com/tesseract-ocr/tesseract).

---

## Data Ingestion

### 1. **Download datasets**  
The project uses datasets of job posts and resumes. You can download them automatically using the `download_data.py` script.

Run:  
```bash
python src/utils/download_data.py
```

This script downloads the following datasets:  
- **Job Posts**: job posts dataset from Kaggle.  
- **Resumes**: dataset of resumes in various formats.

The files will be saved in the `data` directory.

---

### 2. **Ingest job posts into the database**  
To index the job posts into the ChromaDB database, run:  

```bash
python main_ingestion.py
```

This script:  
- Reads the job posts dataset from `job_posts`.  
- Cleans and normalizes the data.  
- Generates embeddings for each job post using the `all-mpnet-base-v2` model.  
- Inserts data into the ChromaDB collection named `job_posts`.

---

### 3. **Ingest resumes into the database**  
The `main_ingestion.py` script also indexes resumes. Make sure the resume files are present in the `data/Resumes Datasets/` directory.

---

## Running the Web Application

1. **Start the Streamlit app**

   ```bash
   streamlit run main.py
   ```

2. **User interface**

   - **Enter a job description**: Paste a job description into the text box.  
   - **Find matches**: Click the "🚀 Find match" button to start the search.  
   - **View results**: The app shows the most similar job post and the top 5 matching resumes.

---

## Project Structure

```
job-matcher/
├── chroma_db/                # Persistent vector database
├── data/                     # Job posts and resumes datasets
│   ├── job_posts/            # Job posts dataset
│   └── Resumes Datasets/     # Resumes dataset
├── src/                      # Source code
│   ├── insertion/            # Scripts for data ingestion
│   └── utils/                # Utilities for data management
├── main.py                   # Streamlit application
├── main_ingestion.py         # Data ingestion script
├── requirements.txt          # Project dependencies
└── README.md                 # Documentation
```

---

## Main Dependencies

- **Streamlit**: For the user interface.  
- **ChromaDB**: For the vector database.  
- **SentenceTransformers**: To generate embeddings.  
- **Tesseract OCR**: To extract text from images.

---

## Debugging and Troubleshooting

1. **Error connecting to ChromaDB**  
   - Ensure the `chroma_db` directory exists and is writable.  
   - Verify the database path is correct.

2. **Unsupported file**  
   - Make sure resume files have supported extensions (`.docx`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.ini`).

3. **Tesseract OCR issues**  
   - Verify Tesseract is correctly installed.  
   - Add Tesseract to your environment path if needed.

---

## Contributions

If you want to contribute, feel free to open a pull request or report issues in the Issues section.

---

## License

This project is licensed under the MIT License.
