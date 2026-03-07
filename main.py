import yt_dlp
import os

DOWNLOAD_DIR = "downloads"


def progresso(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()

        print(f"⬇️ {percent} | 🚀 {speed} | ⏳ ETA: {eta}", end="\r")

    elif d['status'] == 'finished':
        print("\n✅ Download concluído. Processando arquivo...")


def criar_pasta():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)


def obter_info(url):
    ydl_opts = {'quiet': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    print("\n📹 Informações do vídeo")
    print("Título:", info.get("title"))
    print("Canal:", info.get("uploader"))
    print("Duração:", info.get("duration"), "segundos")

    return info


def baixar_video(url, formato="video"):
    criar_pasta()

    if formato == "audio":
        formato_dl = "bestaudio"
        posprocess = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    else:
        formato_dl = "bestvideo+bestaudio/best"
        posprocess = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]

    opcoes = {
        'format': formato_dl,
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'progress_hooks': [progresso],
        'postprocessors': posprocess
    }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        ydl.download([url])


def escolher_formato():
    print("\nEscolha o formato:")
    print("1 - Vídeo MP4")
    print("2 - Apenas áudio MP3")

    opcao = input("Opção: ").strip()

    if opcao == "2":
        return "audio"
    return "video"


def main():
    print("=== 🎬 YouTube Downloader ===")

    url = input("Cole o link do vídeo: ").strip()

    if not url:
        print("❌ Você precisa inserir um link.")
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