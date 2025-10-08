import os
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Weaviate
import weaviate

from ai.config import ENV_PATH
load_dotenv(dotenv_path=ENV_PATH)

# Ensure all required environment variables are loaded
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
WEAVIATE_URL = os.getenv("WEAVIATE_URL")

if not all([OPENAI_API_KEY, WEAVIATE_API_KEY, WEAVIATE_URL]):
    raise ValueError("One or more required environment variables are not set.")

# Initialize Weaviate client
client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

import json
from typing import Optional

# ... (imports remain the same)

# ... (environment variable loading remains the same)

# ... (client and embeddings initialization remains the same)


def create_schema_if_not_exists(client: weaviate.Client, schema_path: str) -> str:
    """
    Creates a class in Weaviate based on a JSON schema file if it doesn't already exist.

    Args:
        client: The Weaviate client instance.
        schema_path: The absolute path to the JSON schema file.

    Returns:
        The name of the class defined in the schema.
    """
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    class_name = schema.get("class")
    if not class_name:
        raise ValueError("Schema file must contain a 'class' key.")

    if not client.schema.exists(class_name):
        client.schema.create_class(schema)
        print(f"Created new schema for class: '{class_name}'")
    
    return class_name


def get_document_loader(file_path: str):
    """Selects the appropriate document loader based on the file extension."""
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    
    if extension == ".pdf":
        return PyPDFLoader(file_path)
    elif extension == ".docx":
        return UnstructuredWordDocumentLoader(file_path)
    elif extension == ".txt":
        return TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def ingest_data(file_path: str, index_name: str, schema_path: Optional[str] = None) -> None:
    """
    Loads data from a supported file, ensures the schema exists, and ingests data into Weaviate.

    Args:
        file_path: The absolute path to the file.
        index_name: The name of the Weaviate index (class) to ingest data into.
        schema_path: Optional path to a JSON schema file for append mode.
    """
    # If in append mode, ensure the custom schema is created first
    if schema_path:
        actual_index_name = create_schema_if_not_exists(client, schema_path)
        if actual_index_name != index_name:
            print(f"Warning: Index name '{index_name}' from filename differs from schema class '{actual_index_name}'. Using schema class name.")
            index_name = actual_index_name

    # Load the document using the appropriate loader
    try:
        loader = get_document_loader(file_path)
        documents = loader.load()
    except ValueError as e:
        print(f"Skipping file {os.path.basename(file_path)} due to error: {e}")
        return

    # Add source metadata to each document
    for doc in documents:
        doc.metadata["source"] = os.path.basename(file_path)

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    # Ingest chunks into Weaviate
    Weaviate.from_documents(
        client=client,
        documents=chunks,
        embedding=embeddings,
        index_name=index_name,
        text_key="text"
    )
    print(f"Successfully ingested {len(chunks)} chunks into index '{index_name}'.")



