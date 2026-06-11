import streamlit as st
import concurrent.futures
import subprocess
import time
import os
import json
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Xicopack · Centro de Mando",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Dark premium background */
.main { background-color: #0d1117; }
section[data-testid="stSidebar"] { background-color: #161b22; }

/* Metric cards */
div[data-testid="metric-container"] {
    background-color: #1e2430;
    padding: 18px 20px;
    border-radius: 12px;
    border: 1px solid #30363d;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}

/* Primary button */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 3.2em;
    background: linear-gradient(135deg, #ff4b4b, #c0392b);
    color: white;
    font-weight: 700;
    font-size: 1rem;
    border: none;
    letter-spacing: 0.5px;
    transition: transform 0.1s ease, box-shadow 0.1s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255,75,75,0.4);
}

/* Report cards */
.report-card {
    background-color: #161b22;
    padding: 22px;
    border-radius: 14px;
    border-left: 5px solid #ff4b4b;
    margin-bottom: 18px;
}
.report-card-ok  { border-left-color: #2ea043; }
.report-card-err { border-left-color: #e74c3c; }

/* Log area */
.log-box {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px;
    font-family: monospace;
    font-size: 0.82rem;
    color: #8b949e;
    max-height: 260px;
    overflow-y: auto;
    margin-bottom: 16px;
}
/* Badge */
.badge {
    display:inline-block;
    padding:3px 10px;
    border-radius:20px;
    font-size:0.75rem;
    font-weight:600;
    margin-right:6px;
}
.badge-green { background:#2ea043; color:#fff; }
.badge-red   { background:#e74c3c; color:#fff; }
.badge-blue  { background:#1f6feb; color:#fff; }
.badge-gray  { background:#30363d; color:#ccc; }

/* Bot Studio */
.bot-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
    transition: border-color 0.2s;
}
.bot-card:hover { border-color: #58a6ff; }
.bot-status-active   { color: #2ea043; font-weight:700; }
.bot-status-draft    { color: #e3b341; font-weight:700; }
.bot-status-disabled { color: #6e7681; font-weight:700; }
.code-output {
    background:#0d1117;
    border:1px solid #30363d;
    border-radius:10px;
    padding:14px;
    font-family:monospace;
    font-size:0.83rem;
    color:#c9d1d9;
    white-space:pre-wrap;
    max-height:340px;
    overflow-y:auto;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

HISTORY_FILE  = "ejecuciones.json"
BOT_REGISTRY  = "bot_registry.json"

BOT_TEMPLATE = '''# ──────────────────────────────────────────
# Bot: {name}
# Descripción: {desc}
# Creado: {date}
# ──────────────────────────────────────────

def run():
    print("🤖 Bot {name} ejecutándose...")
    # ── Escribe tu lógica aquí ──
    print("✅ Tarea completada.")

if __name__ == "__main__":
    run()
'''

def detect_environment():
    """Detecta si corremos en Colab o local."""
    if os.path.exists("/content"):
        return "☁️ Google Colab", "/content/"
    return "💻 Local", str(Path(__file__).parent) + "/"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_history(entry: dict):
    history = load_history()
    history.insert(0, entry)
    history = history[:20]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

# ── BOT REGISTRY HELPERS ─────────────────
def load_bots() -> dict:
    """Carga el registro de bots desde JSON."""
    if os.path.exists(BOT_REGISTRY):
        with open(BOT_REGISTRY) as f:
            return json.load(f)
    return {}

def save_bots(registry: dict):
    with open(BOT_REGISTRY, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def write_bot_file(filename: str, code: str, base_path: str):
    """Escribe el archivo .py del bot en disco."""
    full_path = os.path.join(base_path, filename)
    with open(full_path, "w") as f:
        f.write(code)
    return full_path

def run_bot_code(script_path: str, timeout: int = 60):
    """Ejecuta un bot y devuelve (éxito, stdout, stderr, duración)."""
    t0 = time.time()
    try:
        res = subprocess.run(
            ["python3", script_path],
            capture_output=True, text=True, timeout=timeout
        )
        return res.returncode == 0, res.stdout, res.stderr, round(time.time()-t0, 2)
    except subprocess.TimeoutExpired:
        return False, "", f"⏱️ Timeout ({timeout}s) excedido.", round(time.time()-t0, 2)
    except Exception as e:
        return False, "", str(e), round(time.time()-t0, 2)

def run_agent(name: str, script_path: str):
    """Ejecuta un agente y retorna (nombre, éxito, salida, duración)."""
    t0 = time.time()
    if not os.path.exists(script_path):
        return name, False, f"❌ Archivo no encontrado: `{script_path}`", 0.0
    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout or "(sin salida estándar)"
        if result.returncode != 0 and result.stderr:
            output += f"\n\n⚠️ **stderr:**\n```\n{result.stderr.strip()}\n```"
        success = result.returncode == 0
    except subprocess.TimeoutExpired:
        output = "⏱️ Tiempo máximo excedido (120 s). El agente fue interrumpido."
        success = False
    except Exception as exc:
        output = f"💥 Excepción inesperada: {exc}"
        success = False
    return name, success, output, round(time.time() - t0, 2)

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    env_label, base_path = detect_environment()
    history = load_history()

    # ── SIDEBAR ──────────────────────────────
    with st.sidebar:
        st.markdown("## 🐝 Xicopack Hive")
        st.caption("Panel de Control · Todos Santos, BCS")
        st.divider()

        # Contexto personal
        st.markdown("### 📍 Contexto Actual")
        ubicacion = st.radio("Ubicación:", ["🏪 Local Xicopack", "🏠 Casa / Estudio"], index=0)
        prioridad = {
            "🏪 Local Xicopack": "Atención a clientes · Avanzar cotizaciones si está libre",
            "🏠 Casa / Estudio": "Optimización Shopify · Carga de inventario · Música",
        }[ubicacion]
        st.info(f"**Prioridad ahora:**\n{prioridad}")

        st.divider()

        # Selección de agentes
        st.markdown("### 🤖 Agentes a Ejecutar")
        agents_toggle = {
            "AUDITOR TÉCNICO (Metafields)": st.checkbox("🔩 Auditor Técnico",     value=True),
            "SEGURIDAD GOOGLE (SEO)":        st.checkbox("🔍 Seguridad Google SEO", value=True),
            "AUDITOR DE PRECIOS":            st.checkbox("💰 Auditor de Precios",   value=True),
            "AUDITOR DE FACTURACIÓN":        st.checkbox("🧾 Auditor de Facturación",value=True),
            "CIBERSEGURIDAD":                st.checkbox("🛡️ Ciberseguridad",        value=True),
        }
        agent_files = {
            "AUDITOR TÉCNICO (Metafields)": "metafield_audit.py",
            "SEGURIDAD GOOGLE (SEO)":        "seo_security_audit.py",
            "AUDITOR DE PRECIOS":            "price_audit.py",
            "AUDITOR DE FACTURACIÓN":        "billing_agent.py",
            "CIBERSEGURIDAD":                "security_leak_audit.py",
        }
        n_selected = sum(1 for v in agents_toggle.values() if v)

        st.divider()
        st.markdown("### ⚙️ Entorno")
        st.code(env_label, language=None)
        st.caption(f"Base path: `{base_path}`")

    # ── HEADER ───────────────────────────────
    st.title("🐝 Xicopack Agent Hive")
    st.subheader("Orquestador Central de Auditoría · Todos Santos, BCS")

    # ── TABS ─────────────────────────────────
    tab_home, tab_bots, tab_context, tab_history, tab_report = st.tabs(
        ["🚀 Ejecutar", "🛠️ Bot Studio", "🎛️ Mi Contexto", "📋 Historial", "📄 Último Reporte"]
    )

    # ══════════════════════════════════════════
    #  TAB 1: EJECUTAR
    # ══════════════════════════════════════════
    with tab_home:
        # Métricas de estado rápido
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🤖 Agentes seleccionados", n_selected, delta=f"de {len(agents_toggle)}")
        c2.metric("📁 Archivos .py presentes",
                  sum(1 for f in agent_files.values() if os.path.exists(base_path + f)),
                  delta=f"de {len(agent_files)}")
        c3.metric("📋 Ejecuciones guardadas", len(history))
        c4.metric("📍 Modo", env_label.split()[0])

        st.divider()

        btn_col, info_col = st.columns([2, 3])

        with btn_col:
            run_clicked = st.button("🚀 INICIAR AUDITORÍA MASIVA", type="primary")
            st.caption("Todos los agentes seleccionados corren en paralelo.")

        with info_col:
            st.markdown("""
            **¿Cómo funciona?**
            1. Cada agente es un script Python independiente.
            2. Corren **en paralelo** (ThreadPoolExecutor) para mayor velocidad.
            3. Los resultados se agregan en un reporte Markdown descargable.
            4. El historial se guarda localmente en `ejecuciones.json`.
            """)

        if run_clicked:
            selected = {
                name: base_path + agent_files[name]
                for name, enabled in agents_toggle.items() if enabled
            }
            if not selected:
                st.warning("⚠️ Selecciona al menos un agente en la barra lateral.")
                st.stop()

            # UI dinámica
            progress_bar = st.progress(0, text="Iniciando agentes...")
            log_placeholder = st.empty()
            log_lines = []

            def log(msg):
                log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
                log_placeholder.markdown(
                    "<div class='log-box'>" +
                    "<br>".join(log_lines[-14:]) +
                    "</div>",
                    unsafe_allow_html=True
                )

            log(f"🕐 Inicio de auditoría · {n_selected} agentes seleccionados")

            reports     = []
            ok_count    = 0
            err_count   = 0
            total       = len(selected)
            completed   = 0
            start_time  = time.time()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(run_agent, name, path): name
                           for name, path in selected.items()}

                for future in concurrent.futures.as_completed(futures):
                    name, success, output, duration = future.result()
                    completed += 1
                    progress_bar.progress(completed / total,
                                          text=f"Completado: {name} ({completed}/{total})")
                    status_icon = "✅" if success else "❌"
                    log(f"{status_icon} {name} — {duration}s")

                    reports.append((name, success, output, duration))
                    if success: ok_count += 1
                    else:       err_count += 1

            total_time = round(time.time() - start_time, 2)
            log(f"🏁 Auditoría finalizada · {total_time}s · ✅{ok_count} ❌{err_count}")

            progress_bar.progress(1.0, text="✅ Auditoría completada.")

            st.divider()

            # Resumen de resultados
            r1, r2, r3 = st.columns(3)
            r1.metric("⏱️ Tiempo total", f"{total_time}s")
            r2.metric("✅ Exitosos", ok_count)
            r3.metric("❌ Con errores", err_count)

            # Tarjetas por agente
            st.markdown("### 📊 Reportes por Agente")
            for name, success, output, duration in sorted(reports, key=lambda x: not x[1]):
                card_class = "report-card-ok" if success else "report-card-err"
                badge_html = (
                    f'<span class="badge badge-green">✅ OK</span>'
                    if success else
                    f'<span class="badge badge-red">❌ Error</span>'
                )
                with st.expander(f"{'✅' if success else '❌'} {name} — {duration}s", expanded=success):
                    st.markdown(
                        f'<div class="report-card {card_class}">{badge_html}'
                        f'<span class="badge badge-gray">⏱ {duration}s</span>'
                        f'<br><br>{output}</div>',
                        unsafe_allow_html=True
                    )

            # Reporte completo
            report_md  = f"# 📊 REPORTE EJECUTIVO XICOPACK\n\n"
            report_md += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report_md += f"**Entorno:** {env_label}\n"
            report_md += f"**Tiempo total:** {total_time}s · ✅ {ok_count} exitosos · ❌ {err_count} con error\n\n---\n\n"
            for name, success, output, duration in reports:
                report_md += f"## {'✅' if success else '❌'} {name} ({duration}s)\n\n{output}\n\n---\n\n"

            with open("REPORTE_EJECUTIVO.md", "w") as f:
                f.write(report_md)

            # Guardar en historial
            save_history({
                "fecha":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "entorno":  env_label,
                "tiempo":   total_time,
                "ok":       ok_count,
                "error":    err_count,
                "agentes":  [r[0] for r in reports],
            })

            st.download_button(
                "📥 Descargar Reporte Completo (.md)",
                report_md,
                file_name=f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
            )

    # ══════════════════════════════════════════
    #  TAB 2: BOT STUDIO
    # ══════════════════════════════════════════
    with tab_bots:
        st.markdown("## 🛠️ Bot Studio")
        st.caption("Crea, edita, ejecuta y administra tus bots desde aquí — sin tocar archivos manualmente.")

        registry = load_bots()

        studio_col, panel_col = st.columns([3, 2], gap="large")

        # ── PANEL IZQUIERDO: Editor ───────────
        with studio_col:
            mode = st.radio(
                "Modo:",
                ["✨ Crear nuevo bot", "✏️ Editar bot existente"],
                horizontal=True
            )
            st.divider()

            if mode == "✨ Crear nuevo bot":
                st.markdown("### ✨ Nuevo Bot")
                nc1, nc2 = st.columns(2)
                bot_name = nc1.text_input(
                    "Nombre del bot",
                    placeholder="ej. precio_watcher",
                    key="new_bot_name"
                ).strip().replace(" ", "_").lower()
                bot_desc = nc2.text_input(
                    "Descripción corta",
                    placeholder="¿Qué hace este bot?",
                    key="new_bot_desc"
                )
                bot_status = st.selectbox(
                    "Estado inicial",
                    ["activo", "borrador", "desactivado"],
                    key="new_bot_status"
                )
                default_code = BOT_TEMPLATE.format(
                    name=bot_name or "mi_bot",
                    desc=bot_desc or "Sin descripción",
                    date=datetime.now().strftime("%Y-%m-%d")
                )
                bot_code = st.text_area(
                    "📝 Código del bot (Python)",
                    value=default_code,
                    height=360,
                    key="new_bot_code"
                )
                save_col, _ = st.columns([1, 2])
                if save_col.button("💾 Guardar bot", key="save_new_bot"):
                    if not bot_name:
                        st.error("⚠️ Ponle un nombre al bot antes de guardar.")
                    elif bot_name in registry:
                        st.error(f"⚠️ Ya existe un bot llamado `{bot_name}`. Usa el modo Editar.")
                    else:
                        filename = f"{bot_name}.py"
                        write_bot_file(filename, bot_code, base_path)
                        registry[bot_name] = {
                            "filename": filename,
                            "description": bot_desc,
                            "status": bot_status,
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        save_bots(registry)
                        st.success(f"✅ Bot `{bot_name}.py` guardado en `{base_path}`")
                        st.rerun()

            else:  # ── Editar bot existente ──
                st.markdown("### ✏️ Editar Bot Existente")
                if not registry:
                    st.info("Aún no has creado ningún bot. Usa el modo '✨ Crear nuevo bot'.")
                else:
                    bot_options = list(registry.keys())
                    selected_bot = st.selectbox(
                        "Selecciona un bot:",
                        bot_options,
                        key="edit_bot_select"
                    )
                    meta = registry[selected_bot]
                    full_path = os.path.join(base_path, meta["filename"])

                    # Cargar código actual
                    current_code = ""
                    if os.path.exists(full_path):
                        with open(full_path) as f:
                            current_code = f.read()
                    else:
                        st.warning(f"⚠️ El archivo `{meta['filename']}` no existe en disco. Puedes recrearlo aquí.")

                    edit_desc   = st.text_input("Descripción", value=meta.get("description", ""), key="edit_desc")
                    edit_status = st.selectbox(
                        "Estado",
                        ["activo", "borrador", "desactivado"],
                        index=["activo", "borrador", "desactivado"].index(meta.get("status", "borrador")),
                        key="edit_status"
                    )
                    edited_code = st.text_area(
                        "📝 Código",
                        value=current_code,
                        height=360,
                        key="edit_bot_code"
                    )

                    ec1, ec2, ec3 = st.columns(3)
                    if ec1.button("💾 Guardar cambios", key="save_edit"):
                        write_bot_file(meta["filename"], edited_code, base_path)
                        registry[selected_bot]["description"] = edit_desc
                        registry[selected_bot]["status"]      = edit_status
                        registry[selected_bot]["modified"]    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_bots(registry)
                        st.success(f"✅ `{meta['filename']}` actualizado.")
                        st.rerun()

                    if ec2.button("📋 Duplicar", key="dup_bot"):
                        new_key  = f"{selected_bot}_copia"
                        new_file = f"{new_key}.py"
                        write_bot_file(new_file, edited_code, base_path)
                        registry[new_key] = {
                            **meta,
                            "filename": new_file,
                            "status":   "borrador",
                            "created":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        save_bots(registry)
                        st.success(f"📋 Duplicado como `{new_key}`.")
                        st.rerun()

                    if ec3.button("🗑️ Eliminar", key="del_bot", type="secondary"):
                        # Borrar archivo si existe
                        if os.path.exists(full_path):
                            os.remove(full_path)
                        del registry[selected_bot]
                        save_bots(registry)
                        st.warning(f"🗑️ Bot `{selected_bot}` eliminado.")
                        st.rerun()

        # ── PANEL DERECHO: Ejecutar & Registro ─
        with panel_col:
            st.markdown("### ▶️ Ejecutar Bot")
            if not registry:
                st.info("No hay bots todavía. Créalos en el panel izquierdo.")
            else:
                run_target = st.selectbox(
                    "Bot a ejecutar:",
                    list(registry.keys()),
                    key="run_bot_select"
                )
                run_timeout = st.slider("Timeout (segundos)", 10, 120, 60, key="bot_timeout")

                if st.button("▶️ EJECUTAR", key="run_bot_btn"):
                    target_meta = registry[run_target]
                    target_path = os.path.join(base_path, target_meta["filename"])
                    with st.spinner(f"Ejecutando `{run_target}`..."):
                        ok, stdout, stderr, dur = run_bot_code(target_path, run_timeout)
                    if ok:
                        st.success(f"✅ Completado en {dur}s")
                    else:
                        st.error(f"❌ Error después de {dur}s")
                    if stdout:
                        st.markdown("**Salida:**")
                        st.markdown(
                            f"<div class='code-output'>{stdout}</div>",
                            unsafe_allow_html=True
                        )
                    if stderr:
                        st.markdown("**Errores / stderr:**")
                        st.markdown(
                            f"<div class='code-output' style='color:#ff7b72;'>{stderr}</div>",
                            unsafe_allow_html=True
                        )

            st.divider()
            st.markdown("### 📦 Registro de Bots")
            if not registry:
                st.caption("Vacío.")
            else:
                status_icon = {"activo": "🟢", "borrador": "🟡", "desactivado": "⚫"}
                for bname, bmeta in registry.items():
                    icon  = status_icon.get(bmeta.get("status", "borrador"), "⚪")
                    fpath = os.path.join(base_path, bmeta["filename"])
                    size  = f"{os.path.getsize(fpath):,}B" if os.path.exists(fpath) else "❌ no en disco"
                    st.markdown(
                        f"<div class='bot-card'>"
                        f"<strong>{icon} {bname}</strong><br>"
                        f"<small style='color:#8b949e;'>{bmeta.get('description','—')}</small><br>"
                        f"<small>📄 <code>{bmeta['filename']}</code> · {size}</small><br>"
                        f"<small>🕐 Modificado: {bmeta.get('modified','—')}</small>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

    # ══════════════════════════════════════════
    #  TAB 3: CONTEXTO PERSONAL
    # ══════════════════════════════════════════
    with tab_context:
        st.markdown("## 🎛️ Centro de Mando Personal")
        st.caption("Todos Santos, BCS · Luis Genji")

        p1, p2, p3 = st.tabs(["🛒 Shopify & Xicopack", "🎸 Música & Diálogos", "🤖 IA & Bots"])

        with p1:
            st.header("Xicopack · Tienda Física + Online")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("""
                **🏪 Tareas Local:**
                - Limpieza y atención a clientes
                - Avanzar cotizaciones cuando esté libre
                - Revisar stock físico vs Shopify
                """)
            with col_b:
                st.markdown("""
                **💻 Tareas Remotas (Casa):**
                - Optimización de página Shopify
                - Carga de inventario CSV
                - Análisis SEO y precios
                """)
            st.divider()
            st.markdown("**📅 Próximas acciones Shopify:**")
            acciones = {
                "Actualizar metafields de productos": "🟡 Pendiente",
                "Subir CSV con optimización SEO":    "🟡 Pendiente",
                "Auditoría de precios vs competencia":"✅ Completada",
                "Configurar descuentos mayoreo":     "🔴 Sin empezar",
            }
            for tarea, estado in acciones.items():
                st.markdown(f"- {estado} {tarea}")

        with p2:
            st.header("Música & Proyectos Creativos")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.subheader("📖 Diálogos")
                st.progress(0.35, text="Avance del libro: 35%")
                st.markdown("""
                - Capítulo actual en redacción
                - Grabación de álbum: pendiente sala
                """)
            with col_m2:
                st.subheader("🎸 Bandas")
                st.markdown("""
                | Integrante | Instrumento |
                |-----------|------------|
                | Lucho | Guitarra |
                | Ernesto | Bajo |
                | Iván | Batería |
                """)
            st.warning("🗓️ **Próximo evento importante: 6 de Julio**")

        with p3:
            st.header("IA & Infraestructura de Bots")
            st.markdown("""
            **🐝 Agentes activos en el Hive:**
            """)
            for name, fpath in agent_files.items():
                full = base_path + fpath
                exists = os.path.exists(full)
                icon = "🟢" if exists else "🔴"
                size = f"{os.path.getsize(full):,} bytes" if exists else "no encontrado"
                st.markdown(f"- {icon} **{name}** — `{fpath}` ({size})")

    # ══════════════════════════════════════════
    #  TAB 3: HISTORIAL
    # ══════════════════════════════════════════
    with tab_history:
        st.markdown("## 📋 Historial de Ejecuciones")
        history = load_history()
        if not history:
            st.info("Aún no hay ejecuciones registradas. Lanza tu primera auditoría en la pestaña 🚀.")
        else:
            for i, entry in enumerate(history):
                with st.expander(f"{'✅' if entry['error']==0 else '⚠️'} {entry['fecha']} — {entry['tiempo']}s", expanded=(i == 0)):
                    cols = st.columns(4)
                    cols[0].metric("Entorno",   entry.get("entorno", "—"))
                    cols[1].metric("⏱️ Tiempo",  f"{entry['tiempo']}s")
                    cols[2].metric("✅ OK",       entry["ok"])
                    cols[3].metric("❌ Errores",  entry["error"])
                    st.markdown("**Agentes ejecutados:** " + ", ".join(entry.get("agentes", [])))

    # ══════════════════════════════════════════
    #  TAB 4: ÚLTIMO REPORTE
    # ══════════════════════════════════════════
    with tab_report:
        st.markdown("## 📄 Último Reporte Ejecutivo")
        if os.path.exists("REPORTE_EJECUTIVO.md"):
            with open("REPORTE_EJECUTIVO.md") as f:
                content = f.read()
            mod_time = datetime.fromtimestamp(
                os.path.getmtime("REPORTE_EJECUTIVO.md")
            ).strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"Generado: {mod_time} · {len(content):,} caracteres")
            st.markdown(content)
            st.download_button(
                "📥 Descargar",
                content,
                file_name="REPORTE_EJECUTIVO.md",
                mime="text/markdown",
            )
        else:
            st.info("Aún no existe ningún reporte. Ejecuta una auditoría primero.")

if __name__ == "__main__":
    main()
