import os
from copy import deepcopy
from pathlib import Path
from typing import List

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_parse import LlamaParse

from src.extraction.base_parser import BaseParser
from src.extraction.schemas import BankAccount


class LlamaParser(BaseParser):
    def __init__(
        self,
        llama_api_key: str = None,
        anthropic_api_key: str = None,
        model: str = "claude-3-5-haiku-latest",
        separator: str = "\n---\n",
    ):
        self.llama_api_key = llama_api_key or os.environ.get("LLAMA_CLOUD_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.separator = separator

        self._setup_models()

    def _setup_models(self):
        llm = Anthropic(model=self.model, api_key=self.anthropic_api_key)
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.llm = llm
        Settings.embed_model = embed_model

    def _get_page_nodes(self, file_path: Path) -> List[TextNode]:
        docs = LlamaParse(result_type="text", api_key=self.llama_api_key).load_data(str(file_path))

        nodes = []
        for doc in docs:
            doc_chunks = doc.text.split(self.separator)
            for doc_chunk in doc_chunks:
                node = TextNode(
                    text=doc_chunk,
                    metadata=deepcopy(doc.metadata),
                )
                nodes.append(node)

        return nodes

    def _query_documents(self, nodes: List[TextNode], query: str) -> BankAccount:
        index = VectorStoreIndex(nodes)
        sllm = Settings.llm.as_structured_llm(output_cls=BankAccount)
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            llm=sllm,
            response_mode="tree_summarize",
        )

        response = query_engine.query(query)
        return response

    def parse_file(self, file_path: Path) -> BankAccount:
        query = "En la carátula del estado de cuenta, encuentra el dueño de la cuenta, el número \
        clabe de 18 dígitos y el nombre del banco"

        nodes = self._get_page_nodes(file_path)
        result = self._query_documents(nodes, query)

        return result
