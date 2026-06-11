/* ══════════════════════════════════════════
   STATE
══════════════════════════════════════════ */
const state = {
  csvData: null,       // Array of product objects
  photoMap: {},        // filename (lowercase, no ext) → object URL
  columns: 2,
  primaryColor: '#6366f1',
  empresa: '',
  catalogoTitulo: '',
  dataSource: null,    // 'sheets' | 'csv'
};

/* ══════════════════════════════════════════
   GOOGLE SHEETS INTEGRATION
══════════════════════════════════════════ */

/**
 * Validates pasted Sheets URL and lights up the button
 */
function handleSheetsUrl(value) {
  const input = document.getElementById('sheets-url');
  const btn = document.getElementById('btn-sheets-load');
  const id = extractSheetId(value);

  if (id) {
    input.classList.remove('invalid');
    input.classList.add('valid');
    btn.disabled = false;
  } else if (value.length > 10) {
    input.classList.add('invalid');
    input.classList.remove('valid');
    btn.disabled = true;
  } else {
    input.classList.remove('valid', 'invalid');
    btn.disabled = false;
  }
}

/**
 * Extracts the spreadsheet ID from any Google Sheets URL
 */
function extractSheetId(url) {
  const match = url.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/);
  return match ? match[1] : null;
}

/**
 * Extracts optional gid (sheet tab) from URL
 */
function extractGid(url) {
  const match = url.match(/[#&?]gid=(\d+)/);
  return match ? match[1] : '0';
}

/**
 * Converts a Google Sheets URL to a CSV export URL
 */
function buildCsvUrl(sheetUrl) {
  const id = extractSheetId(sheetUrl);
  const gid = extractGid(sheetUrl);
  if (!id) return null;
  return `https://docs.google.com/spreadsheets/d/${id}/export?format=csv&gid=${gid}`;
}

/**
 * Converts a Google Drive share link to a direct image URL
 * Handles: /file/d/ID/view  →  /uc?export=view&id=ID
 */
function normalizeDriveUrl(url) {
  if (!url) return url;
  // Already direct
  if (url.includes('drive.google.com/uc') || url.includes('lh3.googleusercontent.com')) return url;
  // Share link format
  const match = url.match(/\/file\/d\/([a-zA-Z0-9_-]+)/);
  if (match) return `https://drive.google.com/uc?export=view&id=${match[1]}`;
  return url;
}

/**
 * Main function: fetch CSV from Google Sheets and parse it
 */
async function loadFromSheets() {
  const url = document.getElementById('sheets-url').value.trim();
  const csvUrl = buildCsvUrl(url);
  const btn = document.getElementById('btn-sheets-load');
  const statusEl = document.getElementById('sheets-status');

  if (!csvUrl) {
    setSheetStatus('✗ Link inválido. Asegurate de pegar el link completo de Google Sheets.', 'error');
    return;
  }

  // Loading state
  btn.classList.add('loading');
  btn.disabled = true;
  setSheetStatus('⏳ Conectando con Google Sheets...', 'loading');

  try {
    const response = await fetch(csvUrl);
    if (!response.ok) {
      throw new Error(`No se pudo acceder al Sheet (${response.status}). Verificá que esté compartido como "Cualquiera con el link puede ver".`);
    }
    const text = await response.text();
    state.csvData = parseCSV(text);

    if (state.csvData.length === 0) {
      throw new Error('El Sheet no tiene filas de datos. Verificá que tenga encabezados y productos.');
    }

    state.dataSource = 'sheets';
    setSheetStatus(`✓ ${state.csvData.length} productos cargados desde Google Sheets`, 'success');
    // Clear CSV status since sheets takes priority
    setStatus('csv', '', 'info');
    checkReady();

  } catch (err) {
    setSheetStatus(`✗ ${err.message}`, 'error');
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
}

function setSheetStatus(msg, cls) {
  const el = document.getElementById('sheets-status');
  el.textContent = msg;
  el.className = 'sheets-status ' + cls;
}

/* ══════════════════════════════════════════
   TEMPLATE CSV DOWNLOAD
══════════════════════════════════════════ */
function downloadTemplate() {
  const header = [
    'nombre',
    'descripcion',
    'imagen',
    'imagen_url',
    'sku_caja',
    'unidades_caja',
    'ean_caja',
    'sku_paquete',
    'unidades_paquete',
    'ean_paquete',
    'marca',
    'categoria',
    'precio_lista'
  ].join(',');

  const rows = [
    [
      'Aceite de Oliva Extra Virgen',
      'Aceite de oliva prensado en frío, ideal para ensaladas y cocina gourmet.',
      'aceite_oliva.jpg',
      'https://drive.google.com/file/d/TU_ID_AQUI/view',
      'AOV-C-001',
      '12',
      '7501234567890',
      'AOV-P-001',
      '1',
      '7501234567891',
      'Marca XYZ',
      'Aceites y Condimentos',
      '85.00'
    ],
    [
      'Arroz Blanco Extra',
      'Arroz de grano largo, cocción rápida y suave al paladar.',
      'arroz_blanco.jpg',
      '',
      'ARR-C-010',
      '24',
      '7501234500011',
      'ARR-P-010',
      '1',
      '7501234500012',
      'Marca XYZ',
      'Granos y Cereales',
      '22.50'
    ],
    [
      'Sal de Mesa Fina',
      'Sal refinada de uso doméstico e industrial.',
      'sal_mesa.jpg',
      '',
      'SAL-C-002',
      '30',
      '7501234512345',
      '',
      '',
      '',
      'Marca ABC',
      'Condimentos',
      '8.00'
    ]
  ].map(r => r.map(v => `"${v}"`).join(','));

  const csv = [header, ...rows].join('\n');
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'plantilla_catalogo.csv';
  a.click();
  URL.revokeObjectURL(url);
}

/* ══════════════════════════════════════════
   HELP PANEL
══════════════════════════════════════════ */
function toggleHelp() {
  document.getElementById('help-panel').classList.toggle('hidden');
}

/* ══════════════════════════════════════════
   COLOR
══════════════════════════════════════════ */
function setColor(hex) {
  document.getElementById('config-color').value = hex;
  state.primaryColor = hex;
  document.documentElement.style.setProperty('--primary', hex);
  const light = hexToRgba(hex, 0.15);
  document.documentElement.style.setProperty('--primary-light', light);
}

document.getElementById('config-color').addEventListener('input', (e) => {
  setColor(e.target.value);
});

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `rgba(${r},${g},${b},${alpha})`;
}

/* ══════════════════════════════════════════
   DRAG & DROP
══════════════════════════════════════════ */
function handleDragOver(e, type) {
  e.preventDefault();
  document.getElementById(`${type}-dropzone`).classList.add('drag-over');
}
function handleDragLeave(e, type) {
  document.getElementById(`${type}-dropzone`).classList.remove('drag-over');
}
function handleDrop(e, type) {
  e.preventDefault();
  document.getElementById(`${type}-dropzone`).classList.remove('drag-over');
  if (type === 'csv') {
    const file = e.dataTransfer.files[0];
    if (file) handleCSVFile(file);
  } else {
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
    if (files.length) handlePhotoFilesArray(files);
  }
}

/* ══════════════════════════════════════════
   CSV PARSING
══════════════════════════════════════════ */
function handleCSVFile(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const text = e.target.result;
      state.csvData = parseCSV(text);
      if (state.csvData.length === 0) throw new Error('El CSV no tiene filas de datos.');
      setStatus('csv', `✓ ${state.csvData.length} productos cargados`, 'success');
      checkReady();
    } catch(err) {
      setStatus('csv', `✗ Error: ${err.message}`, 'error');
    }
  };
  reader.readAsText(file, 'UTF-8');
}

function parseCSV(text) {
  // Remove BOM if present
  text = text.replace(/^\uFEFF/, '');
  const lines = text.split(/\r?\n/).filter(l => l.trim());
  if (lines.length < 2) throw new Error('El archivo debe tener encabezado y al menos una fila.');

  const headers = parseCSVLine(lines[0]).map(h => h.trim().toLowerCase().replace(/\s+/g,'_'));
  const rows = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    if (values.length === 0 || values.every(v => !v.trim())) continue;
    const obj = {};
    headers.forEach((h, idx) => {
      obj[h] = (values[idx] || '').trim();
    });
    // Require at least a name
    if (!obj.nombre && !obj.name && !obj.producto) continue;
    rows.push(normalizeProduct(obj, headers));
  }
  return rows;
}

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i+1] === '"') { current += '"'; i++; }
      else inQuotes = !inQuotes;
    } else if ((ch === ',' || ch === ';') && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += ch;
    }
  }
  result.push(current);
  return result;
}

// Normalize field names from CSV to internal schema
function normalizeProduct(obj, headers) {
  // Try to find fields by various possible names
  const get = (...keys) => {
    for (const k of keys) {
      if (obj[k] !== undefined && obj[k] !== '') return obj[k];
    }
    return '';
  };

  return {
    nombre:           get('nombre', 'name', 'producto', 'product', 'descripcion_corta', 'titulo'),
    descripcion:      get('descripcion', 'description', 'detalle', 'detail', 'descripcion_larga'),
    imagen:           get('imagen', 'image', 'foto', 'photo', 'img', 'archivo_imagen'),
    imagen_url:       get('imagen_url', 'image_url', 'foto_url', 'drive_url', 'url_imagen', 'photo_url'),
    sku_caja:         get('sku_caja', 'sku_box', 'caja_sku', 'box_sku', 'sku_c', 'codigo_caja'),
    unidades_caja:    get('unidades_caja', 'units_box', 'qty_box', 'unidades', 'cantidad_caja', 'piezas_caja'),
    ean_caja:         get('ean_caja', 'ean_box', 'barcode_caja', 'gtin_caja', 'codigo_barra_caja'),
    sku_paquete:      get('sku_paquete', 'sku_package', 'paquete_sku', 'pkg_sku', 'sku_p', 'codigo_paquete'),
    unidades_paquete: get('unidades_paquete', 'units_pkg', 'qty_pkg', 'cantidad_paquete'),
    ean_paquete:      get('ean_paquete', 'ean_package', 'barcode_paquete', 'gtin_paquete'),
    marca:            get('marca', 'brand', 'fabricante'),
    categoria:        get('categoria', 'category', 'linea', 'line', 'rubro'),
    precio_lista:     get('precio_lista', 'price', 'precio', 'list_price', 'pvp'),
  };
}

/* ══════════════════════════════════════════
   PHOTO HANDLING
══════════════════════════════════════════ */
function handlePhotoFiles(fileList) {
  handlePhotoFilesArray(Array.from(fileList));
}

function handlePhotoFilesArray(files) {
  const images = files.filter(f => f.type.startsWith('image/'));
  if (images.length === 0) {
    setStatus('photos', '✗ No se encontraron imágenes', 'error');
    return;
  }
  // Clear previous
  Object.values(state.photoMap).forEach(url => URL.revokeObjectURL(url));
  state.photoMap = {};

  images.forEach(file => {
    const key = normalizeImageKey(file.name);
    state.photoMap[key] = URL.createObjectURL(file);
  });

  setStatus('photos', `✓ ${images.length} imágenes cargadas`, 'success');
  checkReady();
}

function normalizeImageKey(filename) {
  // Remove extension, lowercase, normalize spaces/underscores
  return filename.replace(/\.[^.]+$/, '').toLowerCase().replace(/[\s-]+/g, '_');
}

function findPhoto(p) {
  // Priority 1: imagen_url (Google Drive or any direct URL)
  if (p.imagen_url) return normalizeDriveUrl(p.imagen_url);
  // Priority 2: local uploaded photo matched by filename
  if (p.imagen) {
    const key = normalizeImageKey(p.imagen);
    if (state.photoMap[key]) return state.photoMap[key];
  }
  return null;
}

/* ══════════════════════════════════════════
   STATUS HELPERS
══════════════════════════════════════════ */
function setStatus(type, msg, cls) {
  const el = document.getElementById(`${type}-status`);
  el.textContent = msg;
  el.className = 'upload-status ' + cls;
}

function checkReady() {
  const btn = document.getElementById('btn-generate');
  const hint = document.getElementById('generate-hint');
  if (state.csvData && state.csvData.length > 0) {
    btn.disabled = false;
    const photoCount = Object.keys(state.photoMap).length;
    hint.textContent = photoCount > 0
      ? `${state.csvData.length} productos · ${photoCount} fotos listas`
      : `${state.csvData.length} productos listos (sin fotos)`;
  } else {
    btn.disabled = true;
    hint.textContent = 'Cargá el CSV para activar el generador';
  }
}

/* ══════════════════════════════════════════
   GENERATE CATALOG
══════════════════════════════════════════ */
function generateCatalog() {
  if (!state.csvData || state.csvData.length === 0) return;

  // Read config
  state.columns = parseInt(document.getElementById('config-cols').value) || 2;
  state.empresa = document.getElementById('empresa-nombre').value || 'Mi Empresa';
  state.catalogoTitulo = document.getElementById('catalogo-titulo').value || 'Catálogo de Productos';
  state.primaryColor = document.getElementById('config-color').value;

  // Apply color
  setColor(state.primaryColor);

  const perPage = state.columns === 1 ? 2 : state.columns === 2 ? 4 : 6;
  const products = state.csvData;
  const totalPages = Math.ceil(products.length / perPage);

  const container = document.getElementById('catalog-pages');
  container.innerHTML = '';

  for (let p = 0; p < totalPages; p++) {
    const slice = products.slice(p * perPage, (p + 1) * perPage);
    const pageEl = buildPage(slice, p + 1, totalPages);
    container.appendChild(pageEl);
  }

  // Update toolbar
  document.getElementById('toolbar-title').textContent = state.catalogoTitulo;
  document.getElementById('toolbar-count').textContent = `${products.length} productos · ${totalPages} páginas`;

  // Show catalog
  document.getElementById('app-shell').classList.add('hidden');
  document.getElementById('catalog-view').classList.remove('hidden');
  window.scrollTo(0, 0);
}

function buildPage(products, pageNum, totalPages) {
  const page = document.createElement('div');
  page.className = 'catalog-page';

  // Header
  const header = document.createElement('div');
  header.className = 'page-header';
  header.innerHTML = `
    <span class="page-header-brand" style="color:${state.primaryColor}">${escapeHtml(state.empresa)}</span>
    <span class="page-header-title">${escapeHtml(state.catalogoTitulo)}</span>
    <span class="page-number">Página ${pageNum} / ${totalPages}</span>
  `;
  page.appendChild(header);

  // Products grid
  const grid = document.createElement('div');
  grid.className = `products-in-page cols-${state.columns}`;

  products.forEach(product => {
    grid.appendChild(buildProductCard(product));
  });

  page.appendChild(grid);

  // Footer
  const footer = document.createElement('div');
  footer.className = 'page-footer';
  const today = new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long' });
  footer.innerHTML = `
    <span>${escapeHtml(state.empresa)}</span>
    <span>${today}</span>
  `;
  page.appendChild(footer);

  return page;
}

function buildProductCard(p) {
  const card = document.createElement('div');
  card.className = 'product-card';

  // ── Image ──
  const imgWrap = document.createElement('div');
  imgWrap.className = 'product-img-wrap';

  const photoUrl = findPhoto(p);
  if (photoUrl) {
    const img = document.createElement('img');
    img.src = photoUrl;
    img.alt = p.nombre;
    img.loading = 'lazy';
    imgWrap.appendChild(img);
  } else {
    imgWrap.innerHTML = `
      <div class="product-img-placeholder">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
          <path d="M21 15l-5-5L5 21"/>
        </svg>
        <span>Sin imagen</span>
      </div>
    `;
  }
  card.appendChild(imgWrap);

  // ── Info ──
  const info = document.createElement('div');
  info.className = 'product-info';

  let extraHtml = '';
  if (p.marca) extraHtml += `<strong>Marca:</strong> ${escapeHtml(p.marca)}  `;
  if (p.categoria) extraHtml += `<strong>Cat.:</strong> ${escapeHtml(p.categoria)}  `;
  if (p.precio_lista) extraHtml += `<strong>Precio lista:</strong> $${escapeHtml(p.precio_lista)}`;

  info.innerHTML = `
    <div class="product-name">${escapeHtml(p.nombre)}</div>
    ${p.descripcion ? `<div class="product-desc">${escapeHtml(p.descripcion)}</div>` : ''}
    ${extraHtml ? `<div class="product-extra">${extraHtml}</div>` : ''}
  `;
  card.appendChild(info);

  // ── SKUs ──
  const hasCaja = !!p.sku_caja;
  const hasPaquete = !!p.sku_paquete;

  if (hasCaja || hasPaquete) {
    const skuSection = document.createElement('div');
    skuSection.className = `product-skus ${hasCaja && hasPaquete ? 'has-both' : 'has-one'}`;

    if (hasCaja) {
      skuSection.appendChild(buildSkuBlock('CAJA', p.sku_caja, p.unidades_caja, p.ean_caja, state.primaryColor));
    }
    if (hasPaquete) {
      skuSection.appendChild(buildSkuBlock('PAQUETE', p.sku_paquete, p.unidades_paquete, p.ean_paquete, state.primaryColor));
    }

    card.appendChild(skuSection);
  }

  return card;
}

function buildSkuBlock(tipo, sku, unidades, ean, color) {
  const icon = tipo === 'CAJA'
    ? `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>`
    : `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>`;

  const block = document.createElement('div');
  block.className = 'sku-block';

  const lightColor = hexToRgbaStatic(color, 0.15);
  block.innerHTML = `
    <div class="sku-label" style="color:${color};background:${lightColor}">
      ${icon} ${tipo}
    </div>
    <div class="sku-code">${escapeHtml(sku)}</div>
    <div class="sku-detail">
      ${unidades ? `<strong>Contenido:</strong> ${escapeHtml(unidades)} unid.<br/>` : ''}
      ${ean ? `<strong>EAN:</strong> ${escapeHtml(ean)}` : ''}
    </div>
  `;
  return block;
}

function hexToRgbaStatic(hex, alpha) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `rgba(${r},${g},${b},${alpha})`;
}

/* ══════════════════════════════════════════
   BACK TO UPLOAD
══════════════════════════════════════════ */
function backToUpload() {
  document.getElementById('catalog-view').classList.add('hidden');
  document.getElementById('app-shell').classList.remove('hidden');
}

/* ══════════════════════════════════════════
   UTILS
══════════════════════════════════════════ */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}

/* ══════════════════════════════════════════
   INIT
══════════════════════════════════════════ */
// Make photos-input support folder selection on modern browsers
document.getElementById('photos-input').setAttribute('webkitdirectory', '');
document.getElementById('photos-input').setAttribute('mozdirectory', '');

// Expose functions to window for inline HTML handlers
window.handleSheetsUrl = handleSheetsUrl;
window.loadFromSheets = loadFromSheets;
window.downloadTemplate = downloadTemplate;
window.toggleHelp = toggleHelp;
window.setColor = setColor;
window.handleDragOver = handleDragOver;
window.handleDragLeave = handleDragLeave;
window.handleDrop = handleDrop;
window.handleCSVFile = handleCSVFile;
window.handlePhotoFiles = handlePhotoFiles;
window.generateCatalog = generateCatalog;
window.backToUpload = backToUpload;


// Load AI Sync Module
import './ai-sync.js';
