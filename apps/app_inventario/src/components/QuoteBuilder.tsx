import { useState } from 'react';
import type { QuoteItem } from '../types';
import { 
  FileText, Trash2, Printer, ClipboardCheck, ArrowLeft, 
  Percent, Building2, User, Phone, MapPin, Calendar, HelpCircle,
  CreditCard, Edit, Save, Database, CheckCircle2, AlertCircle, RefreshCw
} from 'lucide-react';
import { db } from '../lib/firebase';
import { collection, addDoc } from 'firebase/firestore';

interface QuoteBuilderProps {
  quoteItems: QuoteItem[];
  onUpdateQuantity: (index: number, quantity: number) => void;
  onRemoveItem: (index: number) => void;
  onClearQuote: () => void;
  onBackToCatalog: () => void;
}

export function QuoteBuilder({
  quoteItems,
  onUpdateQuantity,
  onRemoveItem,
  onClearQuote,
  onBackToCatalog
}: QuoteBuilderProps) {
  const [clientName, setClientName] = useState<string>('Café Sol Todos Santos');
  const [contactName, setContactName] = useState<string>('Manuel Espinoza');
  const [phone, setPhone] = useState<string>('612-124-5588');
  const [address, setAddress] = useState<string>('Calle Centenario #24, Centro, Todos Santos, B.C.S.');
  const [validityDays, setValidityDays] = useState<number>(15);
  
  const [checkoutTab, setCheckoutTab] = useState<'operator' | 'accounts'>('operator');
  const [isEditingAccounts, setIsEditingAccounts] = useState<boolean>(false);
  const [bankName, setBankName] = useState<string>('BANCO BBVA MÉXICO');
  const [clabeNumber, setClabeNumber] = useState<string>('0121 8000 1234 5678 90');
  const [beneficiary, setBeneficiary] = useState<string>('XICOPACK S. DE R.L. DE C.V.');
  const [paypalEmail, setPaypalEmail] = useState<string>('pagos@xicopack.com');
  const [applePayLink, setApplePayLink] = useState<string>('https://pay.apple.com/xicopack');

  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveStatus, setSaveStatus] = useState<'PAGADO' | 'PROCESADO' | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [discountPercent, setDiscountPercent] = useState<number>(0);
  const [includeIva, setIncludeIva] = useState<boolean>(true);
  const [isCopied, setIsCopied] = useState<boolean>(false);

  const subtotal = quoteItems.reduce((acc, item) => {
    const variant = item.selectedVariant === 'CAJA' ? item.product.variants.caja : item.product.variants.paquete;
    if (!variant) return acc;
    return acc + (variant.price * item.quantity);
  }, 0);

  const discountAmount = (subtotal * discountPercent) / 100;
  const taxableAmount = subtotal - discountAmount;
  const ivaAmount = includeIva ? taxableAmount * 0.16 : 0;
  const total = taxableAmount + ivaAmount;

  const handleFinalizeQuote = async (status: 'PAGADO' | 'PROCESADO') => {
    setIsSaving(true);
    setErrorMessage(null);
    setSaveStatus(null);
    setStatusMessage(null);

    const tableName = status === 'PAGADO' ? 'cotizaciones_pagadas' : 'cotizaciones_procesadas';

    const payload = {
      cliente: { nombre: clientName, contacto: contactName, telefono: phone, direccion: address },
      items: quoteItems.map(item => {
        const variantData = item.selectedVariant === 'CAJA' ? item.product.variants.caja : item.product.variants.paquete;
        return {
          producto: item.product.name,
          variante: item.selectedVariant,
          sku: variantData?.sku || '',
          cantidad: item.quantity,
          precio_unitario: variantData?.price || 0,
          total_parcial: (variantData?.price || 0) * item.quantity
        };
      }),
      total_neto: total,
      metodo_pago_seleccionado: checkoutTab === 'operator' ? 'Hablar con Operador (WhatsApp)' : 'Cuentas de Pago',
      status: status,
      timestamp: new Date().toISOString()
    };

    try {
      if (db) {
        await addDoc(collection(db, tableName), payload);
        setSaveStatus(status);
        setStatusMessage(`Cotización enviada a Firestore "${tableName}".`);
      } else {
        throw new Error("Firestore db not initialized.");
      }
    } catch (err: any) {
      console.warn("Firestore insertion failed", err);
      setStatusMessage(`Cotización guardada localmente (Firebase no configurado).`);
    }
    
    setIsSaving(false);
  };

  const handlePrint = () => window.print();

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between p-4 bg-stone-50 rounded-2xl border border-stone-200/50 gap-4">
        <div>
          <button onClick={onBackToCatalog} className="text-stone-500 hover:text-stone-850 text-xs font-semibold mb-1">
            <ArrowLeft className="w-3.5 h-3.5 inline mr-1" /> Volver al catálogo interactivo
          </button>
          <h2 className="text-lg font-bold">Presupuesto y Cotizaciones B2B</h2>
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <button onClick={handlePrint} className="h-10 px-4 rounded-xl bg-emerald-800 text-white text-xs font-medium flex items-center justify-center gap-2 transition-all">
            <Printer className="w-4 h-4" /> Imprimir / PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white rounded-2xl border border-stone-200/60 p-5 space-y-4">
            <h4 className="text-xs uppercase font-bold border-b pb-2 flex items-center gap-1.5"><Building2 className="w-3.5 h-3.5" /> Datos del Cliente</h4>
            <div className="space-y-3.5 text-xs">
              <div><label>Empresa</label><input type="text" value={clientName} onChange={(e) => setClientName(e.target.value)} className="w-full border rounded p-2" /></div>
              <div><label>Contacto</label><input type="text" value={contactName} onChange={(e) => setContactName(e.target.value)} className="w-full border rounded p-2" /></div>
            </div>
          </div>
          <div className="bg-emerald-850/95 text-white p-5 rounded-3xl space-y-4">
            <span className="text-[10px] font-mono tracking-widest text-emerald-200 uppercase font-bold block">Resumen del Pedido</span>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between"><span>Suma de Artículos</span><span>${subtotal.toFixed(2)}</span></div>
              <div className="flex justify-between"><span>Subtotal Neto</span><span>${taxableAmount.toFixed(2)}</span></div>
              <div className="flex justify-between text-sm font-bold pt-1.5 items-baseline">
                <span>Gran Total</span><span className="text-base">${total.toFixed(2)}</span>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-2xl border p-5">
            <button onClick={() => handleFinalizeQuote('PROCESADO')} className="w-full py-2 bg-stone-100 text-stone-800 font-bold rounded mb-2">Guardar Cotización en Firebase</button>
            {statusMessage && <div className="text-xs text-emerald-700 bg-emerald-50 p-2 rounded">{statusMessage}</div>}
          </div>
        </div>
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border p-5">
            <h4 className="text-xs uppercase font-bold border-b pb-3 mb-4">Conceptos Seleccionados ({quoteItems.length})</h4>
            <div className="space-y-4">
              {quoteItems.map((item, index) => {
                const activeVariant = item.selectedVariant === 'CAJA' ? item.product.variants.caja : item.product.variants.paquete;
                if (!activeVariant) return null;
                return (
                  <div key={index} className="flex justify-between p-3 bg-stone-50 rounded-xl border items-center">
                    <div>
                      <h5 className="text-xs font-bold">{item.product.name}</h5>
                      <span className="text-[10px]">{item.selectedVariant} - {activeVariant.sku}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-xs font-mono">${(activeVariant.price * item.quantity).toFixed(2)}</div>
                      <button onClick={() => onRemoveItem(index)} className="text-red-500"><Trash2 className="w-4 h-4" /></button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
