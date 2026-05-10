import os
from dotenv import load_dotenv
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


# Cliente de ChromaDB persistente en disco
# Por qué persistente: no queremos reindexar los documentos cada vez que
# arranca el agente. Una vez indexado un earnings release, lo reutilizamos.
chroma_client = chromadb.PersistentClient(path="./chroma_db")

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")


def index_document(ticker: str, quarter: str, text: str) -> None:
    """
    Trocea un earnings release y lo indexa en ChromaDB.

    ticker: "AAPL"
    quarter: "Q1_2026" — identifica unívocamente el documento
    text: texto limpio del earnings release

    Por qué RecursiveCharacterTextSplitter:
    Intenta dividir por párrafos primero, luego por frases, luego por palabras.
    Respeta la estructura natural del texto en vez de cortar cada N caracteres
    a ciegas. Para earnings releases, que tienen párrafos bien definidos,
    esto produce chunks mucho más coherentes.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "],
    )

    chunks = splitter.split_text(text)

    # Cada ticker tiene su propia colección en ChromaDB
    # Así podemos indexar múltiples empresas sin que se mezclen
    collection_name = f"earnings_{ticker.lower()}"
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # Generamos los embeddings de todos los chunks de una vez
    # Es más eficiente que hacerlo uno a uno — menos llamadas a la API
    vectors = embeddings_model.embed_documents(chunks)

    # Cada chunk necesita un ID único dentro de la colección
    ids = [f"{quarter}_chunk_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=chunks,
        metadatas=[{"ticker": ticker, "quarter": quarter} for _ in chunks],
    )

    print(f"Indexados {len(chunks)} chunks de {ticker} {quarter}")


def query_document(ticker: str, question: str, n_results: int = 4) -> str:
    """
    Dado un ticker y una pregunta, recupera los fragmentos más relevantes
    del earnings release indexado y los devuelve como contexto para el LLM.

    n_results=4: cuatro fragmentos de 1000 caracteres son ~4000 caracteres
    de contexto — suficiente para responder cualquier pregunta sobre el
    earnings release sin saturar el contexto del LLM.
    """
    collection_name = f"earnings_{ticker.lower()}"

    try:
        collection = chroma_client.get_collection(name=collection_name)
    except Exception:
        return ""

    # Convertimos la pregunta en un vector con el mismo modelo
    # que usamos para indexar — tienen que ser compatibles
    question_vector = embeddings_model.embed_query(question)

    results = collection.query(
        query_embeddings=[question_vector],
        n_results=n_results,
    )

    # Unimos los fragmentos recuperados en un solo bloque de texto
    chunks = results["documents"][0]
    return "\n\n---\n\n".join(chunks)


def answer_from_document(ticker: str, question: str) -> str:
    """
    Pipeline completo RAG: recupera contexto relevante y genera respuesta.
    Esta es la función que llamarán los nodos del agente.
    """
    from financial_agent.tools.llm import ask

    context = query_document(ticker, question)

    if not context:
        return "No hay earnings releases indexados para este ticker."

    prompt = f"""You are a financial analyst. Answer the following question based ONLY
on the context provided. If the answer is not in the context, say so explicitly.
Do not make up information.

Context from the earnings release:
{context}

Question: {question}

Answer in Spanish, concisely and precisely."""

    return ask(prompt)