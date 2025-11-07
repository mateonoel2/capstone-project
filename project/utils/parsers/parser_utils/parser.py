from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from copy import deepcopy
from llama_index.core.schema import TextNode
from llama_parse import LlamaParse
from llama_index.llms.anthropic import Anthropic
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ["LLAMA_CLOUD_API_KEY"]
anthropic_key = os.environ["ANTHROPIC_API_KEY"]


def get_page_nodes(file, separator="\n---\n"):
    llm = Anthropic(model="claude-3-5-sonnet-20241022", api_key=anthropic_key)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.llm = llm
    Settings.embed_model = embed_model
    docs = LlamaParse(result_type="text", api_key=api_key).load_data(file)

    nodes = []
    for doc in docs:
        doc_chunks = doc.text.split(separator)
        for doc_chunk in doc_chunks:
            node = TextNode(
                text=doc_chunk,
                metadata=deepcopy(doc.metadata),
            )
            nodes.append(node)

    return nodes


def count_braces(text):
    """Counts the occurrences of `{` and `}` in a string and checks if they are balanced."""
    open_braces = text.count("{")
    close_braces = text.count("}")
    return open_braces, close_braces


def get_response_from_docs(docs, query, schema):
    index = VectorStoreIndex(docs)
    sllm = Settings.llm.as_structured_llm(output_cls=schema)
    query_engine = index.as_query_engine(
        similarity_top_k=5,
        llm=sllm,
        response_mode="tree_summarize",
    )

    response = query_engine.query(query)
    return response
