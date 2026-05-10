from financial_agent.graphs.state import AgentState
from financial_agent.tools.sec_edgar import get_recent_filings, find_earnings_release
from financial_agent.tools.rag import index_document, answer_from_document


def rag_analyst_node(state: AgentState) -> AgentState:
    """
    Nodo que extrae insights del earnings release más reciente usando RAG.
    Primero indexa el documento si no está ya indexado, luego hace queries.
    """
    ticker = state["ticker"]

    filings = get_recent_filings(ticker, form_type="8-K", count=20)
    texto = ""
    quarter = ""

    for f in filings:
        texto = find_earnings_release(f["cik"], f["accession_number"])
        if len(texto) > 5000:
            quarter = f["filed_at"][:7].replace("-", "_")
            break

    if not texto:
        return {"rag_context": "No se encontraron earnings releases para este ticker."}

    # Indexamos el documento — si ya existe con ese ID, ChromaDB lo ignora
    index_document(ticker, quarter, texto)

    # Preguntas clave que cualquier analista haría sobre un earnings release
    questions = [
        "What was the revenue this quarter and how does it compare to last year?",
        "What did management say about guidance and outlook for next quarter?",
        "Which business segments performed best and worst?",
        "What are the main risks or challenges mentioned by management?",
    ]

    answers = []
    for question in questions:
        answer = answer_from_document(ticker, question)
        answers.append(f"Q: {question}\nA: {answer}")

    rag_context = "\n\n".join(answers)

    return {"rag_context": rag_context}