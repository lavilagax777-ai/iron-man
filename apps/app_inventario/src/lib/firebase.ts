import { initializeApp } from 'firebase/app';
import { getFirestore, doc, setDoc, writeBatch } from 'firebase/firestore';

// IMPORTANTE: Asegúrate de reemplazar esto con tu configuración real de Firebase Spark Plan
const firebaseConfig = {
  apiKey: "TU_API_KEY",
  authDomain: "tu-proyecto.firebaseapp.com",
  projectId: "tu-proyecto",
  storageBucket: "tu-proyecto.appspot.com",
  messagingSenderId: "TUS_DATOS",
  appId: "TUS_DATOS"
};

let app;
let dbInstance: any = null;

try {
  app = initializeApp(firebaseConfig);
  dbInstance = getFirestore(app);
} catch (error) {
  console.warn("Firebase config is missing or invalid. Funciona en modo local.");
}

export const db = dbInstance;

export function mapFirestoreProduct(id: string, data: any) {
  return {
    id,
    name: data.name || data.nombre || 'Producto sin nombre',
    description: data.description || data.descripcion || '',
    category: data.category || data.categoria || 'Sin Categoría',
    department: data.department || data.departamento || 'General',
    imageIcon: data.imageIcon || 'box',
    imageUrl: data.image_url || data.imageUrl || '',
    variants: {
      ...(data.sku_caja ? { caja: { sku: data.sku_caja, price: Number(data.precio_caja), quantityLabel: data.label_caja || 'CAJA', existence: data.existencia_caja || 0 } } : {}),
      ...(data.sku_paquete ? { paquete: { sku: data.sku_paquete, price: Number(data.precio_paquete), quantityLabel: data.label_paquete || 'PQTE', existence: data.existencia_paquete || 0 } } : {})
    }
  };
}

export async function bulkUploadProductsToFirestore(items: any[]) {
  if (!db) throw new Error("Base de datos no inicializada. Configura firebaseConfig.");
  const batch = writeBatch(db);
  let success = 0;
  
  items.forEach((item) => {
    const docRef = doc(db, 'productos', item.id || item.clave || Math.random().toString(36).substr(2, 9));
    batch.set(docRef, item, { merge: true });
    success++;
  });
  
  await batch.commit();
  return { success, failed: 0 };
}
