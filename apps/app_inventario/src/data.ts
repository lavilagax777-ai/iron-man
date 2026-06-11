import type { Product } from './types';

export const CATEGORIES = ['Todos', 'Vasos', 'Contenedores', 'Platos y Charolas', 'Cubiertos', 'Accesorios'];

export const PRODUCTS: Product[] = [
  {
    id: 'XP-800',
    name: 'Contenedor Bio Bisagra Grande',
    description: 'Biodegradable premium para alimentos impermeables 9x9',
    category: 'Contenedores',
    department: 'FÉCULA DE MAÍZ',
    imageIcon: 'clamshell',
    variants: {
      caja: { sku: 'bis-gde', type: 'CAJA', price: 1950.00, quantityLabel: 'CAJA 200 Pzas', existence: 20 },
      paquete: { sku: 'bis-gde-p', type: 'PAQUETE', price: 540.00, quantityLabel: 'PQTE 50 Pzas', existence: 95 }
    }
  }
];
