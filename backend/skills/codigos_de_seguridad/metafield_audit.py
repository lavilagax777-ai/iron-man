import pandas as pd
import re

def audit_shopify_vivo():
    try:
        # Cargar la exportación de Shopify
        df_shopify = pd.read_csv("/Users/luis_genji/Downloads/products_export_1.csv")
        
        # Nos enfocamos solo en productos únicos (no variantes repetidas si no es necesario)
        # y que tengan un Título
        df_shopify = df_shopify.dropna(subset=["Handle", "Title"])

        print("🤖 AGENTE: AUDITOR DE TIENDA EN VIVO (SHOPIFY)")
        print("Revisando los productos publicados en tu página...\n")

        errores = []

        for index, row in df_shopify.iterrows():
            # Combinamos Título y Descripción para la búsqueda
            titulo = str(row["Title"]).upper()
            cuerpo = str(row.get("Body (HTML)", "")).upper()
            contenido_total = titulo + " " + cuerpo
            
            handle = row["Handle"]
            faltantes = []

            # 1. Buscar Material
            materiales = ["PLA", "BAGAZO", "CAÑA", "BAMBÚ", "MADERA", "FÉCULA", "AGAVE", "KRAFT", "CARTÓN", "PAPEL"]
            if not any(m in contenido_total for m in materiales):
                faltantes.append("Material")

            # 2. Buscar Capacidad/Medida
            if not re.search(r'\d+\s?(OZ|ML|CM|IN|")|(\d+X\d+)|DIV', contenido_total):
                faltantes.append("Medida/Capacidad")

            # 3. Buscar Unidades
            unidades = ["CJ", "CAJA", "PZ", "PIEZA", "PK", "PAQUETE", "CON ", "C/"]
            if not any(u in contenido_total for u in unidades):
                # Buscamos patrones como "1000 pz" o "C/500"
                if not re.search(r'\d+\s?PZ|C/\d+', contenido_total):
                    faltantes.append("Unidades por empaque")

            if faltantes:
                errores.append({
                    "Handle": handle,
                    "Producto": row["Title"][:40],
                    "Faltante": ", ".join(faltantes)
                })

        # Reporte Final
        if not errores:
            print("✅ ¡EXCELENTE! Todos tus productos en Shopify están optimizados con info técnica.")
        else:
            # Eliminamos duplicados por Handle (ya que un producto puede tener muchas variantes)
            df_errores = pd.DataFrame(errores).drop_duplicates(subset=["Handle"])
            
            print(f"### 🚨 PRODUCTOS EN SHOPIFY QUE NECESITAN OPTIMIZACIÓN ({len(df_errores)} detectados) 🚨\n")
            print("| Producto (URL) | ¿Qué le falta en su página? |")
            print("| :--- | :--- |")
            
            for _, e in df_errores.head(30).iterrows():
                print(f"| {e['Producto']}... | **{e['Faltante']}** |")
            
            if len(df_errores) > 30:
                print(f"\n> [!IMPORTANT]\n> Tienes {len(df_errores) - 30} productos más que no tienen material o medida en su descripción de Shopify.")

    except Exception as e:
        print(f"❌ Error al procesar Shopify: {e}")

if __name__ == "__main__":
    audit_shopify_vivo()
