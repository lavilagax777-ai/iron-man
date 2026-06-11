import time
import threading
import subprocess

def run_agent(agent_name, script_path, interval_seconds=0):
    """Ejecuta un agente de forma aislada."""
    print(f"[{agent_name}] Iniciando orquestación...")
    while True:
        try:
            print(f"[{agent_name}] Ejecutando tarea...")
            # Ejecutamos el script de Python
            result = subprocess.run(['python3', script_path], capture_output=True, text=True)
            if result.stdout:
                print(f"[{agent_name}] Salida:\n{result.stdout.strip()}")
            if result.stderr:
                print(f"[{agent_name}] Error:\n{result.stderr.strip()}")
            
            print(f"[{agent_name}] Tarea completada.")
        except Exception as e:
            print(f"[{agent_name}] Falló la ejecución: {e}")
        
        if interval_seconds > 0:
            print(f"[{agent_name}] Durmiendo por {interval_seconds} segundos...")
            time.sleep(interval_seconds)
        else:
            # Si el intervalo es 0, solo se ejecuta una vez por ahora para pruebas
            print(f"[{agent_name}] Ejecución única finalizada.")
            break

if __name__ == "__main__":
    print("🚀 INICIANDO XICOPACK AGENT HIVE 🚀")
    print("-" * 40)
    
    # Definimos nuestros agentes
    agentes = [
        # (Nombre, Ruta del script, Intervalo en segundos - 0 para correr una vez)
        # ("Auditor_Precios", "price_audit.py", 0),  # Lo dejamos comentado por ahora
        ("Guardian_Calidad", "agents/guardian.py", 0)
    ]
    
    # Lanzamos cada agente en su propio hilo (thread)
    hilos = []
    for nombre, ruta, intervalo in agentes:
        hilo = threading.Thread(target=run_agent, args=(nombre, ruta, intervalo))
        hilo.daemon = True # Permite que el programa principal se cierre aunque el hilo siga
        hilo.start()
        hilos.append(hilo)
    
    # Mantener el orquestador vivo 
    try:
        while True:
            time.sleep(1)
            # Para la prueba inicial, si todos los hilos mueren, salimos
            if not any(t.is_alive() for t in hilos):
                print("-" * 40)
                print("🏁 Todos los agentes han finalizado sus tareas.")
                break
    except KeyboardInterrupt:
        print("\nApagando Xicopack Agent Hive...")
