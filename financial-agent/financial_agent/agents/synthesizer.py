from financial_agent.graphs.state import AgentState
from financial_agent.tools.llm import ask


def synthesizer_node(state: AgentState) -> AgentState:
    """
    Nodo final que sintetiza todos los análisis en un informe de inversión.
    Recibe el estado completo y produce el informe final.
    """
    ticker = state["ticker"]
    company_name = state["company_name"]
    financial_analysis = state["financial_data"].get("analysis", "")
    news_analysis = state["news_sentiment"].get("analysis", "")
    rag_context = state["rag_context"]
    risks = state["risks"]

    prompt = f"""You are a senior investment analyst writing a research report.
Based on the following analyses, write a comprehensive investment report for 
{company_name} ({ticker}).

The report must include:
1. Resumen ejecutivo (2-3 frases)
2. Análisis financiero
3. Análisis de noticias y sentiment
4. Insights del ultimo earnings call
5. Riesgos principales
6. Tesis de inversión (conclusion con recomendacion: comprar / mantener / vender)

Financial analysis:
{financial_analysis}

News sentiment:
{news_analysis}

Earnings release insights:
{rag_context}

Key risks identified:
{risks}

Write the report in Spanish. Be direct, concise, and actionable.
A good analyst does not hedge everything — take a position."""

    report = ask(prompt)

    return {"final_report": report}