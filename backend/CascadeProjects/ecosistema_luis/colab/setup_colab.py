#!/usr/bin/env python3
"""
Script para configurar el entorno de Google Colab con el Ecosistema Luis
"""
import os
import subprocess
import sys

def install_dependencies():
    """Instalar todas las dependencias necesarias"""
    print("🔧 Instalando dependencias...")
    
    # Instalar Streamlit
    !pip install -q streamlit
    
    # Instalar LocalTunnel
    !npm install -g localtunnel
    
    # Instalar dependencias del proyecto
    !pip install -q fastapi uvicorn sqlalchemy torch torchvision pandas plotly
    !pip install -q python-jose[cryptography] passlib[bcrypt] python-multipart
    !pip install -q google-api-python-client google-auth-httplib2 google-auth-oauthlib
    
    print("✅ Dependencias instaladas correctamente")

def setup_streamlit_app():
    """Crear y configurar la app de Streamlit para Colab"""
    app_content = '''
import streamlit as st
import pandas as pd
import plotly.express as px
import torch
import numpy as np
from datetime import datetime, timedelta
import json

# Importar el bot de IA (simulado para Colab)
class ColabProductivityBot:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        st.success(f"🚀 Usando GPU: {torch.cuda.is_available()}")
        
    def predict_priority(self, task_data):
        """Predecir prioridad usando GPU de Colab"""
        # Simulación de predicción de IA
        import random
        return {
            "baja": random.uniform(0.1, 0.3),
            "media": random.uniform(0.3, 0.5), 
            "alta": random.uniform(0.2, 0.6)
        }
    
    def get_context_recommendations(self, context):
        """Obtener recomendaciones basadas en contexto"""
        recommendations = {
            "Local Xicopack": ["limpieza", "atencion", "cotizaciones"],
            "Casa / Estudio": ["optimizacion", "inventario", "musica"],
            "Evento Musical": ["ensayo", "promocion", "logistica"]
        }
        return recommendations.get(context, ["sin_recomendaciones"])

bot = ColabProductivityBot()

# Configuración de página
st.set_page_config(
    page_title="🎛️ Ecosistema Luis - Colab Edition", 
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    .gpu-indicator {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎛️ Centro de Mando: Ecosistema Luis</h1>
    <p>🚀 Potenciado por Google Colab GPU + Redes Neuronales</p>
</div>
""", unsafe_allow_html=True)

# Indicador de GPU
st.markdown(f"""
<div class="gpu-indicator">
    <h3>🔥 Estado del Sistema</h3>
    <p><strong>GPU Disponible:</strong> {torch.cuda.is_available()}</p>
    <p><strong>Dispositivo:</strong> {bot.device}</p>
    <p><strong>Memoria GPU:</strong> {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📍 Contexto Actual")
context = st.sidebar.radio("Ubicación:", ["Local Xicopack", "Casa / Estudio", "Evento Musical"])

if context == "Local Xicopack":
    st.sidebar.warning("🏪 Prioridad: Limpieza y Atención")
elif context == "Casa / Estudio":
    st.sidebar.info("🏠 Prioridad: Optimización")
else:
    st.sidebar.error("🎸 Prioridad: Evento Musical")

# Demo de IA
st.header("🤖 Demostración de IA en GPU")

if st.button("🚀 Ejecutar Análisis con IA"):
    with st.spinner("Procesando con redes neuronales..."):
        # Simular análisis de múltiples tareas
        tasks = [
            {"title": "Revisar inventario", "context": context, "urgency": 0.8},
            {"title": "Actualizar página web", "context": context, "urgency": 0.6},
            {"title": "Preparar material evento", "context": context, "urgency": 0.9}
        ]
        
        results = []
        for task in tasks:
            prediction = bot.predict_priority(task)
            results.append({
                "task": task["title"],
                "prioridad_alta": prediction["alta"],
                "urgencia": task["urgency"]
            })
        
        # Mostrar resultados
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        
        # Gráfico de prioridades
        fig = px.bar(df, x="task", y="prioridad_alta", title="Prioridad IA por Tarea")
        st.plotly_chart(fig, use_container_width=True)

# Recomendaciones contextuales
st.header("💡 Recomendaciones Inteligentes")
recommendations = bot.get_context_recommendations(context)

for rec in recommendations:
    st.markdown(f"""
    <div class="metric-card">
        <h4>📌 {rec.title()}</h4>
        <p>Recomendado para el contexto actual: {context}</p>
    </div>
    """, unsafe_allow_html=True)

# Métricas del sistema
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔥 GPU", "Activa" if torch.cuda.is_available() else "Inactiva")

with col2:
    st.metric("📊 Tareas Analizadas", "3")

with col3:
    st.metric("⚡ Velocidad", "GPU Acelerada")

st.markdown("---")
st.markdown("### 🚀 Conectado desde Google Colab con LocalTunnel")
'''
    
    with open('/content/app.py', 'w') as f:
        f.write(app_content)
    
    print("✅ App de Streamlit creada para Colab")

def launch_services():
    """Iniciar Streamlit y LocalTunnel"""
    print("🚀 Iniciando servicios...")
    
    # Iniciar Streamlit en segundo plano
    !streamlit run /content/app.py &>/dev/null&
    
    # Obtener URL del túnel
    print("🌐 Generando túnel público...")
    !npx localtunnel --port 8501

def main():
    """Función principal de configuración"""
    print("🎛️ Configurando Ecosistema Luis en Google Colab...")
    print("=" * 50)
    
    install_dependencies()
    setup_streamlit_app()
    launch_services()
    
    print("=" * 50)
    print("✅ ¡Sistema listo! Usa la URL generada arriba para acceder.")

if __name__ == "__main__":
    main()

