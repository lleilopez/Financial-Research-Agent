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

def find_earnings_release(cik: str, accession_number: str) -> str:
    """
    Usa el LLM para identificar cuál de los documentos de un 8-K
    es el earnings release trimestral.

    Por qué el LLM y no heurísticas:
    Cada empresa nombra y estructura sus exhibits de forma diferente.
    Una heurística de keywords funciona para Apple y Microsoft pero
    falla con Tesla. El LLM entiende el contenido independientemente
    del formato o vocabulario específico de cada empresa.
    """
    from financial_agent.tools.llm import ask_json
    import json

    cik_clean = str(int(cik))
    accession_clean = accession_number.replace("-", "")
    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_clean}/{accession_clean}/"

    response = requests.get(index_url, headers=HEADERS)
    if response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Recogemos todos los candidatos que parezcan exhibits 99
    candidates = []
    for link in soup.find_all("a"):
        href = link.get("href", "")
        if not href.endswith(".htm"):
            continue
        nombre = href.split("/")[-1].lower()
        # Cubrimos: ex99, exhibit99, exhibit991, exhibit9911111...
        if "ex99" in nombre or "exhibit99" in nombre:
            candidates.append(f"https://www.sec.gov{href}")

    if not candidates:
        return ""

    # Para cada candidato descargamos los primeros 800 caracteres de texto
    # No necesitamos el documento entero para clasificarlo
    previews = []
    for url in candidates:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            continue
        texto = extract_clean_text(r.text)
        previews.append({
            "url": url,
            "preview": texto[:800],
        })

    if not previews:
        return ""

    # Le pedimos al LLM que identifique cuál es el earnings release
    prompt = f"""Below are previews of documents attached to an SEC 8-K filing.
Identify which one is the quarterly earnings press release — the document where
the company announces its financial results for the quarter (revenue, net income, EPS, etc).

Documents:
{json.dumps(previews, indent=2)}

Respond with a JSON object with a single key "earnings_release_url" containing the URL
of the earnings release document. If none of the documents is an earnings release,
set the value to null.
"""

    result = ask_json(prompt)
    parsed = json.loads(result)
    url = parsed.get("earnings_release_url")

    if not url:
        return ""

    # Descargamos el documento completo
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return ""

    return extract_clean_text(r.text)