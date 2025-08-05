import os
import hashlib
import chromadb

from typing import Set, List
from pathlib import Path

from sentence_transformers import SentenceTransformer
from src.utils.utils_resumes import file_to_plain_text
from src.utils.utils_chromadb import create_collection, delete_collection, insert_points_batch
from tqdm import tqdm

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def get_file_extensions(root: Path) -> Set[str]:
    extensions = {}
    for p in root.rglob("*"):
        if p.is_file():
            ext = p.suffix.lower().lstrip(".")
            if ext:
                if ext not in extensions:
                    extensions[ext] = 0
                extensions[ext] += 1
    return extensions

def process_resumes_to_chroma(
    root_dir: Path,
    collection_name: str,
    model_name: str = "all-mpnet-base-v2",
    batch_size: int = 1000,
    overwrite: bool = False
):
    client = chromadb.PersistentClient(path="./chroma_db")

    if overwrite:
        delete_collection(client, collection_name)

    create_collection(client, collection_name)
    collection = client.get_collection(collection_name)
    existing_ids = collection.get(limit=int(1e9))["ids"]

    model = SentenceTransformer(model_name)

    batch_ids: List[str] = []
    batch_embeddings: List[List[float]] = []
    batch_metadatas: List[str] = []

    for p in tqdm(list(root_dir.rglob("*"))):
        if p.is_file():
            try:
                file_id = hashlib.md5(str(p).encode()).hexdigest()
                if file_id in existing_ids:
                    continue

                text = file_to_plain_text(p)
                embedding = model.encode(text).tolist()

                batch_ids.append(file_id)
                batch_embeddings.append(embedding)
                batch_metadatas.append({"source": str(p)})

                if len(batch_ids) >= batch_size:
                    insert_points_batch(
                        client=client,
                        collection_name=collection_name,
                        ids=batch_ids,
                        embeddings=batch_embeddings,
                        metadatas=batch_metadatas
                    )
                    batch_ids.clear()
                    batch_embeddings.clear()
                    batch_metadatas.clear()

            except Exception as e:
                print(f"Error on {p}: {e}")

    if batch_ids:
        insert_points_batch(
            client=client,
            collection_name=collection_name,
            ids=batch_ids,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas
        )

