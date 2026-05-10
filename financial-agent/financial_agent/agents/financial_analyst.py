from financial_agent.graphs.state import AgentState
from financial_agent.tools.yahoo_finance import (
    get_company_overview,
    get_recent_earnings,
    get_price_history,
)
from financial_agent.tools.llm import ask


def financial_analyst_node(state: AgentState) -> AgentState:
    """
    Nodo que analiza los datos financieros de la empresa.
    Recibe el estado, añade financial_data, y devuelve el estado actualizado.

    Por qué devolvemos solo el campo que modificamos y no el estado entero:
    LangGraph hace un merge automático — si devuelves {"financial_data": ...},
    el resto del estado se mantiene intacto. No tienes que devolver todo.
    """
    ticker = state["ticker"]
    company_name = state["company_name"]

    overview = get_company_overview(ticker)
    earnings = get_recent_earnings(ticker)
    prices = get_price_history(ticker, period="3mo")

    # Pedimos al LLM que interprete los datos, no solo que los transcriba
    # La diferencia entre un agente útil y un buscador glorificado está aquí
    prompt = f"""You are a financial analyst. Analyze the following financial data 
for {company_name} ({ticker}) and provide a concise analysis covering:
1. Revenue and profitability trends
2. Valuation (P/E ratio, forward P/E)
3. Financial health (debt, cash flow)
4. Recent price performance
5. Analyst consensus

Financial overview: {overview}
Recent quarterly earnings: {earnings}
Price history (last 3 months, last 5 data points): {prices[-5:]}

Be concise, factual, and highlight the most important signals for an investment decision.
Respond in Spanish."""

    analysis = ask(prompt)

    return {"financial_data": {"raw": overview, "analysis": analysis}}