import yfinance as yf


def get_company_overview(ticker: str) -> dict:
    """
    Devuelve un resumen financiero básico de una empresa dado su ticker.
    Esto será una de las herramientas del financial_analyst.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "revenue_growth": info.get("revenueGrowth"),
        "profit_margins": info.get("profitMargins"),
        "debt_to_equity": info.get("debtToEquity"),
        "return_on_equity": info.get("returnOnEquity"),
        "free_cashflow": info.get("freeCashflow"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "analyst_target_price": info.get("targetMeanPrice"),
        "recommendation": info.get("recommendationKey"),
    }


def get_recent_earnings(ticker: str, quarters: int = 4) -> list[dict]:
    """
    Devuelve los últimos N trimestres de resultados financieros.
    """
    stock = yf.Ticker(ticker)
    financials = stock.quarterly_financials

    if financials.empty:
        return []

    results = []
    for date in financials.columns[:quarters]:
        quarter_data = {
            "date": str(date.date()),
            "total_revenue": financials.loc["Total Revenue", date] if "Total Revenue" in financials.index else None,
            "gross_profit": financials.loc["Gross Profit", date] if "Gross Profit" in financials.index else None,
            "net_income": financials.loc["Net Income", date] if "Net Income" in financials.index else None,
            "operating_income": financials.loc["Operating Income", date] if "Operating Income" in financials.index else None,
        }
        results.append(quarter_data)

    return results


def get_price_history(ticker: str, period: str = "3mo") -> list[dict]:
    """
    Devuelve el precio de cierre diario de los últimos N meses.
    period puede ser: 1mo, 3mo, 6mo, 1y, 2y
    """
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)

    if history.empty:
        return []

    result = []
    for date, row in history.iterrows():
        result.append({
            "date": str(date.date()),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        })

    return result