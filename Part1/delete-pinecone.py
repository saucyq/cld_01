
from pinecone import Pinecone,ServerlessSpec
pc = Pinecone(
    api_key="#"
)

pc.delete_index("pinecone-test")
# Creator: Abir Chebbi (abir.chebbi@hesge.ch)


