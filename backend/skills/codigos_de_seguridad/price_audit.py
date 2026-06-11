import pandas as pd
import re
import sys

def clean_price(p):
    if pd.isna(p) or p == "": return 0.0
    # Eliminar $, comas y espacios
    p = str(p).replace("$", "").replace(",", "").strip()
    try:
        return float(p)
    except:
        return 0.0

def run_price_audit():
    try:
        # 1. Cargar archivos
        master_path = "/Users/luis_genji/Downloads/ListaPreciosultima - Hoja 1.csv"
        shopify_path = "/Users/luis_genji/Downloads/products_export_1.csv"
        
        df_master = pd.read_csv(master_path, skiprows=2)
        df_shopify = pd.read_csv(shopify_path)

        # 2. Limpieza Master List
        df_master = df_master[["Clave", "Descripción", "Precio"]].dropna(subset=["Clave"])
        df_master["SKU"] = df_master["Clave"].astype(str).str.strip()
        df_master["Precio_Master"] = df_master["Precio"].apply(clean_price)

        # 3. Limpieza Shopify Export
        df_shopify = df_shopify[["Variant SKU", "Variant Price", "Title"]].dropna(subset=["Variant SKU"])
        df_shopify["SKU"] = df_shopify["Variant SKU"].astype(str).str.strip()
        df_shopify["Precio_Shopify"] = df_shopify["Variant Price"].apply(clean_price)

        # 4. Cruce de datos (Merge)
        merged = pd.merge(df_master, df_shopify, on="SKU", how="inner")

        # 5. Cálculo de Diferencia
        merged["Diferencia"] = merged["Precio_Master"] - merged["Precio_Shopify"]

        # 6. Filtrar solo los que tienen error
        errors = merged[abs(merged["Diferencia"]) > 0.01].copy()

        print("💰 AGENTE: AUDITOR DE PRECIOS (LISTA MAESTRA VS SHOPIFY)")
        
        if errors.empty:
            print("✅ EXCELENTE: Todos los precios en Shopify coinciden con tu Lista Maestra.")
        else:
            print(f"### 🚨 REPORTE DE DISCREPANCIAS DE PRECIOS ({len(errors)} detectadas) 🚨")
            print("\n| SKU | Producto | Precio Lista | Shopify | Diferencia |")
            print("| :--- | :--- | :---: | :---: | :---: |")
            
            for _, row in errors.head(30).iterrows():
                print(f"| {row['SKU']} | {str(row['Title'])[:40]}... | ${row['Precio_Master']:,.2f} | ${row['Precio_Shopify']:,.2f} | **${row['Diferencia']:,.2f}** |")
            
            if len(errors) > 30:
                print(f"\n> [!NOTE]\n> Hay {len(errors) - 30} discrepancias adicionales que no se muestran aquí.")

    except Exception as e:
        print(f"❌ Error al procesar la auditoría de precios: {e}")

if __name__ == "__main__":
    run_price_audit()
