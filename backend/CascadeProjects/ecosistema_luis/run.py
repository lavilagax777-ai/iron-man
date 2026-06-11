#!/usr/bin/env python3
"""
Script principal para ejecutar el Ecosistema Luis
"""
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'streamlit', 
        'torch', 'pandas', 'plotly', 'python-jose', 'passlib'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Paquetes faltantes: {missing}")
        print("📦 Instalando dependencias...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("✅ Todas las dependencias están instaladas")

def setup_database():
    """Configurar la base de datos"""
    print("🗄️ Configurando base de datos...")
    
    # Usar SQLite para desarrollo local
    os.environ['DATABASE_URL'] = 'sqlite:///./ecosistema_luis.db'
    
    # Crear tablas
    from api.main import app
    from database.database import create_tables
    create_tables()
    
    print("✅ Base de datos configurada")

def start_api_server(project_dir):
    """Iniciar el servidor API en segundo plano"""
    print("🚀 Iniciando servidor API...")
    
    def run_api():
        api_dir = project_dir / 'api'
        subprocess.run([sys.executable, str(api_dir / "main.py")], cwd=str(api_dir))
    
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Esperar a que el servidor esté listo
    time.sleep(3)
    print("✅ Servidor API iniciado en http://localhost:8000")

def start_streamlit(project_dir):
    """Iniciar Streamlit"""
    print("🎨 Iniciando interfaz Streamlit...")
    
    streamlit_dir = project_dir / 'streamlit'
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(streamlit_dir / "app.py"), "--server.port", "8501"], cwd=str(streamlit_dir))

def main():
    """Función principal"""
    print("🎛️ Iniciando Ecosistema Luis...")
    print("=" * 50)
    
    # Cambiar al directorio del proyecto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Verificar dependencias
    check_dependencies()
    
    # Configurar base de datos
    setup_database()
    
    # Iniciar API
    start_api_server(project_dir)
    
    # Iniciar Streamlit (esto bloqueará el proceso principal)
    start_streamlit(project_dir)

if __name__ == "__main__":
    main()
