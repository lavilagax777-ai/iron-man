import json
import sys

# Simulación de Base de Datos Maestra (Tu "ListaPreciosultima" y políticas)
CATALOGO_MAESTRO = {
    "productos": [
        {"id": 1, "nombre": "Contenedor de Bambú 16oz", "precio": 150.00, "stock": 500, "material": "Bambú"},
        {"id": 2, "nombre": "Plato de Caña de Azúcar", "precio": 85.00, "stock": 1200, "material": "Fibra de caña"}
    ],
    "politicas": {
        "descuento_max_sin_autorizacion": 0.10,
        "envio_inmediato_solo_en": "Playa del Carmen"
    }
}

class AgenteGuardianXicopack:
    def __init__(self):
        print("🛡️  [Guardián] Inicializado. Cargando políticas de Xicopack...")
        # Aquí cargaríamos Gemini 1.5 Pro usando google.generativeai en producción
        # import google.generativeai as genai
        # genai.configure(api_key=tu_api_key)
        # self.model = genai.GenerativeModel('gemini-1.5-pro')

    def auditar_respuesta_mock(self, pregunta_cliente, respuesta_propuesta):
        """
        Versión de prueba (Mock) del auditor. 
        En producción, esto enviará el prompt a Gemini 1.5 Pro.
        """
        print(f"   [Guardián] Analizando propuesta de respuesta...")
        print(f"   > Pregunta: '{pregunta_cliente}'")
        print(f"   > Respuesta del Agente: '{respuesta_propuesta}'")
        
        # Lógica dura básica para pruebas locales (simulando a Gemini)
        respuesta_lower = respuesta_propuesta.lower()
        if "plástico" in respuesta_lower or "plastico" in respuesta_lower:
            return "ESTADO: RECHAZADO\nMOTIVO: El agente mencionó plástico. Somos una marca 100% sustentable.\nTEXTO_FINAL: "
        if "50%" in respuesta_lower or "20%" in respuesta_lower:
            return "ESTADO: RECHAZADO\nMOTIVO: El descuento excede el límite del 10% permitido sin autorización.\nTEXTO_FINAL: "
            
        return f"ESTADO: APROBADO\nMOTIVO: \nTEXTO_FINAL: {respuesta_propuesta}"

if __name__ == "__main__":
    guardian = AgenteGuardianXicopack()
    
    # ---------------------------------------------------------
    # PRUEBA DE EJECUCIÓN (Simulando un mensaje entrante)
    # ---------------------------------------------------------
    print("\n[INICIANDO SIMULACIÓN DE CASO RECHAZADO]")
    pregunta = "¿Tienen platos de plástico y qué descuento me dan?"
    respuesta_mala = "¡Hola! Sí, claro, te puedo ofrecer platos de plástico con un 20% de descuento."
    
    resultado = guardian.auditar_respuesta_mock(pregunta, respuesta_mala)
    print("\n--- DICTAMEN DEL GUARDIÁN ---")
    print(resultado)
    print("-----------------------------\n")
    
    # Terminar con código de salida exitoso
    sys.exit(0)
