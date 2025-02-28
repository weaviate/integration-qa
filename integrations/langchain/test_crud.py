import argparse
import sys
from typing import List
import weaviate
from weaviate.classes.init import Auth
from langchain_core.embeddings import Embeddings
from langchain_weaviate.vectorstores import WeaviateVectorStore
import os
import random

# Constants
NUM_TEXTS = 100_000
BATCH_SIZE = 100
EMBEDDING_DIM = 1536


class FakeEmbeddings(Embeddings):
    """Fake embeddings functionality for testing."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Return random embeddings for documents."""
        return [[random.random() for _ in range(EMBEDDING_DIM)] for _ in texts]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Return a random embedding for a query."""
        return [random.random() for _ in range(EMBEDDING_DIM)]

    async def aembed_query(self, text: str) -> List[float]:
        return self.embed_query(text)


class LangChainCRUD:
    def __init__(self, collection_name: str):
        try:
            weaviate_url = os.environ["WEAVIATE_URL"]
            weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
        except KeyError as e:
            raise ValueError(f"Missing required environment variable: {e}")

        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,
            auth_credentials=Auth.api_key(weaviate_api_key),
        )
        self.collection_name = collection_name
        self.vectorstore = WeaviateVectorStore(
            self.client, collection_name, "text", FakeEmbeddings()
        )

    def create(self):
        print(
            f"📝 Creating {NUM_TEXTS:,} random texts in LangChain with collection {self.collection_name}..."
        )

        for i in range(0, NUM_TEXTS, BATCH_SIZE):
            batch_texts = [
                f"Random text {j}" for j in range(i, min(i + BATCH_SIZE, NUM_TEXTS))
            ]
            self.vectorstore.add_texts(batch_texts)
            print(f"Added batch {i // BATCH_SIZE + 1} of {NUM_TEXTS // BATCH_SIZE + 1}")

        total_count = (
            self.client.collections.get(self.collection_name)
            .aggregate.over_all(total_count=True)
            .total_count
        )

        assert (
            total_count == NUM_TEXTS
        ), f"Expected {NUM_TEXTS:,} records, got {total_count:,}"
        print(
            f"✅ Created {total_count:,} random texts in LangChain with collection {self.collection_name}."
        )

    def read(self):
        print(
            f"📖 Reading a test record from LangChain with collection {self.collection_name}..."
        )

        text_to_search = "Random text 123"
        docs = self.vectorstore.similarity_search(text_to_search, alpha=0.1)
        print(f"Found {len(docs)} similar documents.")
        doc = docs[0]
        assert (
            doc.page_content == text_to_search
        ), f"Expected '{text_to_search}', got '{doc.page_content}'"
        print(
            f"✅ Found the test record in LangChain with collection {self.collection_name}."
        )

    def update(self):
        print("🔄 Update operation is not supported in LangChain.")

    def delete(self):
        print(
            f"🗑️ Deleting records from LangChain with collection {self.collection_name}..."
        )
        random_text = "Random text 123"
        doc_ids = self.vectorstore.add_texts([random_text])

        total_docs_before_delete = (
            self.client.collections.get(self.collection_name)
            .aggregate.over_all(total_count=True)
            .total_count
        )

        self.vectorstore.delete(doc_ids)

        total_docs_after_delete = (
            self.client.collections.get(self.collection_name)
            .aggregate.over_all(total_count=True)
            .total_count
        )

        assert (
            total_docs_after_delete == total_docs_before_delete - 1
        ), f"Expected {total_docs_before_delete - 1:,} records, got {total_docs_after_delete:,}"
        print(
            f"✅ Deleted records from LangChain. Total records: {total_docs_after_delete:,}"
        )

    def cleanup(self):
        if self.client.collections.exists(self.collection_name):
            self.client.collections.delete(self.collection_name)
        self.client.close()


def main():
    parser = argparse.ArgumentParser(
        description="Run CRUD operations on LangChain integration."
    )
    parser.add_argument(
        "--weaviate_collection", required=True, help="The Weaviate collection to use."
    )
    args = parser.parse_args()

    crud = LangChainCRUD(args.weaviate_collection)
    try:
        print("Running all CRUD operations in sequence...")
        crud.create()
        crud.read()
        crud.update()
        crud.delete()
    except Exception as e:
        print(f"❌ Error during CRUD operations: {e}")
        sys.exit(1)
    finally:
        crud.cleanup()


if __name__ == "__main__":
    main()
