from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
import uuid
import shutil
import zipfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/descargar")
def descargar(
    url: str = Form(...),
    tipo: str = Form(...),
    carpeta: str = Form("Descargas_Pinalo")
):
    try:
        carpeta_id = f"{carpeta}_{uuid.uuid4()}"
        os.makedirs(carpeta_id, exist_ok=True)

        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        lista = info["entries"] if "entries" in info else [info]

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

        with yt_dlp.YoutubeDL(opciones) as ydl:
            for entry in lista:
                ydl.download([entry["webpage_url"]])

        zip_name = f"{carpeta_id}.zip"
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(carpeta_id):
                for file in files:
                    ruta = os.path.join(root, file)
                    zipf.write(ruta, os.path.relpath(ruta, carpeta_id))

        shutil.rmtree(carpeta_id)

        return FileResponse(zip_name, filename=zip_name)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

