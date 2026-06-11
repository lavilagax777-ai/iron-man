# 🎛️ Ecosistema Luis - Sistema de Productividad Inteligente

Un sistema completo de productividad que combina redes neuronales, Streamlit, FastAPI y Google Colab para crear un centro de mando inteligente inspirado en tu código Bolt.new.

## 🏗️ Arquitectura del Proyecto

```
ecosistema_luis/
├── api/                    # API FastAPI con endpoints REST
│   └── main.py            # Servidor principal con 7 endpoints
├── models/                # Modelos de Machine Learning
│   └── neural_network.py  # Red neuronal para priorización
├── database/              # Sistema de base de datos
│   ├── models.py         # Modelos SQLAlchemy
│   └── database.py       # Configuración de DB
├── streamlit/            # Interfaz visual
│   └── app.py           # Dashboard inspirado en Bolt.new
├── utils/               # Utilidades
│   └── auth.py          # Autenticación JWT
├── colab/              # Scripts para Google Colab
│   └── setup_colab.py  # Configuración automática
├── requirements.txt    # Dependencias
└── README.md          # Este archivo
```

## 🚀 Características Principales

### 🤖 Inteligencia Artificial
- **Red Neuronal PyTorch**: Priorización automática de tareas
- **Análisis de Patrones**: Detección de mejores horas de productividad
- **Recomendaciones Contextuales**: Sugiere acciones basadas en ubicación

### 📊 Gestión de Datos
- **7 Endpoints REST**: Tasks, Notes, Calendar, Inventory, Learning, AI Logs, Analytics
- **Base de Datos PostgreSQL**: Con soporte para Supabase
- **Autenticación JWT**: Seguridad completa

### 🎨 Interfaz Visual
- **Diseño Bolt.new Style**: Tarjetas modernas y animaciones
- **Dashboard Streamlit**: Visualización en tiempo real
- **Responsive Design**: Funciona en todos los dispositivos

### ☁️ Integración Cloud
- **Google Colab**: Procesamiento GPU gratuito
- **LocalTunnel**: Acceso público desde cualquier lugar
- **Calendarios**: Sincronización con Google Calendar

## 🛠️ Instalación y Configuración

### Opción 1: Desarrollo Local

```bash
# Clonar el proyecto
cd /Users/luis_genji/CascadeProjects/ecosistema_luis

# Instalar dependencias
pip install -r requirements.txt

# Iniciar base de datos (PostgreSQL o SQLite)
export DATABASE_URL="sqlite:///./ecosistema_luis.db"

# Iniciar API
cd api
python main.py

# Iniciar Streamlit (en otra terminal)
cd ../streamlit
streamlit run app.py
```

### Opción 2: Google Colab (Recomendado)

1. Sube los archivos a Google Drive
2. Abre Google Colab y monta tu Drive
3. Ejecuta el script de configuración:

```python
# En una celda de Colab
!pip install -q streamlit
!npm install -g localtunnel

# Copiar y ejecutar el script de configuración
exec(open('/content/drive/MyDrive/ecosistema_luis/colab/setup_colab.py').read())
```

4. Accede a tu app mediante la URL generada

## 📋 Endpoints de la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/tasks` | GET/POST/PUT/DELETE | Gestión de tareas con IA |
| `/api/v1/notes` | GET/POST | Notas y categorías |
| `/api/v1/calendar-events` | GET/POST | Eventos y calendarios |
| `/api/v1/inventory` | GET/POST | Control de inventario |
| `/api/v1/learning` | GET/POST | Seguimiento de aprendizaje |
| `/api/v1/ai-priority-logs` | GET | Logs de decisiones de IA |
| `/api/v1/analytics/productivity` | GET | Análisis de patrones |

## 🎯 Contextos Inteligentes

El sistema se adapta a tres contextos principales:

### 🏪 Local Xicopack
- **Prioridad**: Limpieza y atención al cliente
- **Recomendaciones**: Cotizaciones, inventario, logística

### 🏠 Casa / Estudio
- **Prioridad**: Optimización y desarrollo
- **Recomendaciones**: Actualización web, contenido digital

### 🎸 Evento Musical
- **Prioridad**: Preparación y promoción
- **Recomendaciones**: Ensayos, material, logística

## 🔧 Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework API de alto rendimiento
- **SQLAlchemy**: ORM para base de datos
- **PyTorch**: Redes neuronales y deep learning
- **JWT**: Autenticación segura

### Frontend
- **Streamlit**: Dashboard interactivo
- **Plotly**: Visualización de datos
- **CSS3**: Diseño moderno y responsive

### Cloud & DevOps
- **Google Colab**: GPU gratuita para ML
- **LocalTunnel**: Túneles públicos
- **Supabase**: Base de datos como servicio

## 🎨 Inspiración de Diseño

La interfaz está inspirada en tu código Bolt.new con:
- **Tarjetas animadas** con hover effects
- **Colores consistentes** para cada tipo de contenido
- **Iconos descriptivos** para mejor UX
- **Layout responsive** y moderno

## 📊 Métricas y Analytics

El sistema incluye análisis automático de:
- **Tasa de completación** de tareas
- **Mejores horas** de productividad
- **Patrones por contexto**
- **Confianza de la IA** en predicciones

## 🔐 Seguridad

- **Tokens JWT** para autenticación
- **Hashing de contraseñas** con bcrypt
- **CORS configurado** para desarrollo
- **Validación de inputs** en todos los endpoints

## 🚀 Despliegue

### Producción (Railway/Render)
```bash
# Variables de entorno
DATABASE_URL=postgresql://...
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SECRET_KEY=your-jwt-secret
```

### Desarrollo
```bash
# Base de datos local
export DATABASE_URL="sqlite:///./ecosistema_luis.db"
python api/main.py
streamlit run streamlit/app.py
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Pull Request

## 📄 Licencia

MIT License - Libre para uso personal y comercial

## 🎯 Próximos Pasos

- [ ] Integración con Shopify API
- [ ] Sincronización con Google Calendar
- [ ] App móvil con React Native
- [ ] Dashboard avanzado con más métricas
- [ ] Sistema de notificaciones push

---

**Creado con ❤️ para el Ecosistema Luis - Productividad Inteligente**
