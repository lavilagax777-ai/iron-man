import os
from supabase import create_client, Client

def test_supabase_connection() -> str:
    """Prueba la conexión con Supabase y retorna un mensaje de estado."""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            return "⚠️ SUPABASE_URL o SUPABASE_KEY no encontradas. Completa el archivo .env"

        client: Client = create_client(url, key)
        # Consulta básica para verificar que la conexión funciona
        client.table("_test_ping").select("*").limit(1).execute()
        return "✅ Conexión con Supabase establecida con éxito."

    except ImportError:
        return "⚠️ Librería `supabase` no instalada. Ejecuta: pip install supabase"
    except Exception as e:
        # Si el error es de tabla no encontrada, la conexión sí funciona
        if "does not exist" in str(e) or "relation" in str(e).lower() or "404" in str(e):
            return "✅ Conexión con Supabase exitosa. (La tabla de prueba no existe, pero el servidor responde.)"
        return f"❌ Error conectando a Supabase: {str(e)}"

def test_local_connection() -> str:
    """
    Función genérica placeholder para la base de datos local.
    Aquí se conectará ChromaDB, SQLite, o la solución definitiva
    cuando se decida más adelante.
    """
    message = "✅ Conexión local simulada con éxito. Listo para conectar la base de datos local definitiva más adelante."
    return message
