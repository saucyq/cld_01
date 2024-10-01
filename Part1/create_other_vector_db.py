from typing import List, Optional

from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from google.cloud import storage
import os
import argparse
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

##################################
##################################
from pinecone import Pinecone,ServerlessSpec

# Initialize Pinecone
pc = Pinecone(
    api_key="#"
)

##################################
##################################


def embed_text(
    texts: List[str],
    task: str = "RETRIEVAL_DOCUMENT",
    dimensionality: Optional[int] = 256,
    model_name: str = "text-embedding-004"
) -> List[List[float]]:
    """Embeds texts with a pre-trained, foundational model.
    Args:
        texts (List[str]): A list of texts to be embedded.
        task (str): The task type for embedding. Check the available tasks in the model's documentation.
        dimensionality (Optional[int]): The dimensionality of the output embeddings.
    Returns:
        List[List[float]]: A list of lists containing the embedding vectors for each input text
    """
    if texts is None:
        raise ValueError("Must provide text.")

    if len(texts) > 250:
        raise ValueError("250 is the max number of instances")

    model = TextEmbeddingModel.from_pretrained(model_name)
    inputs = [TextEmbeddingInput(text, task) for text in texts]
    kwargs = dict(
        output_dimensionality=dimensionality) if dimensionality else {}
    embeddings = model.get_embeddings(inputs, **kwargs)
    return [embedding.values for embedding in embeddings]


def download_documents(bucket_name: str, local_dir: str) -> None:
    """Downloads the available documents from the specified Google Cloud Storage bucket.

    Args:
        bucket_name (str): The name of the Google Cloud Storage bucket.
        local_dire (str): The location in which to download the files.
    """
    # Initialize the GCS client
    client = storage.Client()

    # Get the bucket
    bucket = client.get_bucket(bucket_name)

    # List all the blobs (files) in the bucket
    blobs = bucket.list_blobs()

    # Download each blob
    for blob in blobs:
        # Construct the local file path
        local_file_path = os.path.join(local_dir, blob.name)

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Download the blob to the local file path
        blob.download_to_filename(local_file_path)
        print(f"Downloaded {blob.name} to {local_file_path}")


# Split pages/text into chunks
def split_text(docs: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(docs)

    return chunks


def main(bucket_name: str, local_dir: str,index_name:str ):
    download_documents(bucket_name, local_dir)
    loader = PyPDFDirectoryLoader(local_dir)
    docs = loader.load()
    print('Start chunking')
    chunks = split_text(docs, 315, 100)
    embeddings = embed_text(
        [chunk.page_content for chunk in chunks],
        "QUESTION_ANSWERING"
    )
    embedding_dimension = len(embeddings[0])


    #####################################
    #####################################

    #
    # Create the index if it doesn't exist
    if  not pc.has_index(index_name) :
        pc.create_index(
            name=index_name,
            dimension=embedding_dimension,
            metric="cosine" ,
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
        )
        )
    index = pc.Index(index_name)
    # Prepare data for Pinecone upload
    data_to_upload = []
    '''    
    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_data = {
            'id': str(index),  
            'values': embedding,  
            'metadata': chunk.metadata  
        }
        data_to_upload.append(chunk_data)
    '''
    # Upload to Pinecone
    #index.upsert(vectors=data_to_upload)

    to_upsert = [(str(i), embedding) for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))]
    index.upsert(vectors=to_upsert)



    ####################################
    ####################################



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process PDF documents and store their embeddings.")
    parser.add_argument(
        "--bucket_name", help="The GCS bucket name where documents are stored")

    # TODO @Cyril Telly: Ajouter si nécessaire des paramètres
    # P. ex. "URL de la base de donnée" ou "nom de la collecion"

    parser.add_argument("--local_path", help="local path")
    parser.add_argument("--index_name", help="Pinecone index name")  # Add index name argument
    args = parser.parse_args()
    main(args.bucket_name, args.local_path, args.index_name)  # Pass index name to main