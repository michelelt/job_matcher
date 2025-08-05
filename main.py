import streamlit as st
import chromadb
import numpy as np
import uuid # Per generare ID unici
from sentence_transformers import SentenceTransformer # Importa la libreria per gli embedding
import os # Per operazioni sul file system

# Tentativo di importare python-docx per i file .docx
try:
    import docx
except ImportError:
    docx = None
    st.warning("La libreria 'python-docx' non è installata. Non sarà possibile visualizzare l'anteprima dei file .docx.")
    st.info("Per installarla, esegui: `pip install python-docx`")


# --- Configurazione della pagina Streamlit ---
st.set_page_config(
    page_title="Job Matcher con ChromaDB",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Caricamento del modello di embedding ---
@st.cache_resource # Memorizza in cache il modello per evitare di ricaricarlo ad ogni esecuzione
def load_embedding_model():
    """
    Carica il modello di embedding SentenceTransformer.
    """
    with st.spinner("Caricamento del modello di embedding 'all-mpnet-base-v2'... Questo potrebbe richiedere alcuni secondi al primo avvio."):
        model = SentenceTransformer('all-mpnet-base-v2')
    st.success("Modello di embedding caricato!")
    return model

# Carica il modello all'avvio dell'applicazione
embedding_model = load_embedding_model()

# --- Funzione per la generazione degli Embedding (ora usa il modello reale) ---
def get_embedding(text: str) -> list[float]:
    """
    Genera un embedding per il testo dato usando il modello 'all-mpnet-base-v2'.
    """
    return embedding_model.encode(text).tolist()

# --- Inizializzazione del client ChromaDB e delle collezioni ---
# Usiamo un client persistente per connetterci al database esistente.
# In un'applicazione di produzione, potresti connetterti a un server Chroma remoto.
try:
    client = chromadb.PersistentClient(path="./chroma_db")
    st.success("Connesso a ChromaDB (modalità persistente).")
except Exception as e:
    st.error(f"Errore durante la connessione a ChromaDB: {e}")
    st.stop() # Ferma l'esecuzione se non riusciamo a connetterci

# Recupera le collezioni esistenti
try:
    job_posts_collection = client.get_or_create_collection(name="job_posts")
    resumes_collection = client.get_or_create_collection(name="resumes")
    st.info("Collezioni 'job_posts' e 'resumes' caricate.")
    
    # Verifica che le collezioni non siano vuote
    if job_posts_collection.count() == 0:
        st.warning("Attenzione: La collezione 'job_posts' è vuota. Assicurati che il database sia stato popolato in precedenza.")
    if resumes_collection.count() == 0:
        st.warning("Attenzione: La collezione 'resumes' è vuota. Assicurati che il database sia stato popolato in precedenza.")

except Exception as e:
    st.error(f"Errore durante il recupero delle collezioni: {e}")
    st.stop()

# --- Funzione per visualizzare il contenuto del curriculum in base al tipo di file ---
def display_resume_content(file_path: str):
    """
    Visualizza il contenuto di un file di curriculum in Streamlit.
    Supporta immagini, DOCX e file di testo generici.
    """
    if not os.path.exists(file_path):
        st.error(f"File non trovato: {file_path}")
        return

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
        try:
            st.image(file_path, caption=f"Anteprima immagine: {os.path.basename(file_path)}", use_column_width=True)
        except Exception as e:
            st.error(f"Errore durante il caricamento dell'immagine {os.path.basename(file_path)}: {e}")
    elif file_extension == '.docx':
        if docx:
            try:
                document = docx.Document(file_path)
                full_text = []
                for para in document.paragraphs:
                    full_text.append(para.text)
                preview_text = "\n".join(full_text)
                st.text_area(f"Contenuto DOCX: {os.path.basename(file_path)}", preview_text[:1000] + "..." if len(preview_text) > 1000 else preview_text, height=200)
            except Exception as e:
                st.error(f"Errore durante la lettura del file DOCX {os.path.basename(file_path)}: {e}")
        else:
            st.info(f"Impossibile visualizzare l'anteprima del file .docx '{os.path.basename(file_path)}'. Installa 'python-docx'.")
            st.text(f"Percorso file: {file_path}")
    elif file_extension == '.ini': # Esempio di file di testo
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.text_area(f"Contenuto file di testo: {os.path.basename(file_path)}", content[:1000] + "..." if len(content) > 1000 else content, height=200)
        except Exception as e:
            st.error(f"Errore durante la lettura del file di testo {os.path.basename(file_path)}: {e}")
    else:
        st.info(f"Tipo di file non supportato per l'anteprima: {file_extension}")
        st.text(f"Percorso file: {file_path}")


# --- Interfaccia Utente ---
st.title("🔍 Trova il Match Perfetto")
st.markdown("""
Benvenuto nel **Job Matcher**! Incolla una descrizione di lavoro qui sotto
e ti aiuterò a trovare la job post più simile nel nostro database,
e i migliori 5 curriculum che si abbinano a quella job post.
""")

st.markdown("---")

user_job_description = st.text_area(
    "Incolla qui la descrizione della job post:",
    height=200,
    placeholder="Es: 'Cercasi Sviluppatore Web con esperienza in React e Node.js. Richiesta conoscenza di database relazionali e API RESTful...'"
)

find_match_button = st.button("🚀 Trova match")

st.markdown("---")

# --- Logica di ricerca e visualizzazione ---
if find_match_button and user_job_description:
    with st.spinner("Ricerca in corso..."):
        # 1. Genera l'embedding per la job description dell'utente
        user_embedding = get_embedding(user_job_description)

        # 2. Trova la job post più simile nel database
        try:
            st.subheader("Risultati della Ricerca")
            st.write("Cercando la job post più simile alla tua...")
            
            # Query per la job post più simile
            similar_job_posts = job_posts_collection.query(
                query_embeddings=[user_embedding],
                n_results=1,
                include=['documents', 'metadatas', 'embeddings']
            )

            if similar_job_posts['documents']:
                matched_job_post_text = similar_job_posts['documents'][0][0]
                # Usa .get() con un valore di default per gestire il caso in cui 'job_title' non sia presente
                matched_job_post_title = similar_job_posts['metadatas'][0][0].get('job_title', 'Titolo Sconosciuto')
                matched_job_post_embedding = similar_job_posts['embeddings'][0][0]

                st.success("Job Post Trovata!")
                st.markdown(f"### 🎯 Job Post più simile trovata:")
                st.markdown(f"**Titolo:** {matched_job_post_title}")
                st.markdown(f"**Descrizione:** {matched_job_post_text}")
                st.markdown("---")

                # 3. Trova i 5 migliori curriculum simili alla job post trovata
                st.write("Ora cerchiamo i 5 migliori curriculum per questa job post...")
                
                # ChromaDB restituisce i risultati già ordinati per distanza (dal più vicino al più lontano)
                similar_resumes = resumes_collection.query(
                    query_embeddings=[matched_job_post_embedding],
                    n_results=5,
                    include=['documents', 'metadatas', 'distances']
                )

                if similar_resumes['documents']:
                    st.markdown("### 📄 I 5 migliori Curriculum (dal più simile al meno simile):")
                    
                    for i, (resume_doc, resume_metadata, distance) in enumerate(zip(
                        similar_resumes['documents'][0],
                        similar_resumes['metadatas'][0],
                        similar_resumes['distances'][0]
                    )):
                        # resume_doc sarà il percorso del file (es. 'data/Resumes Datasets/.../file.png')
                        # resume_metadata sarà None, come da tua struttura
                        
                        # Poiché i metadati sono None, non possiamo estrarre un nome dal DB.
                        # Potresti voler implementare una logica per inferire il nome dal percorso del file
                        # o assicurarti che il DB contenga un campo 'name' nei metadati.
                        resume_name = "Candidato Sconosciuto" # Default se non c'è un nome nei metadati
                        
                        st.markdown(f"**{i+1}. {resume_name}** (Distanza: {distance:.2f})")
                        display_resume_content(resume_doc) # Chiama la funzione per visualizzare il contenuto del file
                        st.markdown("---")
                else:
                    st.warning("Nessun curriculum trovato per questa job post.")
            else:
                st.warning("Nessuna job post simile trovata nel database.")
        except Exception as e:
            st.error(f"Si è verificato un errore durante la ricerca: {e}")
            st.info("Assicurati che le collezioni 'job_posts' e 'resumes' contengano dati e che la funzione `get_embedding` funzioni correttamente.")
else:
    st.info("Incolla una descrizione di lavoro e clicca 'Trova match' per iniziare!")
