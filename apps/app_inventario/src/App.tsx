import { useState } from 'react';
import type { QuoteItem, Product } from './types';
import { PRODUCTS } from './data';
import { ProductCard } from './components/ProductCard';
import { CatalogDoc } from './components/CatalogDoc';
import { QuoteBuilder } from './components/QuoteBuilder';
import { PresentationView } from './components/PresentationView';
import { Search, PackageOpen } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'interactive' | 'document' | 'presentation' | 'quote'>('interactive');
  const [quoteItems, setQuoteItems] = useState<QuoteItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  const handleAddToQuote = (item: QuoteItem) => {
    setQuoteItems(prev => {
      const existing = prev.find(i => i.product.id === item.product.id && i.selectedVariant === item.selectedVariant);
      if (existing) {
        return prev.map(i => i === existing ? { ...i, quantity: i.quantity + item.quantity } : i);
      }
      return [...prev, item];
    });
    setActiveTab('quote');
  };

  const filteredProducts = PRODUCTS.filter(p => p.name.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="min-h-screen bg-stone-100 text-stone-900 font-sans p-4">
      <header className="mb-6 flex gap-4 overflow-x-auto pb-2 scrollbar-none">
        <button onClick={() => setActiveTab('interactive')} className={`whitespace-nowrap px-4 py-2 rounded-lg font-bold transition-colors ${activeTab === 'interactive' ? 'bg-emerald-800 text-white' : 'bg-white text-stone-600 hover:bg-stone-50'}`}>Catálogo Interactivo</button>
        <button onClick={() => setActiveTab('document')} className={`whitespace-nowrap px-4 py-2 rounded-lg font-bold transition-colors ${activeTab === 'document' ? 'bg-emerald-800 text-white' : 'bg-white text-stone-600 hover:bg-stone-50'}`}>Documento</button>
        <button onClick={() => setActiveTab('presentation')} className={`whitespace-nowrap px-4 py-2 rounded-lg font-bold transition-colors ${activeTab === 'presentation' ? 'bg-emerald-800 text-white' : 'bg-white text-stone-600 hover:bg-stone-50'}`}>Presentación</button>
        <button onClick={() => setActiveTab('quote')} className={`whitespace-nowrap px-4 py-2 rounded-lg font-bold transition-colors ${activeTab === 'quote' ? 'bg-emerald-800 text-white' : 'bg-white text-stone-600 hover:bg-stone-50'}`}>Cotizador ({quoteItems.length})</button>
      </header>
      
      <main>
        {activeTab === 'interactive' && (
          <div className="space-y-6">
            <div className="relative max-w-2xl mx-auto">
              <Search className="absolute left-4 top-3.5 text-stone-400 w-5 h-5" />
              <input type="text" placeholder="Buscar productos por nombre, SKU..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full pl-12 pr-4 py-3 rounded-2xl border border-stone-200 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all" />
            </div>
            
            {filteredProducts.length === 0 ? (
               <div className="text-center py-20 text-stone-500">
                  <PackageOpen className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  <p>No se encontraron productos</p>
               </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {filteredProducts.map(p => (
                  <ProductCard key={p.id} product={p} onAddToQuote={handleAddToQuote} onScanSku={() => {}} />
                ))}
              </div>
            )}
          </div>
        )}
        {activeTab === 'document' && <CatalogDoc onAddDirectVariant={() => {}} products={PRODUCTS} />}
        {activeTab === 'presentation' && <PresentationView products={PRODUCTS} />}
        {activeTab === 'quote' && (
          <QuoteBuilder 
            quoteItems={quoteItems} 
            onUpdateQuantity={(index, q) => setQuoteItems(prev => prev.map((item, i) => i === index ? { ...item, quantity: q } : item))} 
            onRemoveItem={index => setQuoteItems(prev => prev.filter((_, i) => i !== index))} 
            onClearQuote={() => setQuoteItems([])} 
            onBackToCatalog={() => setActiveTab('interactive')} 
          />
        )}
      </main>
    </div>
  );
}
