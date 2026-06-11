import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Configuración de página
st.set_page_config(
    page_title="🎛️ Ecosistema Luis - Centro de Mando Inteligente", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (inspirados en Bolt.new)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    .priority-high { border-left: 4px solid #ef4444; }
    .priority-medium { border-left: 4px solid #f59e0b; }
    .priority-low { border-left: 4px solid #10b981; }
    .context-xicopack { background: rgba(16, 185, 129, 0.1); }
    .context-casa { background: rgba(59, 130, 246, 0.1); }
    .context-musica { background: rgba(239, 68, 68, 0.1); }
    .endpoint-card {
        background: #2d2d2d;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    .endpoint-card:hover {
        border-color: #667eea;
        background: #3d3d3d;
    }
</style>
""", unsafe_allow_html=True)

# Configuración de API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Estado de sesión
if 'token' not in st.session_state:
    st.session_state.token = None
if 'current_context' not in st.session_state:
    st.session_state.current_context = "Local Xicopack"

# Funciones de API
def api_request(method, endpoint, data=None, params=None):
    """Realizar petición a la API"""
    headers = {}
    if st.session_state.token:
        headers['Authorization'] = f'Bearer {st.session_state.token}'
    
    try:
        if method == 'GET':
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(f"{API_BASE_URL}{endpoint}", headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(f"{API_BASE_URL}{endpoint}", headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(f"{API_BASE_URL}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

# Sidebar - Autenticación y Contexto
with st.sidebar:
    st.markdown("## 🔐 Acceso")
    
    if not st.session_state.token:
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            login_data = api_request('POST', '/auth/login', None, {'email': email, 'password': password})
            if login_data:
                st.session_state.token = login_data['access_token']
                st.success("¡Sesión iniciada!")
                st.rerun()
    else:
        st.success("✅ Conectado")
        if st.button("Cerrar Sesión"):
            st.session_state.token = None
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 📍 Contexto Actual")
    
    context_options = ["Local Xicopack", "Casa / Estudio", "Evento Musical"]
    selected_context = st.selectbox("Ubicación:", context_options, index=context_options.index(st.session_state.current_context))
    st.session_state.current_context = selected_context
    
    # Recomendaciones basadas en contexto
    if st.session_state.current_context == "Local Xicopack":
        st.warning("🏪 **Prioridad:** Limpieza y Atención. Avanzar cotizaciones si no hay clientes.")
    elif st.session_state.current_context == "Casa / Estudio":
        st.info("🏠 **Prioridad:** Optimización de página y carga de inventario.")
    else:
        st.error("🎸 **Prioridad:** Preparación para evento musical.")

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🎛️ Centro de Mando: Ecosistema Luis</h1>
    <p>Productividad Inteligente con Redes Neuronales y Automatización</p>
</div>
""", unsafe_allow_html=True)

# Métricas principales
if st.session_state.token:
    # Obtener datos de la API
    tasks_data = api_request('GET', '/api/v1/tasks', params={'limit': 100})
    notes_data = api_request('GET', '/api/v1/notes', params={'limit': 100})
    inventory_data = api_request('GET', '/api/v1/inventory')
    
    if tasks_data and notes_data and inventory_data:
        # Métricas en columnas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = len(tasks_data)
            completed_tasks = len([t for t in tasks_data if t['status'] == 'completada'])
            st.metric("📋 Tareas", f"{completed_tasks}/{total_tasks}", f"{completed_tasks/total_tasks*100:.1f}%")
        
        with col2:
            total_notes = len(notes_data)
            favorite_notes = len([n for n in notes_data if n['is_favorite']])
            st.metric("📝 Notas", f"{favorite_notes}/{total_notes}", "Favoritas")
        
        with col3:
            low_stock = len([i for i in inventory_data if i['quantity'] <= i['min_quantity']])
            st.metric("📦 Inventario", low_stock, "Stock bajo")
        
        with col4:
            today_events = len([e for e in api_request('GET', '/api/v1/calendar-events', params={
                'start_date': datetime.now().isoformat(),
                'end_date': (datetime.now() + timedelta(days=1)).isoformat()
            }) or []])
            st.metric("📅 Hoy", today_events, "Eventos")

# Pestañas principales
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛒 Shopify & Local", "🎸 Música & Proyectos", "🤖 IA & Bots", "📊 Analytics", "⚙️ API Endpoints"])

with tab1:
    st.header("🏪 Xicopack - Gestión Local")
    
    if st.session_state.token:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Tareas del Contexto")
            context_tasks = [t for t in (tasks_data or []) if t.get('context') == st.session_state.current_context]
            
            for task in context_tasks[:5]:
                priority_class = f"priority-{task['priority'].lower()}"
                st.markdown(f"""
                <div class="metric-card {priority_class}">
                    <h4>{task['title']}</h4>
                    <p><small>{task.get('description', 'Sin descripción')}</small></p>
                    <p><strong>Prioridad IA:</strong> {task.get('ai_priority_score', {}).get('alta', 0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📦 Inventario Crítico")
            critical_items = [i for i in (inventory_data or []) if i['quantity'] <= i['min_quantity']]
            
            if critical_items:
                for item in critical_items:
                    st.markdown(f"""
                    <div class="metric-card priority-high">
                        <h4>{item['name']}</h4>
                        <p>Stock: {item['quantity']} / {item['min_quantity']}</p>
                        <p><strong>Proveedor:</strong> {item.get('supplier', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No hay items con stock bajo")
    
    else:
        st.warning("Por favor inicia sesión para ver esta información")

with tab2:
    st.header("🎸 Proyectos Musicales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Diálogos y Letras")
        music_notes = [n for n in (notes_data or []) if n.get('category') == 'musica']
        
        for note in music_notes[:3]:
            st.markdown(f"""
            <div class="metric-card context-musica">
                <h4>{note['title']}</h4>
                <p>{note.get('content', 'Sin contenido')[:100]}...</p>
                <p><small>Creado: {note['created_at'][:10]}</small></p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎵 Próximos Eventos")
        st.info("🗓️ **Próximo evento importante: 6 de Julio**")
        
        # Colaboradores
        st.markdown("**Colaboradores:**")
        collaborators = ["Lucho", "Ernesto", "Iván"]
        for collab in collaborators:
            st.markdown(f"- 🎸 {collab}")

with tab3:
    st.header("🤖 Inteligencia Artificial y Automatización")
    
    if st.session_state.token:
        # Análisis de productividad
        analytics_data = api_request('GET', '/api/v1/analytics/productivity')
        if analytics_data:
            st.subheader("📈 Patrones de Productividad")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tareas Completadas", analytics_data.get('total_completed', 0))
                
            with col2:
                pattern = analytics_data.get('productivity_pattern', {})
                best_hour = pattern.get('best_productivity_hour', 10)
                st.metric("Mejor Hora", f"{best_hour}:00")
        
        # Logs de IA
        st.subheader("🧠 Actividad de la IA")
        ai_logs = api_request('GET', '/api/v1/ai-priority-logs', params={'limit': 10})
        
        if ai_logs:
            for log in ai_logs:
                st.markdown(f"""
                <div class="endpoint-card">
                    <h5>{log['action'].title()}</h5>
                    <p><small>Confianza: {log.get('confidence_score', 0):.2f}</small></p>
                    <p><small>{log['created_at'][:19]}</small></p>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.warning("Inicia sesión para ver análisis de IA")

with tab4:
    st.header("📊 Análisis y Visualización")
    
    if st.session_state.token and tasks_data:
        # Gráfico de tareas por prioridad
        priorities = {}
        for task in tasks_data:
            priority = task.get('priority', 'media')
            priorities[priority] = priorities.get(priority, 0) + 1
        
        fig = px.pie(
            values=list(priorities.values()),
            names=list(priorities.keys()),
            title="Distribución de Tareas por Prioridad"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de contexto
        contexts = {}
        for task in tasks_data:
            context = task.get('context', 'Sin contexto')
            contexts[context] = contexts.get(context, 0) + 1
        
        fig2 = px.bar(
            x=list(contexts.keys()),
            y=list(contexts.values()),
            title="Tareas por Contexto"
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab5:
    st.header("⚙️ API Endpoints Disponibles")
    
    endpoints = [
        {"name": "Profiles", "path": "/api/v1/profiles", "icon": "👤", "method": "GET"},
        {"name": "Tasks", "path": "/api/v1/tasks", "icon": "📋", "method": "GET/POST/PUT/DELETE"},
        {"name": "Notes", "path": "/api/v1/notes", "icon": "📝", "method": "GET/POST"},
        {"name": "Calendar Events", "path": "/api/v1/calendar-events", "icon": "📅", "method": "GET/POST"},
        {"name": "Inventory", "path": "/api/v1/inventory", "icon": "📦", "method": "GET/POST"},
        {"name": "Learning", "path": "/api/v1/learning", "icon": "📚", "method": "GET/POST"},
        {"name": "AI Priority Logs", "path": "/api/v1/ai-priority-logs", "icon": "🤖", "method": "GET"},
        {"name": "Analytics", "path": "/api/v1/analytics/productivity", "icon": "📊", "method": "GET"},
    ]
    
    for endpoint in endpoints:
        st.markdown(f"""
        <div class="endpoint-card">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.5rem;">{endpoint['icon']}</span>
                <div>
                    <h4>{endpoint['name']}</h4>
                    <code>{endpoint['method']} {endpoint['path']}</code>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Instrucciones rápidas
    st.markdown("---")
    st.subheader("🚀 Inicio Rápido")
    
    st.markdown("""
    <div class="metric-card">
        <h4>1. Instalar dependencias</h4>
        <code>cd api && pip install -r requirements.txt</code>
    </div>
    
    <div class="metric-card">
        <h4>2. Iniciar servidor API</h4>
        <code>python3 main.py</code>
    </div>
    
    <div class="metric-card">
        <h4>3. Explorar documentación</h4>
        <code>http://localhost:8000/docs</code>
    </div>
    
    <div class="metric-card">
        <h4>4. Ejecutar Streamlit</h4>
        <code>streamlit run streamlit/app.py</code>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("🗄️ **PostgreSQL**")
with col2:
    st.markdown("🔐 **JWT Auth**")
with col3:
    st.markdown("⚡ **FastAPI**")
with col4:
    st.markdown("🐍 **Python + PyTorch**")
