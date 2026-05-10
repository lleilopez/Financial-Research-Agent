# Bitácora del proyecto — Financial Research Agent

## Descripción general
Agente de investigación financiera que, dado un ticker, produce un informe de inversión completo.
Arquitectura multi-agente con LangGraph, RAG sobre earnings calls, y evaluación de outputs.

---

## Stack
- LangGraph — grafo de decisión multi-agente
- OpenAI GPT-4o-mini — LLM central
- Yahoo Finance — datos financieros y precio histórico
- NewsAPI — noticias y sentiment
- SEC EDGAR — earnings releases oficiales
- ChromaDB — vector store para RAG
- FastAPI — API
- Streamlit — frontend

---

## Estructura del proyecto
financial-agent/
financial_agent/
tools/          # Fuentes de datos y utilidades
agents/         # Nodos especializados del grafo
graphs/         # Definición del grafo LangGraph
api/            # FastAPI
tests/

---

## Decisiones de diseño

### 2025-05-10 — Fuentes de datos

**Yahoo Finance**
- Usamos yfinance para datos financieros básicos y precio histórico.
- Filtramos stock.info a ~15 campos relevantes. El diccionario completo tiene +100 campos — mandar todo al LLM es ruido que degrada el razonamiento.

**NewsAPI**
- La búsqueda es por texto libre, no por ticker. Buscamos por nombre de empresa ("Apple", no "AAPL").
- Limitamos a 10 artículos. Más no mejora el análisis, solo gasta tokens.

**SEC EDGAR**
- El documento útil no es el primaryDocument del 8-K sino el Exhibit 99.1 — el earnings press release escrito en lenguaje natural.
- El primaryDocument es XBRL con metadata estructurada, no legible por el LLM.
- Identificamos el Exhibit 99.1 buscando enlaces con "ex99" en el índice del filing.
- El filtro de keywords (revenue, earnings per share, net income...) no es suficientemente robusto para todos los tickers — Tesla lo demostró. Decisión: usar el LLM para clasificar qué documento es el earnings release.

**LLM (OpenAI)**
- Centralizamos todas las llamadas al LLM en financial_agent/tools/llm.py.
- Motivo: si cambiamos modelo, proveedor, o añadimos logging, lo hacemos en un solo sitio.
- temperature=0 en todas las llamadas de clasificación y extracción — queremos determinismo, no creatividad.
- Dos funciones: ask() para texto libre, ask_json() para cuando necesitamos parsear la respuesta.

---

## Problemas encontrados y soluciones

### SEC EDGAR — identificación del earnings release
**Problema:** no todos los Exhibit 99.x de un 8-K son earnings releases. Tesla publica planes de compensación y otros documentos como Exhibit 99.1 o 99.2, lo que confunde el filtro por nombre de archivo.
**Intento 1:** filtro por keywords (revenue, net income, guidance...) con umbral de 3 matches. Demasiado permisivo — Tesla seguía colándose.
**Intento 2:** subir umbral a 5 matches. Demasiado estricto — Tesla no encontraba nada.
**Solución adoptada:** usar el LLM para clasificar los candidatos. Más robusto que cualquier heurística.

---

## Pendiente
- [ ] Implementar clasificación de earnings releases con LLM
- [ ] Construir componente RAG sobre earnings releases
- [ ] Diseñar grafo LangGraph con nodos especializados
- [ ] Implementar nodo financial_analyst
- [ ] Implementar nodo news_analyst
- [ ] Implementar nodo rag_analyst
- [ ] Implementar nodo risk_analyst
- [ ] Implementar nodo synthesizer
- [ ] Eval framework
- [ ] FastAPI
- [ ] Frontend Streamlit