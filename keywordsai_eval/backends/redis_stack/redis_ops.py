from langchain.text_splitter import TokenTextSplitter
import os
from redis import ResponseError
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.field import VectorField, TextField
import numpy as np
import redis
from redis.client import Pipeline
from openai import OpenAI
from typing import Union
from litellm import token_counter
from pathlib import Path
import json
from ... import settings
from litellm import embedding as litellm_embedding

RELATIVE_PATH = Path(__file__).parent
oai_client = OpenAI()

category_details = {}
topic_details = {}

try:
    with open(RELATIVE_PATH / "category_prompts.json", "r") as f:
        category_details = json.load(f)
    with open(RELATIVE_PATH / "topic_prompts.json", "r") as f:
        topic_details = json.load(f)
except Exception as e:
    print("Error importing category prompts", e)


def create_and_store_embedding(client: redis.Redis, key_name, details, summary=""):

    # convert to numpy array and bytes
    vector = create_embedding_vector(details)
    # Create a new hash with url and embedding
    post_hash = {
        "summary": summary,
        "details": details,
        "embedding": vector,
    }
    # create hash
    client.hset(name=key_name, mapping=post_hash)


def user_content_prompt(user_content):
    return f"""A job seeker says this during job search session: {user_content}"""


def create_embedding_vector(
    text, model=settings.EMBEDDING_MODEL_NAME, dimensions=1536, to_byte=True
) -> Union[np.ndarray, np.bytes_]:
    # Your code here
    """create embedding vector from text
    Keyword arguments:
    text -- text to be embedded, string
    Return: np.array in bytes
    """
    splitter = TokenTextSplitter.from_tiktoken_encoder(
        chunk_size=7000, chunk_overlap=0, encoding_name="cl100k_base"
    )  # safe trim to 8000 tokens, prevent overloading embedding model. text-emebdding-3-small is cl100k_base
    text = splitter.split_text(text)[0]
    token_count = token_counter(text=text)
    print(f"=====Vectorizing: {text[:15]} Token count: {token_count}=====")
    embedding = litellm_embedding(input=text, model=model, dimensions=dimensions)
    query_vector = embedding.data[0].get("embedding", [])
    # Convert the vector to a numpy array
    if to_byte:
        query_vector = np.array(query_vector).astype(np.float32).tobytes()

    return query_vector


def retrieve_topk(query_vector: np.bytes_, index_name, top_k=2):
    """Retrieves the top k relavant text chunks
    Keyword arguments:
    query_vector -- numpy array
    Return: return_description
    """

    client = redis.Redis(**settings.REDIS_CLIENT)
    results = []
    base_query = f"*=>[KNN {top_k} @embedding $vector AS vector_score]"
    search_query = (
        Query(base_query)
        .return_fields("summary", "details", "vector_score")
        .sort_by("vector_score")
        .dialect(2)
    )

    try:
        # ft full text search
        search_results: Pipeline = client.ft(index_name).search(
            search_query, query_params={"vector": query_vector}
        )

        for i, doc in enumerate(search_results.docs):
            results.append(doc.details)
    except Exception as e:
        print("Error calling Redis search: ", e)
        pass
    return results


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def clear_previous_embeddings(index_name):
    """
    Clear the embeddings of a certain key pattern starts with index_name
    """
    "redis-cli --scan --pattern 'job_openai_embedding*' | xargs redis-cli del"
    # Get all the keys that match the pattern
    client = redis.Redis(**settings.REDIS_CLIENT)
    keys = client.keys(f"{index_name}*")
    # Delete all the keys
    for key in keys:
        client.delete(key)


def create_classification_index(client: redis.Redis, index_name: str, prefixes: list[str]):
    SCHEMA = [
        TextField("summary"),
        TextField("details"),
        VectorField(
            "embedding",
            "HNSW",
            {"TYPE": "FLOAT32", "DIM": 1536, "DISTANCE_METRIC": "IP"},
        ),
    ]

    try:
        # Check if the index already exists
        client.ft(index_name).info()
    except ResponseError:
        print("Creating new index...", index_name)
        client.ft(index_name).create_index(
            fields=SCHEMA,
            definition=IndexDefinition(prefix=prefixes, index_type=IndexType.HASH),
        )


def create_classification_embeddings(
    client: redis.Redis, index_name: str = "query_type_categories", model=settings.EMBEDDING_MODEL_NAME
):
    """
    Create an index of documentations for categories that contains the following information:
    - summary: a concise title of the category
    - details: a detailed prompt of the category
    - embedding: the embedding of the prompt
    """
    # Iterate over categories and their details
    for category, description in category_details.items():
        # Construct the concise title and detailed prompt
        prompt = f"This query is classified as {category}: {description}"
        label = f"{index_name}|" + category

        # Check if the embedding already exists, if not, create and store it
        if not client.exists(label):
            create_and_store_embedding(client, label, prompt, category)

    # Create or update the OpenAI index with new categories
    create_classification_index(client, index_name, ["query_type_categories"])


def init_embeddings(client: redis.Redis):
    """
    Create the embeddings for the categories, formats, and expertise domains
    """
    create_classification_embeddings(
        client, index_name=settings.CATEGORY_EMBEDDING_INDEX_NAME
    )
    create_classification_embeddings(
        client, index_name=settings.TOPIC_EMBEDDING_INDEX_NAME
    )


def get_category(
    query_string, index_name: str = settings.CATEGORY_EMBEDDING_INDEX_NAME, client=None
) -> str:
    """Get the category and difficulty of a question based on its embedding

    Keyword arguments:
    client -- redis-client
    query_embedding -- embedding of the question, np.ndarray
    Return: string of category and difficulty: "difficulty:category"
    """
    if not client:
        client = redis.Redis(**settings.REDIS_CLIENT)
    query_vector = create_embedding_vector(query_string)
    base_query = "*=>[KNN 20 @embedding $vector AS vector_score]"
    search_query = (
        Query(base_query)
        .return_fields("summary", "details", "vector_score")
        .sort_by("vector_score")
        .dialect(2)
        .paging(0, 20)
    )

    category = ""

    search_results = client.ft(index_name).search(
        search_query, query_params={"vector": query_vector}
    )
    if not search_results.docs:
        pass
    else:
        category = search_results.docs[0].summary

    return category


def delete_index(index_name, client=None):
    # user_file_index = user.email + "_file"
    # user.user_file_index = user_file_index
    """
    delete index and everything in it
    """
    if not client:
        client = redis.Redis(**settings.REDIS_CLIENT)
    try:
        client.ft(index_name).dropindex(delete_documents=True)
    except Exception as e:
        print("Error", e)


def reset_embeddings(client, test=False):
    if not test:
        delete_index("query_type_categories")
        delete_index("topic_categories")
    init_embeddings(client)
