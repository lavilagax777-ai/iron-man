import streamlit as st

    with tab1:
        st.subheader("Lista de Bandas")
        # Ejemplo de datos
        bandas = pd.DataFrame({
            "Nombre": ["The Taniks", "Binary Beats", "Eco-Rhythm"],
            "Género": ["Cyberpunk", "Electronic", "Acoustic"],
            "Estado": ["Confirmado", "Pendiente", "Confirmado"]
        })
        st.table(bandas)
        
    with tab2:
        st.write("Calendario de próximos eventos...")

elif project == "🛡️ Centro de Seguridad":
    st.title("🛡️ Tanik Security Hub")
    st.write("Monitoreo de filtraciones y limpieza de datos en tiempo real.")
    
    test_text = st.text_area("Prueba el Bot Tanik Cleaner:", "Ingresa texto con llaves de API para probar...")
    if test_text:
        st.subheader("Resultado Protegido:")
        st.code(apply_security_filter(test_text))import pandas as pd
import os
from security_utils import apply_security_filter

# Configuración de página
st.set_page_config(
    page_title="Tanik Command Center",
    page_icon="🐝",
    layout="wide"
)

# Estilos CSS personalizados para el look "Tanizen"
st.markdown("""
    <style>
    .main {
        background-color: #0d1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00ffcc;
    }
    h1, h2, h3 {
        color: #00ffcc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar para navegación
st.sidebar.title("🐝 Tanik Hive")
project = st.sidebar.selectbox("Selecciona Proyecto", ["🏠 Dashboard Global", "📦 Xicopack Admin", "🎸 Proyecto Diálogos", "🛡️ Centro de Seguridad"])

st.sidebar.markdown("---")
st.sidebar.info("Sistema Tanizen Activo • Online")

# --- LÓGICA DE PÁGINAS ---

if project == "🏠 Dashboard Global":
    st.title("Sistema Tanizen Activo")
    st.write("Bienvenido al centro de comando de Luis Genji.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Agentes Activos", "3", "+1")
    with col2:
        st.metric("Salud SEO", "85%", "-5%")
    with col3:
        st.metric("Vulnerabilidades", "0", "Limpio")

elif project == "📦 Xicopack Admin":
    st.title("📦 Xicopack Auditoría B2B")
    
    # Intenta leer el reporte ejecutivo de antigravity
    report_path = "/Users/luis_genji/antigravity/REPORTE_EJECUTIVO.md"
    
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            content = f.read()
            # Aplicamos el filtro de seguridad antes de mostrar
            st.markdown(apply_security_filter(content))
    else:
        st.warning("⚠️ No se encontró el reporte ejecutivo. Ejecuta el orquestador en /antigravity.")

elif project == "🎸 Proyecto Diálogos":
    st.title("🎸 Gestión Musical: Diálogos")
    st.write("Bienvenido a la administración de bandas y eventos.")
    
    tab1, tab2 = st.tabs(["Bandas", "Eventos"])
    

st.markdown("---")
st.caption("Tanik Command Center v1.0 • Desarrollado por Antigravity")
