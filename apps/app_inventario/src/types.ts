export interface ProductVariant {
  sku: string;
  type: 'CAJA' | 'PAQUETE';
  quantityLabel: string; // e.g., "2,000 Pzas.", "50 Pzas."
  price: number;
  existence: string | number; // e.g., "3.00", "0.00", "N/A"
}

export interface Product {
  id: string;
  name: string;
  category: string;
  department: string;
  description: string;
  imageIcon: string; // Used to select a premium mockup/icon
  imageUrl?: string; // Modificado: Ahora vendrá de Firebase Storage, NO de Supabase
  variants: {
    caja?: ProductVariant;
    paquete?: ProductVariant;
  };
}

export interface FilterState {
  search: string;
  category: string;
}

export interface QuoteItem {
  product: Product;
  selectedVariant: 'CAJA' | 'PAQUETE';
  quantity: number;
}
