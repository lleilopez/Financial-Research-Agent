import json
from financial_agent.tools.llm import ask_json


def evaluate_report(report: str, source_data: dict) -> dict:
    """
    Evalúa un informe de inversión en tres dimensiones.

    report: el informe final generado por el synthesizer
    source_data: diccionario con los datos fuente usados para generarlo
        {
            "financial_data": ...,
            "news_sentiment": ...,
            "rag_context": ...,
            "risks": ...
        }

    Devuelve un diccionario con puntuaciones y justificaciones:
        {
            "groundedness": {"score": 4, "justification": "..."},
            "coherence": {"score": 5, "justification": "..."},
            "completeness": {"score": 3, "justification": "..."},
            "overall": 4.0
        }

    Por qué LLM-as-a-judge y no métricas automáticas:
    Métricas como BLEU o ROUGE miden similitud de texto, no calidad de razonamiento.
    Un informe puede tener palabras distintas a los datos fuente y ser perfectamente
    correcto — simplemente los ha parafraseado. El LLM entiende el significado,
    no solo las palabras.
    """
    prompt = f"""You are a STRICT evaluator of financial research reports.
Your job is to find flaws, not to validate. Be critical and demanding.

Score each dimension from 1 to 5. A score of 5 means the report is essentially perfect
with no room for improvement. This should be rare. A score of 3 means acceptable but
with clear gaps. Be specific about what is missing or wrong.

Dimensions:

1. GROUNDEDNESS (1-5): Are ALL specific claims (numbers, percentages, quotes) 
   directly traceable to the source data? Penalize heavily for:
   - Any figure not present in the source data
   - Vague claims without data support
   - Extrapolations presented as facts

2. COHERENCE (1-5): Is the internal logic airtight? Penalize for:
   - A "buy" recommendation despite severe risks
   - Contradictions between sections
   - Conclusions that don't follow from the analysis

3. COMPLETENESS (1-5): Are all sections present AND substantive? Penalize for:
   - Sections that exist but say nothing concrete
   - Missing quantitative data where it should exist
   - Generic statements that could apply to any company

SOURCE DATA:
Financial data: {json.dumps(source_data.get('financial_data', {}), ensure_ascii=False)}
News sentiment: {json.dumps(source_data.get('news_sentiment', {}), ensure_ascii=False)}
Earnings insights: {source_data.get('rag_context', '')}
Risks identified: {source_data.get('risks', [])}

REPORT TO EVALUATE:
{report}

Respond with a JSON object with this exact structure:
{{
    "groundedness": {{"score": <int>, "justification": "<string>"}},
    "coherence": {{"score": <int>, "justification": "<string>"}},
    "completeness": {{"score": <int>, "justification": "<string>"}}
}}"""

    result = ask_json(prompt)
    parsed = json.loads(result)

    scores = [
        parsed["groundedness"]["score"],
        parsed["coherence"]["score"],
        parsed["completeness"]["score"],
    ]
    parsed["overall"] = round(sum(scores) / len(scores), 2)

    return parsed


def print_evaluation(evaluation: dict) -> None:
    """
    Imprime el resultado de la evaluación de forma legible.
    """
    print("\n" + "=" * 60)
    print("EVALUACION DEL INFORME")
    print("=" * 60)

    dimensions = ["groundedness", "coherence", "completeness"]
    labels = {
        "groundedness": "Groundedness (datos reales)",
        "coherence": "Coherencia interna",
        "completeness": "Completitud",
    }

    for dim in dimensions:
        data = evaluation[dim]
        score = data["score"]
        bar = "#" * score + "-" * (5 - score)
        print(f"\n{labels[dim]}: {score}/5 [{bar}]")
        print(f"  {data['justification']}")

    print(f"\nPUNTUACION GLOBAL: {evaluation['overall']}/5")
    print("=" * 60)