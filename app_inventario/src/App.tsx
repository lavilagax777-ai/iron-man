import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Product, QuoteItem } from './types';
import { PRODUCTS, CATEGORIES } from './data';
import { ProductCard } from './components/ProductCard';
import { CatalogDoc } from './components/CatalogDoc';
import { QuoteBuilder } from './components/QuoteBuilder';
import { PresentationView } from './components/PresentationView';
import { 
  Leaf, Search, FileText, ClipboardList, PackageCheck, 
  HelpCircle, Sparkles, SlidersHorizontal, Layers, Check, ShoppingBag, Eye, QrCode, CheckCircle2,
  Presentation
} from 'lucide-react';

import { db, mapFirestoreProduct, bulkUploadProductsToFirestore } from './lib/firebase';
import { collection, onSnapshot } from 'firebase/firestore';

export default function App() {
  const [activeTab, setActiveTab] = useState<'interactive' | 'document' | 'presentation' | 'quote'>('interactive');
  const [quoteItems, setQuoteItems] = useState<QuoteItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Todos');
  const [scannedMessage, setScannedMessage] = useState<{
    sku: string;
    product: Product;
    variantType: 'CAJA' | 'PAQUETE';
    price: number;
    quantityLabel: string;
  } | null>(null);

  // Dynamic Product list loaded from Firestore or falling back to local seed data
  const [productsList, setProductsList] = useState<Product[]>(PRODUCTS);
  const [isDbLoading, setIsDbLoading] = useState<boolean>(false);
  const [isDbConnected, setIsDbConnected] = useState<boolean>(false);
  const [dbStatusDetails, setDbStatusDetails] = useState<string>('Conectando a Google Cloud Firestore...');
  
  // Real-time Database Diagnostics
  const [dbDebugInfo, setDbDebugInfo] = useState<{
    tableName: string;
    totalCount: number;
    columns: string[];
    sampleRows: any[];
    error: string | null;
  } | null>(null);
  const [isConsoleOpen, setIsConsoleOpen] = useState<boolean>(false);
  const [consoleTab, setConsoleTab] = useState<'photos' | 'import'>('import');
  
  // Bulk upload paste state
  const [csvRawText, setCsvRawText] = useState<string>('');
  const [importStatus, setImportStatus] = useState<{ status: 'idle' | 'loading' | 'success' | 'failed'; message: string }>({ status: 'idle', message: '' });

  useEffect(() => {
    setIsDbLoading(true);
    let unsubscribe: (() => void) | null = null;

    try {
      const pathForOnSnapshot = 'productos';
      unsubscribe = onSnapshot(
        collection(db, pathForOnSnapshot),
        (snapshot) => {
          setIsDbLoading(false);
          if (!snapshot.empty) {
            const fetched = snapshot.docs.map((d) => mapFirestoreProduct(d.id, d.data()));
            setProductsList(fetched);
            setIsDbConnected(true);

            const rawDocs = snapshot.docs.map((docVal) => ({ id: docVal.id, ...docVal.data() }));
            const columns = rawDocs.length > 0 ? Object.keys(rawDocs[0]) : [];

            setDbDebugInfo({
              tableName: 'productos',
              totalCount: snapshot.size,
              columns,
              sampleRows: rawDocs.slice(0, 10),
              error: null
            });
            setDbStatusDetails(`¡Conexión Firestore activa! Colección: "productos" (${snapshot.size} elementos en sincronización en tiempo real).`);
          } else {
            setProductsList(PRODUCTS);
            setIsDbConnected(true);
            setDbDebugInfo({
              tableName: 'productos',
              totalCount: 0,
              columns: [],
              sampleRows: [],
              error: 'Colección "productos" vacía en Cloud Firestore'
            });
            setDbStatusDetails('Firestore conectado, pero la colección "productos" no posee documentos. Cargando catálogo semilla.');
          }
        },
        (error) => {
          setIsDbLoading(false);
          setIsDbConnected(false);
          console.error('Firestore connection error:', error);
          setDbStatusDetails('Usando catálogo local de contingencia (Firestore sin permisos o sin configurar)');
          setDbDebugInfo({
            tableName: 'productos',
            totalCount: 0,
            columns: [],
            sampleRows: [],
            error: error.message
          });
        }
      );
    } catch (err: any) {
      setIsDbLoading(false);
      setIsDbConnected(false);
      setDbStatusDetails('Error al iniciar listener de Firestore (Catálogo local activo)');
      setDbDebugInfo({
        tableName: 'productos',
        totalCount: 0,
        columns: [],
        sampleRows: [],
        error: err?.message || String(err)
      });
    }

    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, []);

  const handleBulkImportCSV = async () => {
    if (!csvRawText.trim()) {
      setImportStatus({ status: 'failed', message: 'Por favor pega texto CSV o JSON válido.' });
      return;
    }

    setImportStatus({ status: 'loading', message: 'Analizando y subiendo registros en lotes a Firestore...' });

    try {
      let itemsToUpload: any[] = [];
      const trimmed = csvRawText.trim();
      
      if ((trimmed.startsWith('[') && trimmed.endsWith(']')) || (trimmed.startsWith('{') && trimmed.endsWith('}'))) {
        try {
          const parsed = JSON.parse(trimmed);
          itemsToUpload = Array.isArray(parsed) ? parsed : [parsed];
        } catch (e) {
          throw new Error('Formato JSON inválido.');
        }
      } else {
        const lines = trimmed.split('\n').filter(l => l.trim() !== '');
        if (lines.length < 2) {
          throw new Error('Formato CSV de importación inválido. Falta fila de encabezados o datos.');
        }

        const headerLine = lines[0];
        let delimiter = ',';
        if (headerLine.includes(';')) delimiter = ';';
        else if (headerLine.includes('\t')) delimiter = '\t';

        const headers = headerLine.split(delimiter).map(h => h.trim().replace(/^["']|["']$/g, ''));
        
        for (let i = 1; i < lines.length; i++) {
          const currentLine = lines[i];
          let cells: string[] = [];
          if (delimiter === ',') {
            const matches = currentLine.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || currentLine.split(',');
            cells = matches.map(c => c.trim().replace(/^["']|["']$/g, ''));
          } else {
            cells = currentLine.split(delimiter).map(c => c.trim().replace(/^["']|["']$/g, ''));
          }

          if (cells.length > 0) {
            const obj: any = {};
            headers.forEach((header, index) => {
              obj[header] = cells[index] || '';
            });
            itemsToUpload.push(obj);
          }
        }
      }

      if (itemsToUpload.length === 0) {
        throw new Error('No se encontraron registros de productos válidos.');
      }

      const result = await bulkUploadProductsToFirestore(itemsToUpload);
      setImportStatus({
        status: 'success',
        message: `¡Carga exitosa! Se subieron ${result.success} productos a Firestore. ${result.failed > 0 ? `Fallaron ${result.failed} registros debido a límites de formato.` : ''}`
      });
      setCsvRawText('');
    } catch (err: any) {
      setImportStatus({ status: 'failed', message: err?.message || 'Error inesperado al importar.' });
    }
  };

  const handleScanSku = (sku: string) => {
    if (!sku) return;
    const cleanSku = sku.trim().toUpperCase();
    
    const foundProduct = productsList.find(p => 
      (p.variants.caja && p.variants.caja.sku.toUpperCase() === cleanSku) ||
      (p.variants.paquete && p.variants.paquete.sku.toUpperCase() === cleanSku)
    );

    if (foundProduct) {
      const isCaja = foundProduct.variants.caja?.sku.toUpperCase() === cleanSku;
      const variant = isCaja ? foundProduct.variants.caja : foundProduct.variants.paquete;
      
      if (variant) {
        setSearchTerm(cleanSku);
        setSelectedCategory('Todos');
        setActiveTab('interactive');
        setScannedMessage({
          sku: cleanSku,
          product: foundProduct,
          variantType: isCaja ? 'CAJA' : 'PAQUETE',
          price: variant.price,
          quantityLabel: variant.quantityLabel
        });

        setTimeout(() => {
          const searchInput = document.querySelector('input[placeholder*="Buscar por Clave"]');
          if (searchInput) {
            searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 150);
      }
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const skuParam = params.get('sku');
    if (skuParam) {
      handleScanSku(skuParam);
      const cleanUrl = window.location.origin + window.location.pathname;
      window.history.replaceState({}, '', cleanUrl);
    }
  }, []);

  const handleAddToQuote = (item: QuoteItem) => {
    setQuoteItems(prev => {
      const existingIdx = prev.findIndex(
        i => i.product.id === item.product.id && i.selectedVariant === item.selectedVariant
      );
      if (existingIdx > -1) {
        const copy = [...prev];
        copy[existingIdx].quantity += item.quantity;
        return copy;
      }
      return [...prev, item];
    });
  };

  const handleAddDirectVariant = (product: Product, variantType: 'CAJA' | 'PAQUETE') => {
    handleAddToQuote({
      product,
      selectedVariant: variantType,
      quantity: 1
    });
  };

  const handleUpdateQuantity = (index: number, quantity: number) => {
    if (quantity <= 0) {
      handleRemoveItem(index);
      return;
    }
    setQuoteItems(prev => {
      const copy = [...prev];
      copy[index].quantity = quantity;
      return copy;
    });
  };

  const handleRemoveItem = (index: number) => {
    setQuoteItems(prev => prev.filter((_, idx) => idx !== index));
  };

  const handleClearQuote = () => {
    setQuoteItems([]);
  };

  const filteredProducts = productsList.filter(prod => {
    const matchesSearch = prod.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          prod.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          prod.variants.caja?.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          prod.variants.paquete?.sku.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'Todos' || prod.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-[#faf9f6] text-stone-800 antialiased font-sans flex flex-col">
      
      <div className="bg-emerald-900 text-stone-100 py-1.5 px-4 text-center text-[10px] font-mono tracking-widest font-semibold uppercase flex items-center justify-center gap-1.5 border-b border-emerald-950 print:hidden">
        <Sparkles className="w-3 h-3 text-emerald-300 animate-pulse" />
        Suministro Preferente HORECA & Boutiques • Todos Santos • Entrega Segura
      </div>

      <header className="bg-white border-b border-stone-200/60 sticky top-0 z-30 shadow-sm print:hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
          
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-50 rounded-2xl flex items-center justify-center text-emerald-800 border-2 border-emerald-100">
              <Leaf className="w-5 h-5 fill-emerald-100" />
            </div>
            <div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-lg font-black tracking-tight text-stone-900 uppercase">Xicopack</span>
                <span className="text-[9px] font-bold py-0.5 px-1.5 bg-emerald-100 text-emerald-800 rounded uppercase font-mono tracking-wider border border-emerald-200">B2B</span>
              </div>
              <p className="text-[10px] text-stone-400 font-medium">Empaques Compostables Biodegradables</p>
            </div>
          </div>

          <nav className="flex bg-stone-100 p-1 rounded-xl border border-stone-200/50 gap-0.5 w-full md:w-auto">
            <button
              onClick={() => setActiveTab('interactive')}
              className={`flex-1 md:flex-none px-4 py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                activeTab === 'interactive'
                  ? 'bg-white text-stone-900 shadow-sm'
                  : 'text-stone-500 hover:text-stone-850 hover:bg-stone-50'
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              Catálogo Interactivo
            </button>
            <button
              onClick={() => setActiveTab('document')}
              className={`flex-1 md:flex-none px-4 py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                activeTab === 'document'
                  ? 'bg-white text-stone-900 shadow-sm'
                  : 'text-stone-500 hover:text-stone-850 hover:bg-stone-50'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              Vista de Listado (PDF)
            </button>
            <button
              onClick={() => setActiveTab('presentation')}
              className={`flex-1 md:flex-none px-4 py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                activeTab === 'presentation'
                  ? 'bg-white text-stone-900 shadow-sm'
                  : 'text-stone-500 hover:text-stone-850 hover:bg-stone-50'
              }`}
            >
              <Presentation className="w-3.5 h-3.5" />
              Presentación Distribuidor
            </button>
            <button
              onClick={() => setActiveTab('quote')}
              className={`flex-1 md:flex-none px-4 py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 relative transition-all ${
                activeTab === 'quote'
                  ? 'bg-white text-stone-900 shadow-sm'
                  : 'text-stone-500 hover:text-stone-850 hover:bg-stone-50'
              }`}
            >
              <ClipboardList className="w-3.5 h-3.5" />
              Presupuesto
              {quoteItems.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-emerald-700 text-white font-mono text-[9px] font-bold w-4 h-4 rounded-full flex items-center justify-center border border-white animate-bounce-short">
                  {quoteItems.length}
                </span>
              )}
            </button>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">

        <AnimatePresence>
          {scannedMessage && (
            <motion.div
              initial={{ opacity: 0, y: -25, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, y: -25, height: 0 }}
              className="bg-emerald-900 text-white rounded-3xl border border-emerald-950 p-5 shadow-xl mb-6 flex flex-col md:flex-row items-center justify-between gap-4 relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-800/20 via-transparent to-emerald-800/20 pointer-events-none" />
              
              <div className="flex items-center gap-4 relative z-10">
                <div className="w-12 h-12 bg-white/10 rounded-2xl flex items-center justify-center text-emerald-300 font-bold border border-white/20 select-none animate-pulse shrink-0">
                  <QrCode className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] font-mono bg-emerald-700 px-2 py-0.5 rounded text-emerald-100 font-extrabold uppercase tracking-widest border border-emerald-600/50">
                      Escaneo de Góndola Exitoso
                    </span>
                    <span className="text-xs font-mono text-emerald-300 font-bold">SKU: {scannedMessage.sku}</span>
                  </div>
                  <h4 className="text-sm font-bold text-white mt-1 leading-snug">
                    {scannedMessage.product.name} — <span className="font-semibold text-emerald-200">{scannedMessage.variantType === 'CAJA' ? 'Caja' : 'Paquete'}</span> ({scannedMessage.quantityLabel})
                  </h4>
                  <p className="text-[11px] text-emerald-100/85 font-sans">
                    Se ha filtrado la lista para mostrar este producto. Precio B2B: <span className="font-mono font-bold">${scannedMessage.price.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</span>
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 relative z-10 w-full md:w-auto shrink-0 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    handleAddToQuote({
                      product: scannedMessage.product,
                      selectedVariant: scannedMessage.variantType,
                      quantity: 1
                    });
                    setSearchTerm('');
                    setScannedMessage(null);
                  }}
                  className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-emerald-950 rounded-xl text-xs font-bold transition-all shadow-md hover:shadow-lg active:scale-95 cursor-pointer flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4 text-emerald-950" />
                  Agregar 1 a la Cotización
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setSearchTerm('');
                    setScannedMessage(null);
                  }}
                  className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-medium transition-colors cursor-pointer"
                >
                  Limpiar Filtro
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <div className="hidden print:block mb-8">
          <div className="flex justify-between items-center border-b-2 border-stone-150 pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-emerald-850">XICOPACK</h1>
              <p className="text-xs font-mono uppercase tracking-widest text-[#2f553a]">Empaques Compostables Biodegradables</p>
            </div>
            <div className="text-right text-xs text-stone-400">
              <p>Suministro Integral de Vajilla Natural</p>
              <p className="font-mono">Fecha de Impresión: {new Date().toLocaleDateString('es-MX')}</p>
            </div>
          </div>
        </div>

        <AnimatePresence mode="wait">
          
          {activeTab === 'interactive' && (
            <motion.div
              key="interactive"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.2 }}
              className="space-y-6 print:hidden"
            >
              <div className="bg-white rounded-3xl border border-stone-200/50 p-6 shadow-sm space-y-4">
                <div className="flex flex-col md:flex-row gap-4 items-center">
                  
                  <div className="relative flex-1 w-full">
                    <Search className="absolute left-3.5 top-3 w-4 h-4 text-stone-400" />
                    <input
                      type="text"
                      placeholder="Buscar por Clave, nombre de empaque, material, categoría..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-stone-200 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-emerald-500 text-xs text-stone-850"
                    />
                  </div>

                  <div className="text-xs text-stone-400 md:text-right w-full md:w-auto font-mono">
                    Mostrando <span className="font-bold text-stone-700">{filteredProducts.length}</span> de <span className="font-bold text-stone-700">{productsList.length}</span> empaques
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-3 px-4.5 rounded-2xl bg-stone-50 border border-stone-200/60 text-[10.5px] font-mono select-none">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full shrink-0 ${isDbConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'}`} />
                      <span className="font-extrabold uppercase tracking-widest text-[#2f553a]">Canal Firebase Firestore:</span>
                      <span className={`font-semibold ${isDbConnected ? 'text-emerald-800' : 'text-stone-500'}`}>
                        {dbStatusDetails}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 self-stretch sm:self-auto justify-between sm:justify-start">
                      {isDbLoading && (
                        <span className="text-[10px] text-stone-450 flex items-center gap-1.5 font-mono">
                          <span className="w-3 h-3 border-2 border-stone-300 border-t-emerald-700 rounded-full animate-spin" />
                          sincronizando...
                        </span>
                      )}
                      <button
                        type="button"
                        onClick={() => setIsConsoleOpen(!isConsoleOpen)}
                        className="px-2.5 py-1 bg-amber-50 text-amber-800 hover:bg-amber-100/80 border border-amber-200 rounded-lg text-[10px] font-extrabold uppercase tracking-wider transition-colors cursor-pointer"
                      >
                        {isConsoleOpen ? 'Ocultar Canales ✕' : 'Consola Diagnóstica y Cargar Catálogo ⚙️'}
                      </button>
                    </div>
                  </div>

                  {isConsoleOpen && dbDebugInfo && (
                    <div className="p-4 rounded-2xl bg-stone-900 text-stone-200 border border-stone-850 space-y-4 font-mono text-[11px] leading-relaxed shadow-lg">
                      
                      <div className="flex border-b border-stone-800 pb-2 gap-2 select-none">
                        <button
                          type="button"
                          onClick={() => setConsoleTab('import')}
                          className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer ${consoleTab === 'import' ? 'bg-emerald-600 text-white shadow' : 'bg-stone-800 text-stone-300 hover:bg-stone-750'}`}
                        >
                          📥 Cargar Catálogo de Productos (CSV / Excel)
                        </button>
                        <button
                          type="button"
                          onClick={() => setConsoleTab('photos')}
                          className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer ${consoleTab === 'photos' ? 'bg-amber-500 text-black shadow' : 'bg-stone-800 text-stone-300 hover:bg-stone-750'}`}
                        >
                          📊 Estadísticas y JSON de Firestore
                        </button>
                      </div>

                      {consoleTab === 'import' && (
                        <div className="space-y-3">
                          <div className="p-3 bg-stone-950 border border-stone-850 rounded-xl space-y-2 leading-relaxed">
                            <span className="text-[10px] text-emerald-400 font-extrabold uppercase tracking-widest block">💡 IMPORTACIÓN MASIVA EN SEGUNDOS - CARGA TUS 700+ PRODUCTOS</span>
                            <p className="text-[10px] text-stone-300 leading-normal">
                              El archivo local <span className="text-zinc-400 font-bold">src/data.ts</span> solo contiene los <span className="text-emerald-300 font-bold">19 productos semilla de prueba</span>. Al conectar tu Firebase Firestore, todos los registros se sincronizan en tiempo real al instante.
                            </p>
                            <p className="text-[10px] text-emerald-300 leading-normal">
                              Puedes pegar un listado en formato <span className="text-white font-bold">CSV</span> (del software SICAR o Excel) o una lista de objetos <span className="text-white font-bold">JSON</span> aquí abajo y presionar el cargador de alta velocidad. ¡Los productos se enviarán en lotes transaccionados directamente a Firestore!
                            </p>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-3 bg-stone-950/40 p-3 rounded-xl border border-stone-850 flex flex-col justify-between">
                              <div>
                                <span className="text-[10px] text-amber-400 font-extrabold uppercase tracking-widest block border-b border-stone-800 pb-1 mb-1.5">⚡ INSTRUCCIONES DE IMPORTACIÓN</span>
                                <ol className="list-decimal list-inside space-y-1 text-[10px] text-stone-300 leading-normal">
                                  <li>Exporta tu catálogo a formato <span className="text-amber-300">CSV</span> o cópialo de una hoja Excel.</li>
                                  <li>Usa cabeceras descriptivas: <span className="text-emerald-400">id, name, category, department, description, sku_caja, precio_caja, label_caja, existencia_caja, sku_paquete, precio_paquete, label_paquete, existencia_paquete, image_url</span>.</li>
                                  <li>Pega el texto abajo y haz clic en "Cargar Catálogo masivo". ¡Se sube directo a Firestore!</li>
                                </ol>
                              </div>
                              <div className="pt-2">
                                <span className="text-[10px] text-emerald-400 font-bold uppercase block mb-1">Pega tus filas CSV / JSON:</span>
                                <textarea
                                  value={csvRawText}
                                  onChange={(e) => setCsvRawText(e.target.value)}
                                  placeholder="id,name,category,department,sku_caja,precio_caja,sku_paquete,precio_paquete&#10;75010020,Vaso Compostable 8oz,Vasos,AGAVE,vaso8c,1540.00,vaso8p,110.00"
                                  className="w-full h-24 bg-stone-950 text-stone-200 text-[9px] p-2 rounded border border-stone-800 font-mono focus:outline-none focus:border-emerald-500"
                                />
                                <div className="mt-2 flex items-center justify-between gap-2">
                                  <button
                                    type="button"
                                    onClick={handleBulkImportCSV}
                                    style={{ contentVisibility: 'auto' }}
                                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-650 text-white font-bold rounded-lg text-[9.5px] uppercase transition-all cursor-pointer"
                                  >
                                    Cargar Catálogo masivo a Firestore 🚀
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => {
                                      setCsvRawText(`id,name,category,department,description,sku_caja,precio_caja,label_caja,existencia_caja,sku_paquete,precio_paquete,label_paquete,existencia_paquete
XP-800,Contenedor Bio Bisagra Grande,Contenedores,FÉCULA DE MAÍZ,Biodegradable premium para alimentos impermeables 9x9,bis-gde,1950.00,CAJA 200 Pzas,20,bis-gde-p,540.00,PQTE 50 Pzas,95
XP-910,Charola Redonda Fibra Caña,Platos y Charolas,CAÑA DE AZÚCAR,Charola ecológica de caña resistente de alta presión,ch-red,1240.00,CAJA 500 Pzas,42,ch-red-p,145.00,PQTE 50 Pzas,12
XP-104,Popote Agave Recto Negro,Accesorios,AGAVE,Popote estuchado biodegradable fabricado con residuos agave,pop-neg,650.00,CAJA 1000 Pzas,110,pop-neg-p,45.00,PQTE 50 Pzas,N/A`);
                                    }}
                                    className="px-2 py-1 bg-stone-800 hover:bg-stone-750 text-stone-400 rounded-lg text-[9px] cursor-pointer"
                                  >
                                    Pegar Ejemplo 📝
                                  </button>
                                </div>
                                {importStatus.message && (
                                  <div className={`mt-2 p-1.5 rounded text-[8.5px] font-bold ${importStatus.status === 'success' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : importStatus.status === 'failed' ? 'bg-red-950 text-red-300 border border-red-900' : 'bg-stone-950 text-amber-300 animate-pulse border border-stone-800'}`}>
                                    {importStatus.message}
                                  </div>
                                )}
                              </div>
                            </div>

                            <div className="space-y-2 bg-stone-950/40 p-3 rounded-xl border border-stone-850 flex flex-col justify-between">
                              <div>
                                <span className="text-[10px] text-emerald-400 font-extrabold uppercase tracking-widest block border-b border-stone-800 pb-1 mb-1.5">📋 FORMATO REQUERIDO DE LAS COLUMNAS</span>
                                <p className="text-[10px] text-stone-300 leading-normal mb-2">Para una sincronización perfecta, tus columnas en Excel o CSV deben llamarse igual a éstas:</p>
                                <div className="space-y-1.5 text-[9.5px]">
                                  <div><span className="text-emerald-400 font-bold">id / clave:</span> Código único del producto (ej: XP-800)</div>
                                  <div><span className="text-emerald-400 font-bold">name / nombre:</span> Nombre comercial corto del producto</div>
                                  <div><span className="text-emerald-300 font-bold">category:</span> Categoría filtrable (Contenedores, Vasos, Platos, etc.)</div>
                                  <div><span className="text-emerald-300 font-bold">department:</span> Bio-materia prima (AGAVE, CAÑA DE AZÚCAR, BAMBÚ, etc.)</div>
                                  <div><span className="text-amber-200">precio_caja:</span> Valor decimal o entero para el precio por Caja</div>
                                  <div><span className="text-amber-200">precio_paquete:</span> Valor decimal o entero para el precio por Paquete</div>
                                </div>
                              </div>
                              <div className="p-2 bg-stone-950 rounded border border-stone-800 text-[8.5px] text-stone-450 mt-1 lines-clamp-3">
                                <span className="text-stone-300 font-bold">Tip:</span> Firebase Firestore acepta inserciones masivas transaccionadas de hasta 500 operaciones por lote. El sistema divide automáticamente el archivo en lotes seguros.
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {consoleTab === 'photos' && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <div className="text-emerald-400 font-bold uppercase text-[10px] tracking-widest border-b border-stone-800 pb-1 flex justify-between items-center">
                              <span>📊 Estadísticas de la Colección</span>
                              <span className="bg-emerald-950 text-emerald-300 px-1.5 py-0.5 rounded text-[9px] uppercase">Firestore Activo</span>
                            </div>
                            <div><span className="text-stone-450">Colección Detectada:</span> <span className="text-white font-bold">{dbDebugInfo.tableName}</span></div>
                            <div><span className="text-stone-450">Registros Totales:</span> <span className="text-white font-bold">{dbDebugInfo.totalCount} productos</span></div>
                            <div>
                              <span className="text-stone-450">Estructura de Campo de Documentos (Campos Encontrados):</span>{' '}
                              <div className="text-[10px] text-stone-300 max-h-20 overflow-y-auto bg-stone-950 p-2 rounded border border-stone-800 mt-1 select-all">
                                {dbDebugInfo.columns.length > 0 ? dbDebugInfo.columns.join(' | ') : 'Sin campos detectados en documentos.'}
                              </div>
                            </div>
                          </div>

                          <div className="space-y-2">
                            <div className="text-amber-400 font-bold uppercase text-[10px] tracking-widest border-b border-stone-800 pb-1">
                              <span>🛡️ Reglas y Seguridad de Firestore</span>
                            </div>
                            <p className="text-[10.5px] text-stone-300 leading-normal">
                              La base de datos cuenta con políticas de seguridad de <span className="text-white font-bold">firestore.rules</span> activadas y desplegadas:
                            </p>
                            <ul className="list-disc list-inside space-y-1 text-[10px] text-stone-400">
                              <li>Operaciones de lectura <span className="text-emerald-400">allow get, list</span> abiertas para visitantes públicos.</li>
                              <li>Operaciones de escritura <span className="text-amber-300">allow create, update, delete</span> restringidas a usuarios autenticados.</li>
                              <li>Validación estricta de límites de caracteres, tipos numéricos y claves obligatorias.</li>
                            </ul>
                            <div className="p-2 bg-stone-950 rounded border border-stone-850 text-[8.5px] text-stone-450 leading-relaxed font-mono">
                              Project ID: <span className="text-stone-300">gen-lang-client-0471881450</span><br />
                              Mode: Firebase Enterprise (Firestore Single-instance)
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="bg-stone-950 p-2.5 rounded border border-stone-850 mt-2 space-y-2">
                        <div className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest">
                          🔍 Primeras Filas Detectadas en Firestore Real-Time
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px]">
                          {productsList.slice(0, 4).map((p, idx) => {
                            const sampleRaw = dbDebugInfo.sampleRows[idx] || {};
                            return (
                              <div key={p.id} className="p-2 rounded bg-stone-900 border border-stone-800 flex gap-2 items-start">
                                {p.imageUrl && (
                                  <div className="w-9 h-9 bg-stone-800 rounded shrink-0 flex items-center justify-center overflow-hidden border border-stone-700">
                                    <img 
                                      src={p.imageUrl} 
                                      alt={p.name} 
                                      className="w-full h-full object-contain"
                                      referrerPolicy="no-referrer"
                                      onError={(e) => {
                                        e.currentTarget.style.display = 'none';
                                        const parentNode = e.currentTarget.parentNode;
                                        if (parentNode) {
                                          const replacementNode = document.createElement('span');
                                          replacementNode.innerText = '📦';
                                          replacementNode.className = 'text-[9px] flex items-center justify-center pt-2';
                                          parentNode.appendChild(replacementNode);
                                        }
                                      }}
                                    />
                                  </div>
                                )}
                                <div className="min-w-0 flex-1 leading-normal">
                                  <div className="truncate text-white font-bold">{p.name}</div>
                                  <div className="text-stone-450 truncate">Id: <span className="text-stone-300">{p.id}</span> | SKU Caja: <span className="text-amber-200">{p.variants.caja?.sku || 'N/A'}</span></div>
                                  <div className="text-emerald-400 truncate text-[9px] select-all mt-0.5" title={p.imageUrl}>
                                    URL: {p.imageUrl ? p.imageUrl.substring(0, 50) + '...' : 'Usando Icono Predeterminado'}
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        <div className="text-[9.5px] text-stone-400 leading-normal border-t border-stone-850 pt-1.5">
                          💡 <span className="text-amber-300">¿Cómo se resuelven las imágenes?</span> Si tus productos de Firestore contienen URLs de imágenes públicas (p. ej. de tu hosting o Google Drive público) en la columna <span className="text-stone-300 font-bold">image_url</span>, el sistema las mostrará automáticamente aquí y en las tarjetas del catálogo. Si no poseen imagen, se usará un elegante icono acorde a la materia prima.
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex justify-between items-center gap-4 flex-wrap pt-1">
                  <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none flex-1">
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

                  <div className="h-px bg-stone-200 w-full md:hidden" />

                  <div className="flex gap-1.5 items-center bg-stone-50 border border-stone-200 p-1.5 rounded-xl w-full md:w-auto shadow-sm">
                    <div className="flex items-center gap-1.5 px-2 text-[10px] font-extrabold text-stone-500 uppercase tracking-wider">
                      <QrCode className="w-3.5 h-3.5 text-[#2f553a] animate-pulse" />
                      <span>Escaner Láser B2B:</span>
                    </div>
                    <select
                      id="sku-scanner-select"
                      className="bg-white border border-stone-200 rounded-lg px-2 py-1 text-[11px] font-mono font-medium text-stone-700 outline-none focus:ring-1 focus:ring-emerald-500 max-w-[140px] md:max-w-[200px]"
                    >
                      <option value="">-- Elige un SKU --</option>
                      {productsList.flatMap(p => [
                        p.variants.caja ? { sku: p.variants.caja.sku, name: `${p.name.substring(0, 20)}... (Caja)` } : null,
                        p.variants.paquete ? { sku: p.variants.paquete.sku, name: `${p.name.substring(0, 20)}... (Paquete)` } : null,
                      ]).filter(Boolean).map(item => (
                        <option key={item!.sku} value={item!.sku}>{item!.sku} - {item!.name}</option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => {
                        const sel = document.getElementById('sku-scanner-select') as HTMLSelectElement;
                        if (sel && sel.value) {
                          handleScanSku(sel.value);
                        }
                      }}
                      className="px-3 py-1 bg-emerald-800 hover:bg-emerald-850 text-white rounded-lg text-[10px] font-bold transition-all cursor-pointer flex items-center gap-1 active:scale-95"
                    >
                      Disparar Láser ☄️
                    </button>
                  </div>
                </div>
              </div>

              {filteredProducts.length === 0 ? (
                <div className="bg-white rounded-3xl border border-stone-25 px-8 py-20 text-center max-w-sm mx-auto space-y-3">
                  <div className="w-12 h-12 bg-stone-100 rounded-full flex items-center justify-center mx-auto text-stone-400">
                    <Search className="w-6 h-6" />
                  </div>
                  <h4 className="text-sm font-bold text-stone-800">No se encontraron productos</h4>
                  <p className="text-xs text-stone-500 leading-relaxed">Prueba con otros términos de búsqueda o cambia la categoría de filtro.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {filteredProducts.map(product => (
                    <ProductCard
                      key={product.id}
                      product={product}
                      onAddToQuote={handleAddToQuote}
                      onScanSku={handleScanSku}
                    />
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'document' && (
            <motion.div
              key="document"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              <CatalogDoc onAddDirectVariant={handleAddDirectVariant} products={productsList} />
            </motion.div>
          )}

          {activeTab === 'presentation' && (
            <motion.div
              key="presentation"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              <PresentationView products={productsList} />
            </motion.div>
          )}

          {activeTab === 'quote' && (
            <motion.div
              key="quote"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              <QuoteBuilder
                quoteItems={quoteItems}
                onUpdateQuantity={handleUpdateQuantity}
                onRemoveItem={handleRemoveItem}
                onClearQuote={handleClearQuote}
                onBackToCatalog={() => setActiveTab('interactive')}
              />
            </motion.div>
          )}

        </AnimatePresence>
      </main>

      <footer className="bg-white border-t border-stone-200 py-8 mt-12 print:hidden select-none">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-stone-400">
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-stone-600 tracking-tight">XICOPACK</span>
            <span>•</span>
            <span>Todos los derechos reservados © 2026.</span>
          </div>

          <div className="flex gap-4">
            <span className="font-medium text-stone-500">Diseño Sustentable</span>
            <span className="text-stone-300">|</span>
            <span className="font-medium text-stone-500">100% Biodegradable</span>
            <span className="text-stone-300">|</span>
            <span className="font-medium text-stone-500 font-mono text-[10px]">SICAR Direct Integration</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
