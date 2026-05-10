from financial_agent.graphs.state import AgentState
from financial_agent.tools.llm import ask
import json


def risk_analyst_node(state: AgentState) -> AgentState:
    """
    Nodo que identifica riesgos sintetizando los outputs de los tres
    analistas anteriores. No llama a ninguna API externa — razona
    sobre el estado que ya tienen los nodos anteriores.

    Por qué un nodo separado para riesgos y no incluirlo en el synthesizer:
    Separar la identificación de riesgos de la síntesis final permite que
    el synthesizer reciba los riesgos como input estructurado, no como
    texto libre. Esto hace el informe final más consistente.
    """
    financial_analysis = state["financial_data"].get("analysis", "")
    news_analysis = state["news_sentiment"].get("analysis", "")
    rag_context = state["rag_context"]

    prompt = f"""You are a risk analyst. Based on the following analyses, identify 
the top 5 investment risks for this company. Be specific and actionable.

Financial analysis:
{financial_analysis}

News sentiment analysis:
{news_analysis}

Earnings release insights:
{rag_context}

Respond with a JSON object with a single key "risks" containing a list of 5 strings,
each describing a specific risk. Respond in Spanish."""

    result = ask(prompt)

    # El modelo puede devolver JSON con o sin backticks — limpiamos
    clean = result.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(clean)
        risks = parsed.get("risks", [])
    except Exception:
        risks = [clean]

    return {"risks": risks}