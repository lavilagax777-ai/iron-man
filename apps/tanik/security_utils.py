import re

def bot_tanik_cleaner(texto):
    """
    Escanea y protege datos sensibles en tiempo real.
    """
    patrones = {
        "GOOGLE_KEY": r"AIza[0-9A-Za-z-_]{35}",
        "SHOPIFY_TOKEN": r"shpat_[0-9a-fA-F]{32}",
        "SECRETOS": r"(?i)(pass|password|clave|token|secret|shpat)\s*(?:es|:|=)\s*['\"]?([^'\"\s.]+)['\"]?"
    }
    
    if not isinstance(texto, str):
        return texto
        
    for nombre, patron in patrones.items():
        if re.search(patron, texto):
            # Reemplaza por el aviso de seguridad de Tanik
            texto = re.sub(patron, f"🔒 [DATOS PROTEGIDOS POR TANIK]", texto)
            
    return texto

def apply_security_filter(data):
    """
    Aplica el filtro de seguridad a diferentes tipos de datos (strings, dicts, lists).
    """
    if isinstance(data, str):
        return bot_tanik_cleaner(data)
    elif isinstance(data, dict):
        return {k: apply_security_filter(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [apply_security_filter(i) for i in data]
    return data
