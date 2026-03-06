import yt_dlp

def baixar_video(url):
    opcoes = {
        'format': 'bestvideo+bestaudio/best',   # melhor qualidade disponível
        'outtmpl': '%(title)s.%(ext)s',         # nome do arquivo
        'noplaylist': True,                     # baixa apenas o vídeo
        'merge_output_format': 'mp4',           # força saída em MP4
        'progress_hooks': [progresso],

        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        ydl.download([url])


def progresso(d):
    if d['status'] == 'downloading':
        print(f"Baixando: {d.get('_percent_str','')} | Velocidade: {d.get('_speed_str','')}")
    elif d['status'] == 'finished':
        print("Download concluído, convertendo para MP4...")


def main():
    print("=== Downloader de vídeos do YouTube ===")
    url = input("Cole o link do vídeo: ").strip()

    if not url:
        print("Você precisa inserir um link.")
        return

    try:
        baixar_video(url)
        print("✅ Vídeo baixado com sucesso!")
    except Exception as e:
        print("❌ Erro ao baixar:", e)


if __name__ == "__main__":
    main()