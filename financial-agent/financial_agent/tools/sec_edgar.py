import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "financial-agent tu-email@gmail.com",
}


def get_recent_filings(ticker: str, form_type: str = "8-K", count: int = 5) -> list[dict]:
    """
    Devuelve los últimos N filings de un tipo dado para una empresa.
    """
    cik = _get_cik(ticker)
    if not cik:
        return []

    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return []

    data = response.json()
    filings = data["filings"]["recent"]

    results = []
    for i, form in enumerate(filings["form"]):
        if form == form_type:
            results.append({
                "form": form,
                "filed_at": filings["filingDate"][i],
                "accession_number": filings["accessionNumber"][i],
                "primary_document": filings["primaryDocument"][i],
                "cik": cik,
            })
        if len(results) >= count:
            break

    return results


def get_earnings_release_text(cik: str, accession_number: str) -> str:
    """
    Dado un filing 8-K, encuentra el Exhibit 99.1 (earnings press release)
    y devuelve su texto limpio.
    """
    cik_clean = str(int(cik))
    accession_clean = accession_number.replace("-", "")
    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_clean}/{accession_clean}/"

    response = requests.get(index_url, headers=HEADERS)
    if response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Recogemos todos los enlaces que parecen exhibits
    exhibit_candidates = []
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if "ex99" in href.lower() and href.endswith(".htm"):
            exhibit_candidates.append(f"https://www.sec.gov{href}")

    # Palabras que aparecen en cualquier earnings release
    # Si el documento no contiene ninguna, no es un earnings release
    earnings_keywords = [
    "revenue",
    "earnings per share",
    "net income",
    "quarter",
    "results",
    "billion",
    "million",
    "operating income",
    "guidance",
]

    for url in exhibit_candidates:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            continue

        texto = extract_clean_text(response.text)

        # Comprobamos que al menos 3 keywords aparecen en el texto
        texto_lower = texto.lower()
        matches = sum(1 for kw in earnings_keywords if kw in texto_lower)

        if matches >= 5:
            return texto

    return ""


def extract_clean_text(html: str) -> str:
    """
    Extrae el texto limpio de un documento HTML/XBRL de la SEC.
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    lines = [line.strip() for line in text.splitlines()]
    clean_lines = [line for line in lines if line]

    return "\n".join(clean_lines)


def _get_cik(ticker: str) -> str | None:
    """
    Convierte un ticker en el CIK de la SEC.
    """
    tickers_url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(tickers_url, headers=HEADERS)

    if response.status_code != 200:
        return None

    data = response.json()
    for entry in data.values():
        if entry["ticker"].upper() == ticker.upper():
            return str(entry["cik_str"]).zfill(10)

    return None