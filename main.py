from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
import uuid
import shutil
import zipfile

app = FastAPI()

# ============================
#   CORS PARA NETLIFY
# ============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes poner tu dominio de Netlify si quieres
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
#   ENDPOINT PRINCIPAL
# ============================
@app.post("/descargar")
def descargar(url: str, tipo: str, carpeta: str = "Descargas_Pinalo"):
    try:
        # Crear carpeta temporal única
        carpeta_id = f"{carpeta}_{uuid.uuid4()}"
        os.makedirs(carpeta_id, exist_ok=True)

        # Obtener información sin descargar
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        # Detectar playlist
        if "entries" in info:
            lista = info["entries"]
        else:
            lista = [info]

        # Configuración según tipo
        if tipo in ["playlist_audio", "audio"]:
            opciones = {
                "format": "bestaudio/best",
                "outtmpl": f"{carpeta_id}/%(title)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            }
        else:
            opciones = {
                "format": "best",
                "outtmpl": f"{carpeta_id}/%(title)s.%(ext)s"
            }

        # Descargar uno por uno
        with yt_dlp.YoutubeDL(opciones) as ydl:
            for entry in lista:
                ydl.download([entry["webpage_url"]])

        # Crear ZIP
        zip_name = f"{carpeta_id}.zip"
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(carpeta_id):
                for file in files:
                    ruta = os.path.join(root, file)
                    zipf.write(ruta, os.path.relpath(ruta, carpeta_id))

        # Borrar carpeta temporal
        shutil.rmtree(carpeta_id)

        return FileResponse(zip_name, filename=zip_name)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


