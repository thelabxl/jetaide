from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams
import httpx

from app.core.config import settings


class QdrantService:
    """Service for managing vector memory with Qdrant."""

    COLLECTION_NAME = "jetaide_memories"
    VECTOR_SIZE = 1536  # OpenAI ada-002 embedding size

    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key or None,
        )

    async def ensure_collection(self):
        """Create the collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.COLLECTION_NAME for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(size=self.VECTOR_SIZE, distance=Distance.COSINE),
            )

    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding from OpenRouter (using OpenAI compatible endpoint)."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.openrouter_base_url}/embeddings",
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
                json={"model": "openai/text-embedding-ada-002", "input": text},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

    async def store_memory(
        self,
        user_id: str,
        content: str,
        metadata: dict | None = None,
    ) -> str:
        """
        Store a memory with its embedding.

        Args:
            user_id: The user's ID
            content: The text content to store
            metadata: Additional metadata to store with the memory

        Returns:
            The ID of the stored point
        """
        await self.ensure_collection()

        embedding = await self.get_embedding(content)
        point_id = f"{user_id}_{hash(content)}"

        payload = {
            "user_id": user_id,
            "content": content,
            **(metadata or {}),
        }

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[PointStruct(id=point_id, vector=embedding, payload=payload)],
        )

        return point_id

    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ) -> list[dict]:
        """
        Search for relevant memories for a user.

        Args:
            user_id: The user's ID
            query: The search query
            limit: Maximum number of results

        Returns:
            List of relevant memories with their content and scores
        """
        await self.ensure_collection()

        query_embedding = await self.get_embedding(query)

        results = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_embedding,
            query_filter={
                "must": [{"key": "user_id", "match": {"value": user_id}}]
            },
            limit=limit,
        )

        return [
            {
                "content": hit.payload.get("content", ""),
                "score": hit.score,
                "metadata": {k: v for k, v in hit.payload.items() if k not in ["user_id", "content"]},
            }
            for hit in results
        ]

    async def delete_user_memories(self, user_id: str):
        """Delete all memories for a user."""
        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector={
                "filter": {"must": [{"key": "user_id", "match": {"value": user_id}}]}
            },
        )


qdrant_service = QdrantService()
