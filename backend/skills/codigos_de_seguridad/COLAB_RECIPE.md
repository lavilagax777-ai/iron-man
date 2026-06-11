# 📖 Receta Maestra v2: Streamlit en Google Colab
> **Xicopack Agent Hive · Todos Santos, BCS**

---

## CELDA 1 — Preparar entorno
```python
# @title 🛠️ 1. Instalación de herramientas
!pip install streamlit python-dotenv -q
!npm install -g localtunnel -q

import urllib, os
print("✅ Entorno listo.")
```

---

## CELDA 2 — Cargar tus credenciales (Secretos de Colab)
```python
# @title 🔑 2. Variables de entorno seguras
# Usa los Secretos de Colab (🔑 ícono en la barra lateral)
# para guardar SHOPIFY_TOKEN, SHOP_URL, etc. sin exponer el .env

from google.colab import userdata
import os

# Mapea tus secretos de Colab → variables de entorno
secretos = ["SHOPIFY_TOKEN", "SHOP_URL", "OPENAI_API_KEY"]
for key in secretos:
    try:
        os.environ[key] = userdata.get(key)
        print(f"✅ {key} cargado")
    except Exception:
        print(f"⚠️  {key} no encontrado en Secretos (continúa si no lo usas)")
```

---

## CELDA 3 — Subir tus archivos Python
```python
# @title 📂 3. Subir agentes desde tu computadora
from google.colab import files

print("Sube tus archivos .py (selecciona todos a la vez):")
uploaded = files.upload()

for fname, content in uploaded.items():
    with open(f"/content/{fname}", "wb") as f:
        f.write(content)
    print(f"✅ {fname} copiado a /content/")
```

**Archivos a subir:**
- `streamlit_app.py`
- `billing_agent.py`
- `metafield_audit.py`
- `price_audit.py`
- `security_leak_audit.py`
- `seo_security_audit.py`

---

## CELDA 4 — Verificar archivos presentes
```python
# @title 🔍 4. Verificar que todo esté listo
import os

archivos_requeridos = [
    "streamlit_app.py",
    "billing_agent.py",
    "metafield_audit.py",
    "price_audit.py",
    "security_leak_audit.py",
    "seo_security_audit.py",
]

print("📋 Estado de archivos en /content/:\n")
all_ok = True
for f in archivos_requeridos:
    ruta = f"/content/{f}"
    if os.path.exists(ruta):
        size = os.path.getsize(ruta)
        print(f"  ✅ {f}  ({size:,} bytes)")
    else:
        print(f"  ❌ {f}  — FALTA")
        all_ok = False

print("\n" + ("🚀 Todo listo. Continúa a la celda 5." if all_ok else "⚠️ Sube los archivos faltantes antes de continuar."))
```

---

## CELDA 5 — Lanzar la App 🚀
```python
# @title 🚀 5. Lanzar Streamlit + túnel público
import urllib, subprocess, threading, time

# Obtener IP pública para desbloquear LocalTunnel
public_ip = urllib.request.urlopen(
    'https://ipv4.icanhazip.com'
).read().decode('utf8').strip()

print(f"╔══════════════════════════════════════════════════╗")
print(f"║  1️⃣  TU IP PARA EL TÚNEL: {public_ip:<20}  ║")
print(f"╚══════════════════════════════════════════════════╝")
print()
print("⏳ Iniciando Streamlit... espera ~5 segundos...\n")

# Lanzar Streamlit en background
subprocess.Popen(
    ["streamlit", "run", "/content/streamlit_app.py",
     "--server.port", "8501",
     "--server.headless", "true",
     "--server.runOnSave", "true"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(5)

# Crear el túnel (esto bloquea la celda y muestra el enlace)
print("🌐 Generando enlace público...")
print("2️⃣  Cuando aparezca 'your url is: https://...loca.lt'")
print("    → Haz clic en ese enlace.")
print("3️⃣  En la página que abre, pega tu IP y da clic en Submit.\n")
!npx localtunnel --port 8501
```

---

## CELDA 5B — Alternativa: ngrok (más estable)
```python
# @title 🔀 5B. Alternativa con ngrok (más estable)
# Primero consigue un token gratis en https://ngrok.com/signup
# y guárdalo en Secretos de Colab como NGROK_TOKEN

from google.colab import userdata
import subprocess, time

NGROK_TOKEN = userdata.get("NGROK_TOKEN")

!pip install pyngrok -q
from pyngrok import ngrok, conf

conf.get_default().auth_token = NGROK_TOKEN

# Matar túneles previos si los hay
ngrok.kill()

# Lanzar Streamlit
subprocess.Popen(
    ["streamlit", "run", "/content/streamlit_app.py",
     "--server.port", "8501",
     "--server.headless", "true"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(5)

# Abrir túnel
tunnel = ngrok.connect(8501)
print(f"\n╔══════════════════════════════════════════════════╗")
print(f"║  🌐 TU APP ESTÁ EN:                              ║")
print(f"║  {tunnel.public_url:<48}  ║")
print(f"╚══════════════════════════════════════════════════╝")
print("\n✅ No necesitas IP ni contraseña. Abre el enlace directamente.")
```

---

## 💡 Tips Pro

| Situación | Solución |
|-----------|----------|
| Colab se desconecta solo | Abre la consola del navegador (F12) y pega: `setInterval(()=>{document.querySelector('#top-toolbar').click()}, 60000)` |
| El túnel pide contraseña | Usa la IP que imprimió la Celda 5 |
| Un agente da error | Revisa que el `.py` haya sido subido con la Celda 3 |
| Credenciales de Shopify | Guardar en Secretos de Colab (🔑), NO en el código |
| App no carga | Espera 10s y recarga. Si persiste, re-ejecuta la celda 5 |

---

## 🔄 Flujo Recomendado

```
Celda 1 → Celda 2 → Celda 3 → Celda 4 → Celda 5
  ↓           ↓         ↓          ↓          ↓
Instalar   Secrets   Subir .py  Verificar  ¡Lanzar!
```
