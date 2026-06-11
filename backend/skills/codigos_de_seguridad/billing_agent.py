import pandas as pd

def clean_price(p):
    if pd.isna(p) or p == "": return 0.0
    p = str(p).replace("$", "").replace(",", "").strip()
    try:
        return float(p)
    except:
        return 0.0

def run_billing_audit():
    try:
        print("🧾 AGENTE: AUDITOR DE FACTURACIÓN Y COSTOS")
        print("Analizando márgenes y configuración fiscal en Shopify...\n")

        # Cargar Shopify Export
        shopify_path = "/Users/luis_genji/Downloads/products_export_1.csv"
        df = pd.read_csv(shopify_path)

        # Seleccionar columnas relevantes
        # Shopify usa 'Cost per item' en el export
        cols = ["Variant SKU", "Title", "Variant Price", "Cost per item", "Variant Taxable"]
        df_audit = df[cols].copy()

        df_audit["Price"] = df_audit["Variant Price"].apply(clean_price)
        df_audit["Cost"] = df_audit["Cost per item"].apply(clean_price)
        
        # 1. Auditoría de Costos Faltantes
        missing_costs = df_audit[df_audit["Cost"] == 0].copy()
        
        # 2. Auditoría de Impuestos (Taxable)
        not_taxable = df_audit[df_audit["Variant Taxable"] == False].copy()

        # 3. Alerta de Margen Crítico (Margen < 15%)
        # Margen = (Precio - Costo) / Precio
        df_audit["Margin"] = (df_audit["Price"] - df_audit["Cost"]) / df_audit["Price"]
        low_margin = df_audit[(df_audit["Cost"] > 0) & (df_audit["Margin"] < 0.15)].copy()

        # Reporte
        if missing_costs.empty and not_taxable.empty and low_margin.empty:
            print("✅ TODO EN ORDEN: Costos, impuestos y márgenes configurados correctamente.")
        else:
            if not missing_costs.empty:
                print(f"### ❌ COSTOS FALTANTES ({len(missing_costs)} variantes) ❌")
                print("| SKU | Producto |")
                print("| :--- | :--- |")
                for _, row in missing_costs.head(10).iterrows():
                    print(f"| {row['Variant SKU']} | {str(row['Title'])[:40]}... |")
                print("")

            if not not_taxable.empty:
                print(f"### ⚠️ PRODUCTOS NO GRAVABLES ({len(not_taxable)} variantes) ⚠️")
                print("| SKU | Producto |")
                print("| :--- | :--- |")
                for _, row in not_taxable.head(10).iterrows():
                    print(f"| {row['Variant SKU']} | {str(row['Title'])[:40]}... |")
                print("")

            if not low_margin.empty:
                print(f"### 📉 ALERTA DE MARGEN CRÍTICO (<15%) 📉")
                print("| SKU | Producto | Margen |")
                print("| :--- | :--- | :---: |")
                for _, row in low_margin.head(10).iterrows():
                    print(f"| {row['Variant SKU']} | {str(row['Title'])[:40]}... | **{row['Margin']*100:.1f}%** |")

    except Exception as e:
        print(f"❌ Error en auditoría de facturación: {e}")

if __name__ == "__main__":
    run_billing_audit()
