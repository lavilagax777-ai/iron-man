import type { Product } from '../types';
import { ShoppingBag, QrCode } from 'lucide-react';

interface ProductCardProps {
  product: Product;
  onAddToQuote: (item: any) => void;
  onScanSku: (sku: string) => void;
}

export function ProductCard({ product, onAddToQuote, onScanSku }: ProductCardProps) {
  return (
    <div className="bg-white border border-stone-200 rounded-2xl p-4 flex flex-col hover:shadow-lg transition-all">
      <div className="h-32 bg-stone-50 rounded-xl mb-4 flex items-center justify-center overflow-hidden">
        {product.imageUrl ? (
          <img src={product.imageUrl} alt={product.name} className="w-full h-full object-contain" />
        ) : (
          <div className="text-stone-300">📦</div>
        )}
      </div>
      <div className="text-xs text-stone-500 font-mono mb-1">{product.department}</div>
      <h3 className="font-bold text-stone-800 text-sm mb-2">{product.name}</h3>
      <p className="text-[10px] text-stone-500 mb-4 line-clamp-2">{product.description}</p>
      
      <div className="mt-auto space-y-2">
        {product.variants.caja && (
          <div className="flex justify-between items-center bg-emerald-50 p-2 rounded-lg">
            <div className="text-[10px]">
              <span className="font-bold text-emerald-800">CAJA</span>
              <div className="text-stone-500 font-mono">{product.variants.caja.sku}</div>
            </div>
            <div className="text-right">
              <div className="font-bold text-stone-800">${product.variants.caja.price}</div>
              <button 
                onClick={() => onAddToQuote({ product, selectedVariant: 'CAJA', quantity: 1 })}
                className="text-[9px] bg-emerald-600 text-white px-2 py-1 rounded"
              >
                Cotizar
              </button>
            </div>
          </div>
        )}
        {product.variants.paquete && (
          <div className="flex justify-between items-center bg-amber-50 p-2 rounded-lg">
            <div className="text-[10px]">
              <span className="font-bold text-amber-800">PQTE</span>
              <div className="text-stone-500 font-mono">{product.variants.paquete.sku}</div>
            </div>
            <div className="text-right">
              <div className="font-bold text-stone-800">${product.variants.paquete.price}</div>
              <button 
                onClick={() => onAddToQuote({ product, selectedVariant: 'PAQUETE', quantity: 1 })}
                className="text-[9px] bg-amber-600 text-white px-2 py-1 rounded"
              >
                Cotizar
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
