import { auth, provider, signInWithPopup, signOut } from './firebase-config.js';

let googleAccessToken = null;

// UI Elements
const btnLogin = document.getElementById('btn-login');
const btnLogout = document.getElementById('btn-logout');
const userInfo = document.getElementById('user-info');
const userName = document.getElementById('user-name');
const userAvatar = document.getElementById('user-avatar');
const btnSyncAi = document.getElementById('btn-sync-ai');
const driveFolderUrl = document.getElementById('drive-folder-url');
const aiStatus = document.getElementById('ai-status');

const progressContainer = document.getElementById('ai-progress-container');
const progressText = document.getElementById('ai-progress-text');
const progressCount = document.getElementById('ai-progress-count');
const progressBar = document.getElementById('ai-progress-bar');
const btnExportJson = document.getElementById('btn-export-json');

// Wait for Auth State
auth.onAuthStateChanged((user) => {
  if (user) {
    // User is signed in.
    btnLogin.classList.add('hidden');
    userInfo.classList.remove('hidden');
    userName.textContent = user.displayName;
    userAvatar.src = user.photoURL;
    aiStatus.textContent = 'Listo para sincronizar. Pega la URL de tu carpeta.';
    aiStatus.className = 'upload-status info';
    checkSyncReady();
  } else {
    // No user
    btnLogin.classList.remove('hidden');
    userInfo.classList.add('hidden');
    aiStatus.textContent = 'Inicia sesión con Google para usar esta función.';
    aiStatus.className = 'upload-status';
    googleAccessToken = null;
    btnSyncAi.disabled = true;
  }
});

// Login Handlers
btnLogin.addEventListener('click', async () => {
  try {
    const result = await signInWithPopup(auth, provider);
    const credential = GoogleAuthProvider.credentialFromResult(result);
    // Get the OAuth access token for Google Drive API
    googleAccessToken = credential.accessToken;
  } catch (error) {
    console.error('Login error:', error);
    alert('Error al iniciar sesión: ' + error.message);
  }
});

btnLogout.addEventListener('click', () => {
  signOut(auth);
});

// Sync Ready Check
driveFolderUrl.addEventListener('input', checkSyncReady);

function checkSyncReady() {
  if (auth.currentUser && driveFolderUrl.value.trim().length > 10 && window.state.csvData?.length > 0) {
    btnSyncAi.disabled = false;
  } else {
    btnSyncAi.disabled = true;
  }
}

// Ensure it activates when CSV loads
const originalCheckReady = window.checkReady;
window.checkReady = function() {
  originalCheckReady();
  checkSyncReady();
};

// Start AI Sync
btnSyncAi.addEventListener('click', async () => {
  const folderUrl = driveFolderUrl.value.trim();
  if (!folderUrl || !googleAccessToken) return;

  btnSyncAi.disabled = true;
  btnSyncAi.innerHTML = 'Sincronizando...';
  progressContainer.classList.remove('hidden');
  
  try {
    // 1. List Files from backend
    aiStatus.textContent = 'Obteniendo archivos de Drive...';
    aiStatus.className = 'upload-status loading';
    
    const listRes = await fetch('/api/drive/list', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folderUrl, token: googleAccessToken })
    });
    
    if (!listRes.ok) throw new Error(await listRes.text());
    
    const { files } = await listRes.json();
    
    if (!files || files.length === 0) {
      throw new Error('No se encontraron imágenes en la carpeta.');
    }

    aiStatus.textContent = `Procesando ${files.length} imágenes con Gemini...`;
    
    let processed = 0;
    let matches = 0;
    
    // 2. Process each file
    for (const file of files) {
      processed++;
      progressText.textContent = `Analizando: ${file.name}`;
      progressCount.textContent = `${processed}/${files.length}`;
      progressBar.style.width = `${(processed / files.length) * 100}%`;
      
      try {
        const matchRes = await fetch('/api/match-sku', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fileId: file.id, fileName: file.name, token: googleAccessToken })
        });
        
        if (matchRes.ok) {
          const { sku } = await matchRes.json();
          // 3. Match SKU with state.csvData
          const product = window.state.csvData.find(p => p.sku_caja === sku || p.sku_paquete === sku);
          
          if (product) {
            product.imagen_url = file.webContentLink; // Assign drive direct download link
            matches++;
          }
        }
      } catch (e) {
        console.error('Error in batch for file:', file.name, e);
      }
    }
    
    aiStatus.textContent = `Sincronización completada. ${matches} productos actualizados.`;
    aiStatus.className = 'upload-status success';
    window.checkReady(); // Update main UI
    
    // Show JSON export button
    btnExportJson.classList.remove('hidden');

  } catch (error) {
    console.error('Sync error:', error);
    aiStatus.textContent = 'Error: ' + error.message;
    aiStatus.className = 'upload-status error';
  } finally {
    btnSyncAi.disabled = false;
    btnSyncAi.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> Sincronizar con IA`;
    setTimeout(() => {
      progressContainer.classList.add('hidden');
    }, 3000);
  }
});

// JSON Export functionality
btnExportJson.addEventListener('click', () => {
  if (!window.state.csvData) return;
  
  const jsonStr = JSON.stringify(window.state.csvData, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = "productos_sincronizados.json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});
