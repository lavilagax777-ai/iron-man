"""
catalogo_qr.py  ·  Xicopack — Catálogo con Códigos QR
======================================================
Ejecutar:   streamlit run streamlit/catalogo_qr.py
Requiere:   pip install "qrcode[pil]" Pillow pandas streamlit
"""

import io
import os
import streamlit as st
import pandas as pd
import qrcode
from PIL import Image

# ─────────────────────────────────────────────
#  CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="📦 Catálogo QR · Xicopack",
    page_icon="📦",
    layout="wide",
)

# Rutas
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CSV_PATH   = os.path.join(BASE_DIR, "..", "productos_catalogo.csv")
FOTOS_DIR  = os.path.join(BASE_DIR, "..", "fotos_productos")
os.makedirs(FOTOS_DIR, exist_ok=True)

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
.main { background:#0d1117; }
section[data-testid="stSidebar"] { background:#161b22; }

.prod-card {
    background:#161b22;
    border:1px solid #30363d;
    border-radius:14px;
    padding:16px;
    margin-bottom:8px;
    transition: border-color .2s;
}
.prod-card:hover { border-color:#58a6ff; }

.precio-big  { font-size:1.6rem; font-weight:800; color:#3fb950; }
.sku-mono    { font-family:monospace; font-size:.8rem; color:#8b949e; }
.desc-small  { font-size:.86rem; color:#c9d1d9; line-height:1.5; }

.badge-caja {
    background:#1f6feb; color:#fff;
    padding:2px 10px; border-radius:20px;
    font-size:.72rem; font-weight:700;
    display:inline-block; margin-bottom:6px;
}
.badge-pqte {
    background:transparent; color:#58a6ff;
    padding:2px 10px; border-radius:20px;
    font-size:.72rem; font-weight:700;
    border:1px solid #388bfd;
    display:inline-block; margin-bottom:6px;
}
.sin-foto {
    background:#21262d;
    border:2px dashed #30363d;
    border-radius:10px;
    height:130px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#484f58;
    font-size:.82rem;
    margin-bottom:8px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  FUNCIONES
# ─────────────────────────────────────────────

@st.cache_data
def load_productos(path: str) -> pd.DataFrame:
    """Lee el CSV y normaliza columnas."""
    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise RuntimeError(f"No se pudo leer el CSV: {e}")

    df.columns = df.columns.str.strip()

    # Mapeo flexible de columnas
    rename = {}
    for col in df.columns:
        cl = col.lower()
        if cl in ("sku", "código", "codigo", "id"):
            rename[col] = "SKU"
        elif "desc" in cl or "nombre" in cl:
            rename[col] = "Descripcion"
        elif "precio" in cl or "price" in cl:
            rename[col] = "Precio"

    df = df.rename(columns=rename)

    # Garantizar columnas mínimas
    if "SKU" not in df.columns:
        df["SKU"] = df.index.astype(str)
    if "Descripcion" not in df.columns:
        df["Descripcion"] = "Sin descripción"
    if "Precio" not in df.columns:
        df["Precio"] = 0.0

    df["SKU"] = df["SKU"].astype(str).str.strip()
    df["Precio"] = (
        df["Precio"]
        .astype(str)
        .str.replace(r"[$,\s]", "", regex=True)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0.0)
    )

    # CAJA vs PAQUETE — SKU que termina en "P" = paquete
    df["Tipo"] = df["SKU"].apply(
        lambda s: "PAQUETE" if s.upper().endswith("P") else "CAJA"
    )
    # SKU raíz para enlazar pares CAJA ↔ PAQUETE
    df["SKU_raiz"] = df["SKU"].apply(
        lambda s: s[:-1] if s.upper().endswith("P") else s
    )
    return df


def generar_qr(texto: str) -> bytes:
    """Devuelve un QR como bytes PNG."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#3fb950", back_color="#0d1117")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def buscar_foto(sku: str) -> str | None:
    """Retorna la ruta de la foto si existe."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = os.path.join(FOTOS_DIR, f"{sku}.{ext}")
        if os.path.exists(p):
            return p
    return None


def fmt_precio(p: float) -> str:
    return f"${p:,.2f} MXN"


# ─────────────────────────────────────────────
#  CARGAR DATOS
# ─────────────────────────────────────────────
try:
    df = load_productos(CSV_PATH)
except RuntimeError as e:
    st.error(str(e))
    st.info(f"Ruta esperada del CSV:\n`{CSV_PATH}`")
    st.stop()


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Catálogo QR")
    st.caption("Xicopack · Todos Santos, BCS")
    st.divider()

    busqueda = st.text_input("🔍 Buscar", placeholder="SKU o nombre…")

    tipo_sel = st.multiselect(
        "Mostrar:",
        ["CAJA", "PAQUETE"],
        default=["CAJA", "PAQUETE"]
    )

    p_min = float(df["Precio"].min())
    p_max = float(df["Precio"].max()) or 1.0
    rango = st.slider(
        "Precio ($MXN)", p_min, p_max, (p_min, p_max), format="$%.0f"
    )

    cols_n = st.radio("Columnas:", [1, 2, 3], index=1, horizontal=True)

    st.divider()
    st.markdown("### 📷 Subir foto")
    sku_up   = st.text_input("SKU exacto").strip().upper()
    foto_up  = st.file_uploader("Imagen", type=["jpg","jpeg","png","webp"])
    if st.button("💾 Guardar foto") and sku_up and foto_up:
        ext  = foto_up.name.rsplit(".", 1)[-1].lower()
        dest = os.path.join(FOTOS_DIR, f"{sku_up}.{ext}")
        with open(dest, "wb") as f:
            f.write(foto_up.read())
        load_productos.clear()
        st.success(f"✅ Foto guardada → `{sku_up}.{ext}`")
        st.rerun()

    st.divider()
    st.caption(f"Total productos: **{len(df)}**")
    st.caption(f"Carpeta fotos: `fotos_productos/`")


# ─────────────────────────────────────────────
#  FILTRAR
# ─────────────────────────────────────────────
mask = df["Tipo"].isin(tipo_sel) & df["Precio"].between(rango[0], rango[1])
if busqueda.strip():
    q = busqueda.strip().lower()
    mask &= (
        df["SKU"].str.lower().str.contains(q, na=False) |
        df["Descripcion"].str.lower().str.contains(q, na=False)
    )

filtrado = df[mask].reset_index(drop=True)


# ─────────────────────────────────────────────
#  ENCABEZADO
# ─────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1f6feb33,#0d1117);
            border:1px solid #1f6feb55; border-radius:14px;
            padding:20px 26px; margin-bottom:20px;">
  <h1 style="margin:0; color:#e6edf3;">📦 Catálogo Xicopack con QR</h1>
  <p style="margin:4px 0 0; color:#8b949e; font-size:.9rem;">
    Precio por caja · Precio por paquete · Foto · Descripción · Código QR descargable
  </p>
</div>
""", unsafe_allow_html=True)

# Métricas rápidas
c1, c2, c3, c4 = st.columns(4)
c1.metric("📋 Mostrando",   len(filtrado), f"de {len(df)}")
c2.metric("📦 Cajas",       int((filtrado["Tipo"] == "CAJA").sum()))
c3.metric("🛍️ Paquetes",    int((filtrado["Tipo"] == "PAQUETE").sum()))
c4.metric("💰 Precio max",  fmt_precio(filtrado["Precio"].max()) if len(filtrado) else "—")

st.divider()

if filtrado.empty:
    st.warning("⚠️ Ningún producto coincide con los filtros.")
    st.stop()


# ─────────────────────────────────────────────
#  TARJETAS DE PRODUCTOS
# ─────────────────────────────────────────────
filas = [filtrado.iloc[i:i+cols_n] for i in range(0, len(filtrado), cols_n)]

for fila_df in filas:
    cols = st.columns(cols_n)

    for col, (_, prod) in zip(cols, fila_df.iterrows()):
        with col:
            sku    = prod["SKU"]
            desc   = prod["Descripcion"]
            precio = prod["Precio"]
            tipo   = prod["Tipo"]

            # ── Badge tipo
            if tipo == "CAJA":
                badge_html = '<span class="badge-caja">📦 PRECIO CAJA</span>'
            else:
                badge_html = '<span class="badge-pqte">🛍️ PRECIO PAQUETE</span>'

            # ── Foto
            foto = buscar_foto(sku)
            if foto:
                st.image(foto, use_container_width=True)
            else:
                st.markdown(
                    "<div class='sin-foto'>📷 Sin foto · sube una en el panel</div>",
                    unsafe_allow_html=True
                )

            # ── Tarjeta info
            st.markdown(f"""
            <div class="prod-card">
              {badge_html}
              <div class="sku-mono">SKU: {sku}</div>
              <div class="desc-small" style="margin:8px 0 10px;">{desc}</div>
              <div class="precio-big">{fmt_precio(precio)}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Precio del par (CAJA ↔ PAQUETE)
            raiz = prod["SKU_raiz"]
            par  = df[(df["SKU_raiz"] == raiz) & (df["SKU"] != sku)]
            if not par.empty:
                p = par.iloc[0]
                icono = "📦" if p["Tipo"] == "CAJA" else "🛍️"
                st.caption(
                    f"{icono} También: **{p['Tipo'].capitalize()}** "
                    f"{fmt_precio(p['Precio'])} · SKU `{p['SKU']}`"
                )

            # ── QR
            qr_bytes = generar_qr(sku)
            qr_col1, qr_col2 = st.columns([1, 1])
            with qr_col1:
                st.image(qr_bytes, caption=f"QR · {sku}", use_container_width=True)
            with qr_col2:
                st.download_button(
                    "⬇️ Descargar QR",
                    data=qr_bytes,
                    file_name=f"qr_{sku}.png",
                    mime="image/png",
                    key=f"dl_qr_{sku}",
                    use_container_width=True,
                )
                # QR del precio también
                qr_precio = generar_qr(f"{sku} | {desc[:40]} | {fmt_precio(precio)}")
                st.download_button(
                    "⬇️ QR con precio",
                    data=qr_precio,
                    file_name=f"qr_precio_{sku}.png",
                    mime="image/png",
                    key=f"dl_precio_{sku}",
                    use_container_width=True,
                )

            st.markdown("---")


# ─────────────────────────────────────────────
#  TABLA EXPORTABLE
# ─────────────────────────────────────────────
with st.expander("📊 Ver todos los productos en tabla"):
    show = filtrado[["SKU", "Tipo", "Descripcion", "Precio"]].copy()
    show["Precio"] = show["Precio"].apply(fmt_precio)
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.download_button(
        "📥 Exportar CSV filtrado",
        filtrado.to_csv(index=False).encode(),
        file_name="catalogo_filtrado.csv",
        mime="text/csv",
    )
