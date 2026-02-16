from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import os
import uuid
import subprocess

app = FastAPI()

def descargar_archivo(url, tipo):
    nombre = str(uuid.uuid4())

    if tipo == "video":
        ydl_opts = {
            "outtmpl": f"{nombre}.%(ext)s"
        }
    elif tipo == "audio":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{nombre}.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        }
    else:
        raise Exception("Tipo no válido")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Buscar archivo generado
    for f in os.listdir():
        if f.startswith(nombre):
            return f

    raise Exception("No se generó archivo")

@app.post("/descargar")
def descargar(url: str, tipo: str):
    try:
        archivo = descargar_archivo(url, tipo)
        return FileResponse(archivo, filename=archivo)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
