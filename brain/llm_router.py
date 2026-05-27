import os
from google import genai
from google.genai import types
from openai import OpenAI

def chat_with_gemini(messages: list[dict]) -> str:
    """Envía el historial de mensajes a Gemini y retorna la respuesta."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ GEMINI_API_KEY no encontrada. Agrega tu clave al archivo .env"

        client = genai.Client(api_key=api_key)

        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
            )

        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=contents
        )
        return response.text

    except ImportError:
        return "⚠️ Librería `google-genai` no instalada. Ejecuta: pip install google-genai"
    except Exception as e:
        return f"❌ Error con Gemini: {str(e)}"

def chat_with_llama(messages: list[dict]) -> str:
    """Envía el historial de mensajes a Llama 3 vía OpenRouter y retorna la respuesta."""
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return "⚠️ OPENROUTER_API_KEY no encontrada. Agrega tu clave al archivo .env"

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct:free",
            messages=messages,
        )
        return response.choices[0].message.content

    except ImportError:
        return "⚠️ Librería `openai` no instalada. Ejecuta: pip install openai"
    except Exception as e:
        return f"❌ Error con Llama 3 (OpenRouter): {str(e)}"

def route_to_llm(llm_choice: str, messages: list[dict]) -> str:
    """Decide a qué modelo enviar el mensaje basado en la elección."""
    if llm_choice == "Gemini 1.5 Pro":
        return chat_with_gemini(messages)
    else:
        return chat_with_llama(messages)
