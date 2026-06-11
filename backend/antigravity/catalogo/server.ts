import express from 'express';
import { createServer as createViteServer } from 'vite';
import cors from 'cors';
import dotenv from 'dotenv';
import { google } from 'googleapis';
import { GoogleGenAI } from '@google/genai';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json());

// Initialize Gemini
// Assumes GEMINI_API_KEY is in .env
const ai = new GoogleGenAI({});

/**
 * Endpoint to list files in a Google Drive folder.
 * Expects { folderUrl, token } in the body.
 */
app.post('/api/drive/list', async (req, res) => {
  try {
    const { folderUrl, token } = req.body;
    if (!folderUrl || !token) {
      return res.status(400).json({ error: 'Falta folderUrl o token' });
    }

    // Extract folder ID from URL
    const match = folderUrl.match(/folders\/([a-zA-Z0-9_-]+)/);
    const folderId = match ? match[1] : folderUrl; // fallback to treating it as ID

    const auth = new google.auth.OAuth2();
    auth.setCredentials({ access_token: token });

    const drive = google.drive({ version: 'v3', auth });
    
    const response = await drive.files.list({
      q: `'${folderId}' in parents and trashed = false and mimeType contains 'image/'`,
      fields: 'files(id, name, webContentLink, webViewLink)',
      pageSize: 1000,
    });

    res.json({ files: response.data.files });
  } catch (error) {
    console.error('Error listing drive files:', error);
    res.status(500).json({ error: 'Error al listar archivos de Drive', details: error.message });
  }
});

/**
 * Endpoint to match SKU using Gemini 1.5 Flash
 * Expects { fileId, fileName, token }
 * Downloads the image from drive and sends it to Gemini.
 */
app.post('/api/match-sku', async (req, res) => {
  try {
    const { fileId, fileName, token } = req.body;
    if (!fileId || !fileName || !token) {
      return res.status(400).json({ error: 'Falta fileId, fileName o token' });
    }

    // 1. Download image from Google Drive
    const auth = new google.auth.OAuth2();
    auth.setCredentials({ access_token: token });
    const drive = google.drive({ version: 'v3', auth });

    const response = await drive.files.get(
      { fileId: fileId, alt: 'media' },
      { responseType: 'arraybuffer' }
    );
    
    const base64Image = Buffer.from(response.data as ArrayBuffer).toString('base64');
    
    // 2. Call Gemini API
    const prompt = `Analiza el nombre del archivo: "${fileName}" y la imagen adjunta. 
Tu tarea es extraer el código SKU del producto. 
El SKU suele ser un código alfanumérico (ej: AOV-C-001, ARR-P-010). 
Valida visualmente la imagen para asegurarte de que corresponde a un producto con este SKU (si el SKU es legible en la caja o paquete, confírmalo, de lo contrario extrae el SKU del nombre del archivo).
Responde ÚNICAMENTE con el código SKU identificado, sin texto adicional ni comillas.`;

    const result = await ai.models.generateContent({
      model: 'gemini-1.5-flash',
      contents: [
        {
          role: 'user',
          parts: [
            { text: prompt },
            {
              inlineData: {
                mimeType: 'image/jpeg', // Assuming jpeg, could dynamically detect if needed
                data: base64Image,
              }
            }
          ]
        }
      ]
    });

    const sku = result.text.trim();
    res.json({ sku });

  } catch (error) {
    console.error('Error matching SKU:', error);
    res.status(500).json({ error: 'Error al analizar la imagen', details: error.message });
  }
});

// Create Vite server in middleware mode
async function startServer() {
  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa',
  });

  // Use vite's connect instance as middleware
  app.use(vite.middlewares);

  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
  });
}

startServer();
