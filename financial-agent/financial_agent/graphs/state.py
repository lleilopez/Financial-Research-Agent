from typing import TypedDict


class AgentState(TypedDict):
    """
    Estado compartido que fluye por todos los nodos del grafo.

    Por qué TypedDict y no un dataclass o un dict normal:
    TypedDict le dice a LangGraph exactamente qué campos esperar y de qué tipo.
    Esto permite validación en tiempo de ejecución y autocompletado en el IDE.
    Un dict normal no da ninguna de las dos cosas.

    Cada campo es responsabilidad de un nodo distinto:
    - ticker: lo recibe el grafo como input inicial, ningún nodo lo modifica
    - company_name: igual que ticker
    - financial_data: lo escribe financial_analyst
    - news_sentiment: lo escribe news_analyst
    - rag_context: lo escribe rag_analyst
    - risks: lo escribe risk_analyst
    - final_report: lo escribe synthesizer
    """
    ticker: str
    company_name: str
    financial_data: dict
    news_sentiment: dict
    rag_context: str
    risks: list[str]
    final_report: str