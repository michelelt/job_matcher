import pandas as pd
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from src.utils.utils_job_posts import clean_html_and_normalize
from src.utils.utils_chromadb import create_collection, delete_collection, insert_points_batch
from tqdm import tqdm

def insert_job_posts_to_chromadb(
    csv_path: str,
    chroma_db_path: str = "./chroma_db",
    collection_name: str = "job_posts",
    overwrite: bool = False,
    batch_size: int = 1000,
    model_name: str = "all-mpnet-base-v2"
):
    path = Path(csv_path)
    client = chromadb.PersistentClient(path=chroma_db_path)

    if create_collection(client, collection_name) is None and overwrite:
        delete_collection(client, collection_name)
        create_collection(client, collection_name)
    
    collection = client.get_collection(collection_name)
    ids = collection.get(limit=int(1e9))['ids']
    
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    model = SentenceTransformer(model_name)
    df['job_description'] = df['job_description'].str.lower().apply(clean_html_and_normalize)
    df['embedding'] = df['job_description'].apply(lambda x: model.encode(x).tolist())
    
    batch_ids = []
    batch_embeddings = []
    batch_metadatas = []
    batch_documents = []

    for i, row in tqdm(df.iterrows(), total=len(df)):
        try:
            _id = str(row["uniq_id"])
            if _id in ids:
                continue

            embedding = row["embedding"]
            document = row["job_description"]
            metadata = row.drop(["uniq_id", "embedding", 'job_description']).to_dict()

            batch_ids.append(_id)
            batch_embeddings.append(embedding)
            batch_metadatas.append(metadata)
            batch_documents.append(document)

            if len(batch_ids) >= batch_size:
                insert_points_batch(
                    client=client,
                    collection_name=collection_name,
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    metadatas=batch_metadatas,
                    documents=batch_documents
                )
                batch_ids.clear()
                batch_embeddings.clear()
                batch_metadatas.clear()
                batch_documents.clear()

        except Exception as e:
            print(f"[ERRORE - Riga {i}] {e}")
            continue

    if batch_ids:
        insert_points_batch(
            client=client,
            collection_name=collection_name,
            ids=batch_ids,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
            documents=batch_documents
        )

