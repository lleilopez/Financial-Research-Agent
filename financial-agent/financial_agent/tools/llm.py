from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def ask(prompt: str, system: str = "You are a helpful financial analyst assistant.") -> str:
    """
    Llamada básica al LLM. Devuelve el texto de la respuesta.
    Todos los nodos del agente usarán esta función para interactuar con el LLM.

    Por qué centralizamos aquí:
    Si mañana queremos cambiar el modelo, ajustar temperatura, añadir
    logging o cambiar de proveedor, lo hacemos en un solo sitio.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def ask_json(prompt: str, system: str = "You are a helpful financial analyst assistant.") -> str:
    """
    Igual que ask() pero fuerza al modelo a responder en JSON válido.
    Útil cuando necesitamos parsear la respuesta programáticamente.

    Por qué temperature=0:
    En tareas de clasificación y extracción de datos no queremos
    creatividad — queremos determinismo. Temperature=0 hace que el
    modelo elija siempre el token más probable.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content