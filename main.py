import yt_dlp
import re
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

DOWNLOAD_DIR = Path("downloads")
HISTORY_FILE = Path("downloads/history.json")


# ---------------------------
# UTILIDADES
# ---------------------------

def criar_pasta():
    DOWNLOAD_DIR.mkdir(exist_ok=True)

def limpar_nome(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome)

def formatar_tempo(segundos):
    if not segundos:
        return "Desconhecido"

    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60

    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def formatar_tamanho(bytes):
    if not bytes:
        return "Desconhecido"

    for unidade in ["B", "KB", "MB", "GB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unidade}"
        bytes /= 1024


# ---------------------------
# HISTÓRICO
# ---------------------------

def carregar_historico():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []

def salvar_historico(video_id):
    hist = carregar_historico()
    hist.append(video_id)
    HISTORY_FILE.write_text(json.dumps(hist, indent=2))

def ja_baixado(video_id):
    return video_id in carregar_historico()


# ---------------------------
# PROGRESSO
# ---------------------------

def progresso(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()

        print(f"⬇️ {percent} | 🚀 {speed} | ⏳ ETA {eta}", end="\r")

    elif d["status"] == "finished":
        print("\n📦 Download concluído. Processando...")


# ---------------------------
# INFORMAÇÕES DO VÍDEO
# ---------------------------

def obter_info(url):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    print("\n📹 Informações")
    print("Título :", info.get("title"))
    print("Canal  :", info.get("uploader"))
    print("Duração:", formatar_tempo(info.get("duration")))
    print("Views  :", info.get("view_count"))
    print("Tamanho estimado:", formatar_tamanho(info.get("filesize") or info.get("filesize_approx")))

    return info


# ---------------------------
# ESCOLHAS
# ---------------------------

def escolher_formato():
    print("\nFormato:")
    print("1 - Vídeo MP4")
    print("2 - Áudio MP3")

    op = input("Escolha: ").strip()

    if op == "2":
        return "audio"

    return "video"


def escolher_qualidade():
    print("\nQualidade:")
    print("1 - Melhor")
    print("2 - 1080p")
    print("3 - 720p")
    print("4 - 480p")

    op = input("Escolha: ").strip()

    qualidades = {
        "1": "bestvideo+bestaudio/best",
        "2": "bestvideo[height<=1080]+bestaudio/best",
        "3": "bestvideo[height<=720]+bestaudio/best",
        "4": "bestvideo[height<=480]+bestaudio/best",
    }

    return qualidades.get(op, qualidades["1"])


# ---------------------------
# NOVA FUNÇÃO
# ORGANIZAR POR CANAL
# ---------------------------

def obter_pasta_canal(info):

    canal = info.get("uploader") or "Desconhecido"
    canal = limpar_nome(canal)

    pasta = DOWNLOAD_DIR / canal
    pasta.mkdir(parents=True, exist_ok=True)

    return pasta


# ---------------------------
# DOWNLOAD
# ---------------------------

def baixar(url, formato="video"):
    criar_pasta()

    # primeiro pega info para descobrir canal
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info_preview = ydl.extract_info(url, download=False)

    pasta_canal = obter_pasta_canal(info_preview)

    base_opts = {
        "outtmpl": f"{pasta_canal}/%(title)s.%(ext)s",
        "progress_hooks": [progresso],
        "ignoreerrors": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "writethumbnail": True,
    }

    if formato == "audio":

        base_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        })

    else:

        qualidade = escolher_qualidade()

        base_opts.update({
            "format": qualidade,
            "merge_output_format": "mp4",
        })

    with yt_dlp.YoutubeDL(base_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        if info:
            salvar_historico(info.get("id"))


# ---------------------------
# PLAYLIST
# ---------------------------

def baixar_playlist(url, formato):

    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = info.get("entries", [])

    print(f"\n📃 Playlist com {len(entries)} vídeos")

    with ThreadPoolExecutor(max_workers=3) as executor:
        for video in entries:
            if not video:
                continue

            if ja_baixado(video["id"]):
                print(f"⏭️ Já baixado: {video['title']}")
                continue

            executor.submit(baixar, video["webpage_url"], formato)


# ---------------------------
# MAIN
# ---------------------------

def main():

    print("🎬 ===== YouTube Downloader PRO =====")

    url = input("Cole o link: ").strip()

    if not url:
        print("❌ URL inválida")
        return

    info = obter_info(url)

    formato = escolher_formato()

    if info.get("_type") == "playlist":
        baixar_playlist(url, formato)
    else:
        baixar(url, formato)

    print("\n🎉 Finalizado!")


if __name__ == "__main__":
    main()