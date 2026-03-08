import yt_dlp
import os
import re
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")


def formatar_tempo(segundos):
    if not segundos:
        return "Desconhecido"

    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60

    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def limpar_nome(nome):
    """Remove caracteres inválidos do nome do arquivo"""
    return re.sub(r'[\\/*?:"<>|]', "", nome)


def progresso(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()

        print(f"⬇️ {percent} | 🚀 {speed} | ⏳ ETA {eta}", end="\r")

    elif d["status"] == "finished":
        print("\n📦 Download concluído. Processando arquivo...")


def criar_pasta():
    DOWNLOAD_DIR.mkdir(exist_ok=True)


def obter_info(url):
    opcoes = {"quiet": True}

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        info = ydl.extract_info(url, download=False)

    print("\n📹 Informações do vídeo")
    print("Título :", info.get("title"))
    print("Canal  :", info.get("uploader"))
    print("Duração:", formatar_tempo(info.get("duration")))
    print("Views  :", info.get("view_count"))

    return info


def escolher_formato():
    print("\nEscolha o formato:")
    print("1 - Vídeo MP4 (melhor qualidade)")
    print("2 - Apenas áudio MP3")

    opcao = input("Opção: ").strip()

    if opcao == "2":
        return "audio"
    return "video"


def escolher_qualidade():
    print("\nQualidade do vídeo:")
    print("1 - Melhor disponível")
    print("2 - 1080p")
    print("3 - 720p")
    print("4 - 480p")

    op = input("Escolha: ").strip()

    qualidades = {
        "1": "bestvideo+bestaudio/best",
        "2": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "3": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "4": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    }

    return qualidades.get(op, qualidades["1"])


def baixar_video(url, formato="video"):
    criar_pasta()

    if formato == "audio":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "progress_hooks": [progresso],
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

    else:
        qualidade = escolher_qualidade()

        ydl_opts = {
            "format": qualidade,
            "merge_output_format": "mp4",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "progress_hooks": [progresso],
            "noplaylist": True,
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    print("🎬 ===== YouTube Downloader =====")

    url = input("Cole o link do vídeo: ").strip()

    if not url:
        print("❌ Link inválido")
        return

    try:
        obter_info(url)

        formato = escolher_formato()

        baixar_video(url, formato)

        print("\n🎉 Download finalizado!")

    except yt_dlp.utils.DownloadError:
        print("❌ Erro ao baixar o vídeo.")
    except Exception as e:
        print("❌ Erro inesperado:", e)


if __name__ == "__main__":
    main()