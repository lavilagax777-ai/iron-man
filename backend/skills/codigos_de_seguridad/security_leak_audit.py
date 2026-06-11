import re
import os

class SecurityAgent:
    def __init__(self):
        # Patrones comunes de API Keys (Google, Stripe, AWS, Shopify)
        self.patterns = {
            "Google API Key": r'AIza[0-9A-Za-z-_]{35}',
            "Generic Secret": r'(?i)(api_key|secret|password|token|auth)\s*[:=]\s*["\']([0-9a-zA-Z]{16,})["\']',
            "Shopify Access Token": r'shpat_[a-fA-A0-9]{32}',
            "AWS Access Key": r'AKIA[0-9A-Z]{16}'
        }

    def scan_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_leaks = []
            for key_type, pattern in self.patterns.items():
                # Evitamos detectar la definición del patrón en este mismo script
                matches = re.findall(pattern, content)
                if matches:
                    found_leaks.append((key_type, len(matches)))
            
            if found_leaks:
                print(f"⚠️ ¡ALERTA DE SEGURIDAD! Posible filtración en: {os.path.basename(file_path)}")
                for leak_type, count in found_leaks:
                    print(f"  - Detectada posible {leak_type}: {count} coincidencia(s)")
                return True
        except Exception:
            return False
        return False

if __name__ == "__main__":
    import sys
    print("🛡️ AGENTE: AUDITOR DE CIBERSEGURIDAD")
    print("Escaneando scripts en busca de llaves expuestas...\n")
    
    agent = SecurityAgent()
    leaks_found = 0
    files_to_scan = []
    
    # Si se pasan argumentos, escaneamos solo esos archivos
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            if os.path.isfile(f) and f.endswith(".py") and not f.endswith("security_leak_audit.py"):
                files_to_scan.append(f)
    else:
        # Si no hay argumentos, escaneamos la carpeta actual
        workspace = "."
        for root, dirs, files in os.walk(workspace):
            # Evitamos carpetas ocultas o de sistema
            if any(ignored in root for ignored in [".git", "__pycache__", ".gemini"]):
                continue
            for file in files:
                if file.endswith(".py") and file != "security_leak_audit.py":
                    files_to_scan.append(os.path.join(root, file))
                    
    for file_path in files_to_scan:
        if agent.scan_file(file_path):
            leaks_found += 1
    
    if leaks_found == 0:
        print("✅ SEGURIDAD: No se detectaron llaves expuestas en tus scripts.")
        sys.exit(0)
    else:
        print(f"\n🚨 COMMIT BLOQUEADO: Mueve las llaves detectadas a un archivo .env inmediatamente para poder subir los cambios.")
        sys.exit(1)
