from pymilvus import MilvusClient, model
from pymilvus.model.base import BaseEmbeddingFunction
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_TEXT_EMBEDDING_MODEL, COLLECTION_NAME, DB_PATH



async def get_embedding(text: str):
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.embeddings.create(
        model=OPENAI_TEXT_EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


class MilvusDB:
    """
    MilvusDB is a singleton class that provides a connection to the Milvus database.
    """
    _instance = None
    _client = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MilvusDB, cls).__new__(cls)
            cls._instance._client = MilvusClient(DB_PATH)
        return cls._instance
    
    def get_client(self) -> MilvusClient:
        return self._client

    def create_collection(self, collection_name: str, dimension: int = None, schema: dict = None):
        if self._client.has_collection(collection_name):
            raise Exception(f"Collection {collection_name} already exists")
        
        self._client.create_collection(collection_name, dimension=dimension, schema=schema)
        

class MilvusCollection:
    """
    MilvusCollection is a class that provides a collection to the Milvus database.
    """
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.db = MilvusDB()
        self.client = self.db.get_client()

    def insert(self, data: dict):
        self.client.insert(collection_name=self.collection_name, data=data)
        
    async def vector_search(self, query: str, limit: int = 3, output_fields: list[str] = None, search_params: dict = None) -> list[dict]:
        query_vector = await get_embedding(query)

        results = self.client.search(
            collection_name=self.collection_name, 
            data=[query_vector],
            limit=limit,
            output_fields=output_fields,
            search_params=search_params
        )

        return results[0]
    

class FaqCollection(MilvusCollection):
    """
    FaqCollection is a class that provides a collection to the Milvus database for the FAQ data.
    """
    def __init__(self):
        super().__init__(COLLECTION_NAME)

    async def vector_search(self, query: str, limit: int = 3, radius: float = 0.4) -> list[dict]:
        search_params = {
            "params": {
                "radius": radius,
            }
        }
        output_fields = ["question", "answer"]

        return await super().vector_search(
            query=query, 
            limit=limit, 
            search_params=search_params, 
            output_fields=output_fields
        )
