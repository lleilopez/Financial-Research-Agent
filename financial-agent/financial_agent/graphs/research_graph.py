from langgraph.graph import StateGraph, END
from financial_agent.graphs.state import AgentState
from financial_agent.agents.financial_analyst import financial_analyst_node
from financial_agent.agents.news_analyst import news_analyst_node
from financial_agent.agents.rag_analyst import rag_analyst_node
from financial_agent.agents.risk_analyst import risk_analyst_node
from financial_agent.agents.synthesizer import synthesizer_node


def build_graph():
    """
    Construye y compila el grafo de decisión del agente.

    Por qué compilamos el grafo en vez de ejecutarlo directamente:
    La compilación valida que todos los nodos están conectados correctamente,
    que no hay nodos huérfanos, y que el estado fluye bien entre ellos.
    Es el equivalente a un type-check del grafo antes de ejecutarlo.
    """
    graph = StateGraph(AgentState)

    # Registramos los nodos
    graph.add_node("financial_analyst", financial_analyst_node)
    graph.add_node("news_analyst", news_analyst_node)
    graph.add_node("rag_analyst", rag_analyst_node)
    graph.add_node("risk_analyst", risk_analyst_node)
    graph.add_node("synthesizer", synthesizer_node)

    # Definimos el flujo
    graph.set_entry_point("financial_analyst")
    graph.add_edge("financial_analyst", "news_analyst")
    graph.add_edge("news_analyst", "rag_analyst")
    graph.add_edge("rag_analyst", "risk_analyst")
    graph.add_edge("risk_analyst", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()