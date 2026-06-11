import { useState } from 'react';
import type { Product } from '../types';
import { PRODUCTS } from '../data';

interface PresentationViewProps {
  products?: Product[];
}

export function PresentationView({ products = PRODUCTS }: PresentationViewProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('Todos');
  const [slideIndex, setSlideIndex] = useState<number>(0);

  const filteredProducts = products.filter(p => 
    selectedCategory === 'Todos' || p.category === selectedCategory
  );

  const activeProducts = filteredProducts.length > 0 ? filteredProducts : products;
  const currentIndex = Math.min(slideIndex, activeProducts.length - 1);
  const currentProduct = activeProducts[currentIndex];

  if (!currentProduct) return <div>No hay productos para mostrar en presentación.</div>;

  return (
    <div className="bg-white rounded-2xl border border-stone-200/60 p-8 text-center space-y-6">
      <h2 className="text-2xl font-bold text-stone-800">Modo Presentación</h2>
      <div className="max-w-md mx-auto bg-stone-50 p-6 rounded-xl border border-stone-100">
        <div className="h-48 mb-4 flex items-center justify-center">
          {currentProduct.imageUrl ? (
            <img src={currentProduct.imageUrl} alt={currentProduct.name} className="h-full object-contain" />
          ) : (
            <div className="text-4xl">📦</div>
          )}
        </div>
        <h3 className="text-lg font-bold">{currentProduct.name}</h3>
        <p className="text-stone-500 text-sm mt-2">{currentProduct.description}</p>
      </div>
      <div className="flex justify-center gap-4">
        <button 
          onClick={() => setSlideIndex(Math.max(0, currentIndex - 1))}
          className="px-4 py-2 bg-stone-100 rounded-lg hover:bg-stone-200"
        >
          Anterior
        </button>
        <button 
          onClick={() => setSlideIndex(Math.min(activeProducts.length - 1, currentIndex + 1))}
          className="px-4 py-2 bg-stone-100 rounded-lg hover:bg-stone-200"
        >
          Siguiente
        </button>
      </div>
    </div>
  );
}
