import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent / ".env")

# ==============================================================================
# 1. CONFIGURACIÓN DE CONEXIÓN A OPEN WEBUI
# ==============================================================================
# Docker publica el contenedor como host:3000 -> contenedor:8080.
# La ruta compatible con OpenAI en Open WebUI termina en "/api".
OPENWEBUI_BASE_URL = "http://localhost:3000/api"

# API Key de Open WebUI (Settings -> Account -> API Keys).
# Se lee de la variable de entorno o del archivo .env junto a este script.
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "").strip().strip('"').strip("'")

# Inicializamos el cliente oficial de OpenAI apuntando a nuestro entorno local
client = OpenAI(
    base_url=OPENWEBUI_BASE_URL,
    api_key=OPENWEBUI_API_KEY,
)

# ==============================================================================
# 2. SELECCIÓN DEL MODELO PERSONALIZADO (CON RAG / KNOWLEDGE BASE)
# ==============================================================================
# ID exacto del modelo creado en Workspace -> Models.
# Se lee de TARGET_MODEL en el .env; si no existe, usa el valor por defecto.
MODELO_A_USAR = os.getenv("TARGET_MODEL", "asistente-innovatech-2027").strip().strip('"').strip("'")

# Batería de pruebas del Lab 2 (no se envía "#": el modelo ya tiene la
# Knowledge Base vinculada y Open WebUI hace la búsqueda vectorial solo).
PREGUNTAS = [
    ("Presentación", "Hola, preséntate brevemente y dime qué tipo de asistencia puedes brindarme."),
    ("Dato exacto", "¿Cuánto es el auxilio de conectividad 2027 y cuál es su código?"),
    ("Condicional / Rol", "Llevo 8 meses en la empresa, ¿cuántos días de vacaciones anticipadas puedo pedir y quién gestiona RRHH?"),
    ("Protocolo técnico", "Detecté una fuga en AWS, ¿en cuánto tiempo debo reportarla, a qué canal y qué cifrado exige la norma?"),
    ("Anti-alucinación", "¿Cuál es el horario de atención de la cafetería los sábados en Innovatech?"),
]


def verificar_modelo() -> bool:
    """Comprueba que la API key funciona y que el modelo existe."""
    try:
        ids = [m.id for m in client.models.list().data]
    except Exception as e:
        print(f"No se pudo autenticar contra Open WebUI: {e}")
        return False
    if MODELO_A_USAR not in ids:
        print(f"El modelo '{MODELO_A_USAR}' no aparece en Open WebUI.")
        print("Modelos disponibles:", ", ".join(ids) or "(ninguno)")
        return False
    print(f"Modelo '{MODELO_A_USAR}' encontrado en Open WebUI.\n")
    return True


def consultar_modelo(prompt_usuario: str) -> None:
    t0 = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=MODELO_A_USAR,
            messages=[{"role": "user", "content": prompt_usuario}],
            temperature=0.3,  # Temperatura baja para respuestas más precisas
        )
        print(response.choices[0].message.content)
        print(f"\n(Tiempo de respuesta: {time.perf_counter() - t0:.2f} s)")
    except Exception as e:
        print(f"Error al conectar con Open WebUI: {e}")


if __name__ == "__main__":
    if not OPENWEBUI_API_KEY:
        print("Falta OPENWEBUI_API_KEY. Ponla en el archivo .env (junto a este script).")
        raise SystemExit(1)

    print(f"Conectando a {OPENWEBUI_BASE_URL} | Modelo: {MODELO_A_USAR}...\n")
    if not verificar_modelo():
        raise SystemExit(1)

    for i, (tipo, pregunta) in enumerate(PREGUNTAS, start=1):
        print("=" * 78)
        print(f"[{i}/{len(PREGUNTAS)}] {tipo}")
        print(f"Pregunta: {pregunta}")
        print("--- Respuesta del Modelo ---")
        consultar_modelo(pregunta)
        print()
