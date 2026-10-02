"""
RAG knowledge base for ShopSmart policies (FAISS + OpenAI embeddings).

The vector store is built lazily on the first policy_lookup call, so importing
this module does not hit the embeddings API.
"""
from functools import lru_cache

from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL, RETRIEVER_K
from data.loader import POLICIES


def split_policies(text: str = POLICIES) -> list[str]:
    """Split the policy document into ~500-char, heading-aligned chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n- ", "\n", " "],
    )
    return splitter.split_text(text)


@lru_cache(maxsize=1)
def get_policy_retriever():
    """Build (once) the FAISS vector store and return a top-k similarity retriever."""
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings

    documents = [
        Document(page_content=chunk, metadata={"source": "policies.txt", "chunk_index": index})
        for index, chunk in enumerate(split_policies())
    ]
    vector_store = FAISS.from_documents(documents, OpenAIEmbeddings(model=EMBEDDING_MODEL))
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": RETRIEVER_K})


@tool
def policy_lookup(query: str) -> str:
    """Search ShopSmart's official policies using semantic search.
    Use this to get accurate policy information about returns, shipping, billing, etc.
    """
    results = get_policy_retriever().invoke(query)
    if not results:
        return "No relevant policy information found."
    policy_text = "\n\n---\n\n".join(document.page_content for document in results)
    return f"Relevant ShopSmart Policies:\n\n{policy_text}"
