import streamlit as st
import os
from dotenv import load_dotenv

# ─────────────────────────────────────────────
#  CONFIGURACIÓN INICIAL
# ─────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="Centro de Mando | Iron Man",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from brain.llm_router import route_to_llm
from brain.memory import test_supabase_connection, test_local_connection

# ─────────────────────────────────────────────
#  INTERFAZ — BARRA LATERAL
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Centro de Mando")
    st.divider()

    # ── Selector de Cerebro (LLM) ──
    st.subheader("🧠 Selector de Cerebro (LLM)")
    llm_choice = st.selectbox(
        "Elige el modelo:",
        options=["Gemini 1.5 Pro", "Llama 3 (vía OpenRouter)"],
        index=0,
    )

    st.info(
        "**Modo Premium (Google AI Studio):** Mientras tengas tu cuenta activa y quieras "
        "pasarle documentos larguísimos, seleccionas **Gemini 1.5 Pro**.\n\n"
        "**Modo Supervivencia (Llama 3):** Si un mes decides no renovar tu suscripción de Google "
        "y quieres algo totalmente gratis, seleccionas **Llama 3 (vía OpenRouter)** en ese mismo menú, "
        "y el sistema automáticamente manda las preguntas al servidor gratuito."
    )

    st.divider()

    # ── Selector de Memoria (Base de Datos) ──
    st.subheader("🗄️ Selector de Memoria (Base de Datos)")
    db_choice = st.selectbox(
        "Elige el entorno:",
        options=["Nube (Supabase)", "Almacenamiento Local (Por definir)"],
        index=0,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Probar Supabase", use_container_width=True):
            with st.spinner("Conectando..."):
                result = test_supabase_connection()
            st.session_state["db_test_result"] = result

    with col2:
        if st.button("💾 Probar Local", use_container_width=True):
            with st.spinner("Verificando..."):
                result = test_local_connection()
            st.session_state["db_test_result"] = result

    if "db_test_result" in st.session_state:
        st.markdown(st.session_state["db_test_result"])

    st.divider()
    st.caption(f"🤖 Modelo activo: **{llm_choice}**")
    st.caption(f"🗄️ Base de datos: **{db_choice}**")


# ─────────────────────────────────────────────
#  INTERFAZ — ÁREA PRINCIPAL DE CHAT
# ─────────────────────────────────────────────
st.title("🦾 Centro de Mando Personal")
st.markdown(
    f"Conversando con **{llm_choice}** · Memoria en **{db_choice}**"
)
st.divider()

# Inicializar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderizar historial existente
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta según el modelo seleccionado
    with st.chat_message("assistant"):
        with st.spinner(f"Procesando con {llm_choice}..."):
            response = route_to_llm(llm_choice, st.session_state.messages)

        st.markdown(response)

    # Guardar respuesta en historial
    st.session_state.messages.append({"role": "assistant", "content": response})
