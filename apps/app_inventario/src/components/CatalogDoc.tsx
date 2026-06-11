import React, { useState } from 'react';
import type { Product } from '../types';
import { PRODUCTS, CATEGORIES } from '../data';
import { Search, Printer, FileText, CheckCircle, AlertCircle, ShoppingCart, HelpCircle } from 'lucide-react';

interface CatalogDocProps {
  onAddDirectVariant: (product: Product, variantType: 'CAJA' | 'PAQUETE') => void;
  products?: Product[];
}

export function CatalogDoc({ onAddDirectVariant, products = PRODUCTS }: CatalogDocProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Todos');
  const [currentPage, setCurrentPage] = useState(1);
  const [justAddedSku, setJustAddedSku] = useState<string | null>(null);

  // Filter products
  const filteredProducts = products.filter(prod => {
    const matchesSearch = prod.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          prod.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          prod.variants.caja?.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          prod.variants.paquete?.sku.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = selectedCategory === 'Todos' || prod.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Flatten products into their individual variants so they can be shown one-by-one, matching the PDF's list layout!
  // The user's screenshots show each CAJA and PQTE as separate rows!
  const catalogRows: Array<{
    product: Product;
    sku: string;
    type: 'CAJA' | 'PAQUETE';
    labelName: string;
    quantityLabel: string;
    price: number;
    existence: string | number;
  }> = [];

  filteredProducts.forEach(prod => {
    if (prod.variants.caja) {
      catalogRows.push({
        product: prod,
        sku: prod.variants.caja.sku,
        type: 'CAJA',
        labelName: `${prod.name} ${prod.variants.caja.quantityLabel}`,
        quantityLabel: prod.variants.caja.quantityLabel,
        price: prod.variants.caja.price,
        existence: prod.variants.caja.existence
      });
    }
    if (prod.variants.paquete) {
      catalogRows.push({
        product: prod,
        sku: prod.variants.paquete.sku,
        type: 'PAQUETE',
        labelName: `${prod.name} ${prod.variants.paquete.quantityLabel}`,
        quantityLabel: prod.variants.paquete.quantityLabel,
        price: prod.variants.paquete.price,
        existence: prod.variants.paquete.existence
      });
    }
  });

  const handleAddVariant = (row: typeof catalogRows[0]) => {
    onAddDirectVariant(row.product, row.type);
    setJustAddedSku(row.sku);
    setTimeout(() => {
      setJustAddedSku(null);
    }, 1200);
  };

  const handlePrint = () => {
    window.print();
  };

  const renderProductGraphic = (icon: string) => {
    switch (icon) {
      case 'straws':
        return (
          <svg className="w-16 h-16" viewBox="0 0 120 120">
            <rect x="35" y="15" width="50" height="90" rx="4" className="fill-amber-50 stroke-amber-600" />
            <line x1="45" y1="5" x2="45" y2="105" className="stroke-amber-800" strokeWidth="3" />
            <line x1="60" y1="5" x2="60" y2="105" className="stroke-emerald-700" strokeWidth="3" />
            <rect x="35" y="45" width="50" height="40" className="fill-emerald-800/90 stroke-emerald-950" />
          </svg>
        );
      case 'bag-small':
      case 'bag-large':
        return (
          <svg className="w-16 h-16" viewBox="0 0 120 120">
            <path d="M40,40 C40,25 80,25 80,40" fill="none" className="stroke-amber-800" strokeWidth="2" />
            <path d="M35,40 L85,40 L90,105 L30,105 Z" className="fill-amber-50 stroke-amber-700" strokeWidth="2" />
            <circle cx="60" cy="72" r="10" className="fill-emerald-50 stroke-emerald-600" />
            <path d="M57,75 Q60,65 63,72" fill="none" className="stroke-emerald-700" strokeWidth="1.5" />
          </svg>
        );
      case 'bowl':
      case 'bowl-large':
        return (
          <svg className="w-16 h-16" viewBox="0 0 120 120">
            <ellipse cx="60" cy="50" rx="36" ry="10" className="fill-stone-100 stroke-stone-400" />
            <path d="M20,50 C20,90 100,90 100,50 Z" className="fill-amber-50 stroke-amber-700" strokeWidth="2" />
          </svg>
        );
      case 'thermal-cup':
      case 'cup':
        return (
          <svg className="w-16 h-16" viewBox="0 0 120 120">
            <ellipse cx="60" cy="25" rx="20" ry="5" className="fill-stone-200 stroke-stone-400" />
            <path d="M38,25 L46,95 L74,95 L82,25 Z" className="fill-amber-50 stroke-amber-700" strokeWidth="2" />
            <path d="M35,45 L85,45 L80,65 L40,65 Z" className="fill-amber-800 stroke-amber-900" />
          </svg>
        );
      case 'lid':
        return (
          <svg className="w-16 h-16" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="38" className="fill-stone-50 stroke-stone-400" strokeWidth="1.5" />
            <circle cx="60" cy="60" r="28" className="fill-stone-100 stroke-stone-300" />
            <ellipse cx="60" cy="60" rx="10" ry="10" className="fill-none stroke-emerald-500/30" />
          </svg>
        );
      case 'clamshell':
        return (
          <svg className="w-16 h-16" viewBox="0 0 120 120">
            <path d="M40,80 L20,70 L30,45 L70,45 L80,70 L60,80 Z" className="fill-stone-100 stroke-stone-400" strokeWidth="1.5" />
            <rect x="35" y="32" width="50" height="15" rx="1" className="fill-stone-50 stroke-stone-400" />
          </svg>
        );
      case 'tray':
        return (
          <svg className="w-16 h-16" viewBox="0 0 120 120">
            <polygon points="15,45 105,45 95,85 25,85" className="fill-amber-50 stroke-amber-700/80" strokeWidth="2" />
          </svg>
        );
      case 'spoon':
        return (
          <svg className="w-16 h-16" viewBox="0 0 120 120">
            <ellipse cx="60" cy="30" rx="12" ry="18" className="fill-stone-100 stroke-stone-400" />
            <path d="M57,48 L56,95 Q60,100 64,95 L63,48 Z" className="fill-stone-50 stroke-stone-400" />
          </svg>
        );
      default:
        return <HelpCircle className="w-12 h-12 text-stone-300" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Search and category filters */}
      <div className="bg-white rounded-3xl border border-stone-200/50 p-5 shadow-sm space-y-4 print:hidden">
        <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3.5 top-3 w-4 h-4 text-stone-400" />
            <input
              type="text"
              placeholder="Buscar por Clave, nombre de empaque o especificación..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-emerald-500 text-xs text-stone-850"
            />
          </div>
          <div className="flex gap-2 w-full md:w-auto">
            <button
              onClick={handlePrint}
              className="flex-1 md:flex-none h-10 px-4 rounded-xl border border-stone-200 bg-white hover:bg-stone-50 text-stone-700 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
            >
              <Printer className="w-4 h-4 text-emerald-800" />
              Imprimir Documento
            </button>
          </div>
        </div>

        {/* Categories tag bar */}
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-emerald-850 text-white shadow-sm'
                  : 'bg-stone-100 text-stone-600 hover:bg-stone-200/60'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* The Printable Catalog Sheets - DESIGNED EXACTLY LIKE THE SICAR PDF IN SCREENSHOTS */}
      <div className="bg-white border border-stone-200/80 p-8 shadow-md rounded-2xl space-y-6 print:border-none print:shadow-none print:p-0">
        
        {/* Document Header - matching "Catálogo de Artículos XICOPACK" */}
        <div className="text-center pb-5 border-b-2 border-stone-150 relative">
          <h2 className="text-xs uppercase tracking-widest text-emerald-700 font-bold mb-1">Catálogo de Artículos</h2>
          <h1 className="text-sm font-extrabold text-stone-900 tracking-wider">XICOPACK - Empaques Compostables Biodegradables</h1>
          <div className="absolute right-0 bottom-1.5 text-[9px] text-stone-400 font-mono hidden md:block">
            Generado por SICAR • {new Date().toLocaleDateString('es-MX')}
          </div>
        </div>

        {/* Items Rows */}
        {catalogRows.length === 0 ? (
          <div className="py-24 text-center text-stone-400">
            <AlertCircle className="w-12 h-12 mx-auto mb-2 text-stone-300" />
            <p className="text-xs">No se encontraron artículos activos para la búsqueda.</p>
          </div>
        ) : (
          <div className="divide-y divide-stone-150">
            {catalogRows.map((row, idx) => (
              <div 
                key={`${row.sku}-${idx}`} 
                className="py-4 flex flex-col md:flex-row items-center justify-between gap-6 hover:bg-stone-55 transition-colors group px-4 rounded-xl -mx-4"
              >
                {/* Left side details */}
                <div className="flex-1 min-w-0 space-y-2">
                  <h4 className="text-xs font-bold text-stone-850 leading-tight">
                    {row.labelName}
                  </h4>
                  
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-y-2 gap-x-4 text-[11px] text-stone-500 font-sans">
                    <div>
                      <span className="text-[#2f553a] font-medium font-mono text-[10px]">Clave:</span> <span className="font-mono font-bold text-stone-800">{row.sku}</span>
                    </div>
                    <div>
                      <span className="text-[#2f553a] font-medium text-[10px]">Existencia:</span> <span className="font-mono text-stone-700">
                        {typeof row.existence === 'number' ? row.existence.toFixed(4) : row.existence}
                      </span>
                    </div>
                    <div>
                      <span className="text-[#2f553a] font-medium text-[10px]">Departamento:</span> <span className="text-stone-700 font-medium">{row.product.department}</span>
                    </div>
                    <div>
                      <span className="text-[#2f553a] font-medium text-[10px]">Categoría:</span> <span className="text-stone-700">{row.product.category}</span>
                    </div>
                  </div>
                </div>

                {/* Pricing & Image Box */}
                <div className="flex items-center gap-6 self-stretch justify-between md:justify-end">
                  {/* Price */}
                  <div className="text-left md:text-right font-mono">
                    <span className="text-[10px] text-stone-400 uppercase tracking-widest block font-bold leading-none">Precio</span>
                    <span className="text-sm font-extrabold text-stone-900">
                      $ {row.price.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                    <span className="text-[10px] text-emerald-800 bg-emerald-50 px-1.5 py-0.5 rounded ml-1.5 border border-emerald-100/50 font-bold print:hidden">
                      {row.type}
                    </span>
                  </div>

                  {/* Graphic Representation */}
                  <div className="border border-stone-200 bg-stone-50 p-2.5 rounded-xl flex items-center justify-center w-20 h-20 shadow-inner group-hover:bg-white transition-colors overflow-hidden">
                    {row.product.imageUrl ? (
                      <img 
                        src={row.product.imageUrl} 
                        alt={row.product.name} 
                        className="w-full h-full object-contain rounded-lg" 
                        referrerPolicy="no-referrer"
                        onError={(e) => {
                          const currentSrc = e.currentTarget.src;
                          
                          // If it failed with .jpg in fotos_de_sku, try .png
                          if (currentSrc.includes('/fotos_de_sku/') && currentSrc.endsWith('.jpg')) {
                            e.currentTarget.src = currentSrc.replace('.jpg', '.png');
                            return;
                          }
                          // If it failed with .png in fotos_de_sku, try .webp
                          if (currentSrc.includes('/fotos_de_sku/') && currentSrc.endsWith('.png')) {
                            e.currentTarget.src = currentSrc.replace('.png', '.webp');
                            return;
                          }
                          // If it failed in fotos_de_sku completely, try 'fotos' bucket
                          if (currentSrc.includes('/fotos_de_sku/')) {
                            const baseFileWithExt = currentSrc.substring(currentSrc.lastIndexOf('/') + 1);
                            const baseFileNoExt = baseFileWithExt.substring(0, baseFileWithExt.lastIndexOf('.'));
                            e.currentTarget.src = currentSrc.replace(/\/fotos_de_sku\/[^\/]+$/, `/fotos/${baseFileNoExt || baseFileWithExt}.jpg`);
                            return;
                          }
                          // If it failed in 'fotos' with .jpg, try .png
                          if (currentSrc.includes('/fotos/') && currentSrc.endsWith('.jpg')) {
                            e.currentTarget.src = currentSrc.replace('.jpg', '.png');
                            return;
                          }
                          // If it failed in 'fotos' with .png, try .webp
                          if (currentSrc.includes('/fotos/') && currentSrc.endsWith('.png')) {
                            e.currentTarget.src = currentSrc.replace('.png', '.webp');
                            return;
                          }

                          e.currentTarget.style.display = 'none';
                          const sib = e.currentTarget.nextElementSibling as HTMLElement;
                          if (sib) {
                            sib.classList.remove('hidden');
                            sib.classList.add('flex', 'w-full', 'h-full', 'items-center', 'justify-center');
                          }
                        }}
                      />
                    ) : null}
                    <div className={row.product.imageUrl ? 'hidden' : 'w-full h-full flex items-center justify-center'}>
                      {renderProductGraphic(row.product.imageIcon)}
                    </div>
                  </div>

                  {/* Add direct action - print hidden */}
                  <div className="print:hidden">
                    <button
                      onClick={() => handleAddVariant(row)}
                      className={`w-9 h-9 rounded-xl flex items-center justify-center border transition-all ${
                        justAddedSku === row.sku
                          ? 'bg-emerald-600 text-white border-emerald-600 scale-95'
                          : 'bg-white hover:bg-stone-100 text-stone-600 border-stone-200 active:scale-[0.98]'
                      }`}
                      title="Agregar a cotización preliminar"
                    >
                      {justAddedSku === row.sku ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        <ShoppingCart className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

              </div>
            ))}
          </div>
        )}

        {/* Footer replicating catalog pagination */}
        <div className="border-t-2 border-stone-150 pt-4 flex flex-col sm:flex-row justify-between text-[11px] text-stone-400 font-mono gap-2">
          <div>Página 1 / 1</div>
          <div className="text-center sm:text-right">Oficiana Regional de Logística, Todos Santos, B.C.S.</div>
        </div>

      </div>
    </div>
  );
}
