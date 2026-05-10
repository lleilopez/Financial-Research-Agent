from financial_agent.graphs.state import AgentState
from financial_agent.tools.news import get_company_news
from financial_agent.tools.llm import ask


def news_analyst_node(state: AgentState) -> AgentState:
    """
    Nodo que analiza el sentiment de noticias recientes.
    """
    ticker = state["ticker"]
    company_name = state["company_name"]

    news = get_company_news(ticker, company_name, days_back=7)

    if not news:
        return {"news_sentiment": {"sentiment": "neutral", "analysis": "No se encontraron noticias recientes."}}

    # Formateamos las noticias para el LLM
    news_text = "\n\n".join([
        f"Titulo: {a['title']}\nFuente: {a['source']}\nFecha: {a['published_at']}\nResumen: {a['description']}"
        for a in news
    ])

    prompt = f"""You are a financial news analyst. Analyze the following recent news 
about {company_name} ({ticker}) and provide:
1. Overall sentiment (bullish / neutral / bearish)
2. Key themes and narratives in the news
3. Any significant events or risks mentioned
4. How the news might impact the investment thesis

News articles:
{news_text}

Respond in Spanish, concisely."""

    analysis = ask(prompt)

    return {
        "news_sentiment": {
            "sentiment": "see_analysis",
            "analysis": analysis,
            "articles_analyzed": len(news),
        }
    }