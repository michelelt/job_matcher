import chromadb


def create_collection(client, name):
    """Crea una collezione con il nome specificato."""
    try:
        collection = client.create_collection(name)
        print(f"Collezione '{name}' creata.")
        return collection
    except Exception as e:
        print(f"Errore creazione collezione: {e}")
        return None

def delete_collection(client, name):
    """Elimina una collezione esistente."""
    try:
        collection = client.delete_collection(name)
        # collection.delete()
        print(f"Collezione '{name}' eliminata.")
    except Exception as e:
        print(f"Errore eliminazione collezione: {e}")

def insert_point(client, collection_name, id, embedding, metadata=None):
    """Inserisce un punto (id, embedding, metadata) nella collezione."""
    try:
        collection = client.get_collection(collection_name)
        collection.add(
            documents=[metadata] if metadata else [""],
            embeddings=[embedding],
            ids=[id]
        )
        # print(f"Punto con id '{id}' inserito in '{collection_name}'.")
    except Exception as e:
        print(f"Errore inserimento punto: {e}")

def search_point(client, collection_name, query_embedding, n_results=5):
    """Cerca i punti più simili al vettore query_embedding."""
    try:
        collection = client.get_collection(collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
    except Exception as e:
        print(f"Errore nella ricerca: {e}")
        return None


def insert_points_batch(client, collection_name, ids, embeddings, metadatas=None, documents=None):
    """
    Inserisce in batch punti nella collezione.
    
    ids: lista di stringhe
    embeddings: lista di vettori
    metadatas: lista di metadata o None
    """
    try:
        collection = client.get_collection(collection_name)
        if metadatas is None:
            metadatas = [""] * len(ids)
        if documents is None:
            documents = [""] * len(ids)
        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        print(f"Inseriti {len(ids)} punti in batch in '{collection_name}'.")
    except Exception as e:
        print(f"Errore inserimento batch: {e}")