import pandas as pd

def auditor_seguridad_google():
    try:
        # Cargamos el export de Shopify
        df = pd.read_csv("/Users/luis_genji/Downloads/products_export_1.csv")
        # Quitamos variantes para auditar solo el producto base
        df = df.drop_duplicates(subset=["Handle"])
        
        print("🛡️ AGENTE DE SEGURIDAD: LINEAMIENTOS DE GOOGLE")
        print("Auditando Títulos, Metas y URLs de tu tienda en vivo...\n")

        alertas = []

        for index, row in df.iterrows():
            # Shopify usa "SEO Title" y "SEO Description" en el export si se llenaron
            # Si no, usa el Title normal
            titulo = str(row.get("Page Title")) if pd.notna(row.get("Page Title")) else str(row["Title"])
            meta = str(row.get("Meta Description")) if pd.notna(row.get("Meta Description")) else ""
            handle = str(row["Handle"])
            
            error_msg = []

            # 1. Regla de Longitud de Título (Google corta después de 60 chars)
            if len(titulo) > 60:
                error_msg.append(f"Título muy largo ({len(titulo)}/60)")
            elif len(titulo) < 15:
                error_msg.append("Título muy corto")

            # 2. Regla de Meta Descripción (Google corta después de 155-160 chars)
            if meta == "" or meta == "nan":
                error_msg.append("Falta Meta Descripción")
            elif len(meta) > 155:
                error_msg.append(f"Meta muy larga ({len(meta)}/155)")
            elif len(meta) < 50:
                error_msg.append("Meta demasiado breve")

            # 3. Regla de URL (Handle) - Evitar guiones bajos y caracteres especiales
            if "_" in handle:
                error_msg.append("URL usa '_' (usar '-' mejor)")
            if re.search(r'[^a-zA-Z0-9-]', handle):
                error_msg.append("URL con caracteres especiales")

            if error_msg:
                alertas.append({
                    "Producto": titulo[:40],
                    "Alertas": " | ".join(error_msg)
                })

        if not alertas:
            print("✅ ¡TODO EN ORDEN! Tu tienda cumple con los lineamientos básicos de Google.")
        else:
            print(f"### ⚠️ ALERTA DE CUMPLIMIENTO SEO ({len(alertas)} productos) ⚠️\n")
            print("| Producto | Problema detectado |")
            print("| :--- | :--- |")
            for a in alertas[:25]:
                print(f"| {a['Producto']}... | **{a['Alertas']}** |")
            
            if len(alertas) > 25:
                print(f"\n> [!CAUTION]\n> Hay {len(alertas) - 25} productos adicionales que Google podría estar ignorando o penalizando.")

    except Exception as e:
        print(f"❌ Error en auditoría de seguridad: {e}")

if __name__ == "__main__":
    import re
    auditor_seguridad_google()
