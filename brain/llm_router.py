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

def chat_with_grok(messages: list[dict]) -> str:
    """Envía el historial de mensajes a Grok 3 (xAI) y retorna la respuesta."""
    try:
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            return "⚠️ XAI_API_KEY no encontrada. Agrega tu clave al archivo .env"

        client = OpenAI(
            base_url="https://api.x.ai/v1",
            api_key=api_key,
        )

        response = client.chat.completions.create(
            model="grok-beta", # Puedes cambiarlo a "grok-3" cuando xAI lance el endpoint exacto
            messages=messages,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error con Grok: {str(e)}"

def chat_with_claude(messages: list[dict]) -> str:
    """Envía el historial de mensajes a Claude y retorna la respuesta."""
    try:
        # Importación aquí para no romper la app si no está instalada
        import anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "⚠️ ANTHROPIC_API_KEY no encontrada. Agrega tu clave al archivo .env"

        client = anthropic.Anthropic(api_key=api_key)
        
        # Claude requiere un formato ligeramente distinto
        system_msg = "You are a helpful assistant."
        claude_msgs = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                claude_msgs.append({"role": msg["role"], "content": msg["content"]})

        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1024,
            system=system_msg,
            messages=claude_msgs
        )
        return response.content[0].text

    except ImportError:
        return "⚠️ Librería `anthropic` no instalada. Ejecuta: pip install anthropic"
    except Exception as e:
        return f"❌ Error con Claude: {str(e)}"

def route_to_llm(llm_choice: str, messages: list[dict]) -> str:
    """Decide a qué modelo enviar el mensaje basado en la elección."""
    if llm_choice == "Gemini 1.5 Pro":
        return chat_with_gemini(messages)
    elif llm_choice == "Grok 3":
        return chat_with_grok(messages)
    elif llm_choice == "Claude":
        return chat_with_claude(messages)
    else:
        return "Modelo no soportado"
