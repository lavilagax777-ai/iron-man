import concurrent.futures
import subprocess
import time
import os

def run_agent(name, script_path):
    # Ejecuta el script y captura su salida
    result = subprocess.run(['python3', script_path], capture_output=True, text=True)
    return f"\n{'='*40}\n📢 REPORTE: {name}\n{'='*40}\n{result.stdout}"

def main():
    print("🐝 XICOPACK AGENT HIVE - ORQUESTADOR CENTRAL")
    print("Iniciando auditoría masiva en paralelo...\n")
    
    start_time = time.time()

    # Definición de agentes y sus rutas
    agents = {
        "AUDITOR TÉCNICO (Metafields)": "/Users/luis_genji/antigravity/metafield_audit.py",
        "SEGURIDAD GOOGLE (SEO)": "/Users/luis_genji/antigravity/seo_security_audit.py",
        "AUDITOR DE PRECIOS": "/Users/luis_genji/antigravity/price_audit.py",
        "AUDITOR DE FACTURACIÓN": "/Users/luis_genji/antigravity/billing_agent.py",
        "CIBERSEGURIDAD": "/Users/luis_genji/antigravity/security_leak_audit.py"
    }

    full_report = "# 📊 REPORTE EJECUTIVO DE AUDITORÍA XICOPACK\n\n"
    full_report += f"**Fecha de ejecución:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Ejecución en paralelo usando ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_agent = {executor.submit(run_agent, name, path): name for name, path in agents.items()}
        
        for future in concurrent.futures.as_completed(future_to_agent):
            try:
                report = future.result()
                print(report)
                full_report += report + "\n"
            except Exception as e:
                error_msg = f"❌ Error en uno de los agentes: {e}"
                print(error_msg)
                full_report += error_msg + "\n"

    end_time = time.time()
    summary = f"\n{'*'*40}\n✅ SISTEMA ACTUALIZADO\nTiempo total: {end_time - start_time:.2f}s\n{'*'*40}"
    print(summary)
    full_report += summary

    # Guardar reporte en archivo
    report_file = "/Users/luis_genji/antigravity/REPORTE_EJECUTIVO.md"
    with open(report_file, "w") as f:
        f.write(full_report)
    
    print(f"\n📂 Reporte persistente guardado en: {report_file}")

if __name__ == "__main__":
    main()
