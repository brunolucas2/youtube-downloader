import os
import shutil
import yt_dlp
from yt_dlp.utils import YoutubeDLError

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
MP3_BITRATES = [128, 192, 256, 320]

# Cores ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"


# ---------------------------------------------------------------------------
# Configuração e interface
# ---------------------------------------------------------------------------

def init():
    """Prepara o ambiente e retorna as opções base do yt-dlp."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    if os.name == "nt":
        os.system("")  # habilita sequências ANSI no terminal do Windows

    return {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "noplaylist": True,
        # O yt-dlp usa Deno por padrão; aqui o Node.js também é permitido
        # (versões antigas do yt-dlp ignoram esta opção).
        "js_runtimes": {"deno": {}, "node": {}},
    }


def clean():
    os.system("cls" if os.name == "nt" else "clear")


def paint(text, color):
    return f"{color}{text}{RESET}"


def show(text="", color=""):
    print(paint(text, color) if color else text)


def header():
    line = "=" * 44
    show(line, CYAN)
    show(f"{'YOUTUBE DOWNLOADER':^44}", BOLD + CYAN)
    show(line, CYAN)


def show_menu(title, options, back="Voltar"):
    show(f"\n{title}", BOLD + MAGENTA)
    for number, text in enumerate(options, 1):
        print(paint(f"[{number}]", CYAN), text)
    print(paint("[0]", CYAN), back)


def ask_number(prompt, maximum):
    """Pede um número entre 0 e `maximum` (0 = voltar)."""
    while True:
        value = input(prompt).strip()
        if value.isdigit() and 0 <= int(value) <= maximum:
            return int(value)
        show("Opção inválida!", RED)


def pause():
    input(paint("\nPressione Enter para voltar ao menu...", YELLOW))


def format_duration(seconds):
    if not seconds:
        return "desconhecida"
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


# ---------------------------------------------------------------------------
# Análise do vídeo e filtragem dos formatos
# ---------------------------------------------------------------------------

class YTDLPLogger:
    def __init__(self):
        self.messages = []

    def debug(self, message):
        pass

    def warning(self, message):
        self.messages.append(str(message))

    def error(self, message):
        self.messages.append(str(message))

def analyze_video(url, base):
    """Consulta metadados e formatos sem baixar nada."""
    logger = YTDLPLogger()

    opts = {
        **base,
        "quiet": True,
        "skip_download": True,
        "ignore_no_formats_error": True,
        "logger": logger,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    messages = " ".join(logger.messages).lower()

    if "private" in messages:
        raise ValueError("private video")

    if "unavailable" in messages or "removed" in messages:
        raise ValueError("video unavailable")

    if not info or not info.get("formats"):
        raise ValueError("Nenhum formato encontrado.")

    return info


def show_video_info(info):
    show("Informações do vídeo", BOLD + MAGENTA)
    fields = [
        ("Título", info.get("title")),
        ("Canal", info.get("channel") or info.get("uploader")),
        ("Duração", format_duration(info.get("duration"))),
        ("ID", info.get("id")),
    ]
    for label, value in fields:
        print(paint(f"{label}:", BLUE), value or "desconhecido")


def has_codec(codec):
    return codec not in (None, "none")


def video_score(f):
    return (
        (f.get("vcodec") or "").startswith("avc1"),
        f.get("ext") == "mp4",
        f.get("fps") or 0,
        f.get("tbr") or 0,
        has_codec(f.get("acodec")),
    )


def audio_score(f):
    return (f.get("language_preference") or 0, f.get("tbr") or 0)



def get_video_formats(info):
    """Uma opção por resolução, escolhendo o melhor formato de cada uma."""
    best = {}

    for f in info["formats"]:
        if not (has_codec(f.get("vcodec")) and f.get("height")):
            continue

        height = f["height"]

        if height not in best or video_score(f) > video_score(best[height]):
            best[height] = f

    return [
        {
            "format_id": f["format_id"],
            "height": height,
            "fps": f.get("fps"),
            "ext": f.get("ext"),
            "vcodec": f["vcodec"].split(".")[0],
            "has_audio": has_codec(f.get("acodec")),
        }
        for height, f in sorted(best.items(), reverse=True)
    ]



def get_audio_formats(info):
    """Formatos somente-áudio, sem duplicatas de (extensão, bitrate)."""
    best = {}
    for f in info["formats"]:
        if not (has_codec(f.get("acodec")) and not has_codec(f.get("vcodec"))):
            continue
        abr = f.get("abr") or f.get("tbr") or 0
        key = (f.get("ext"), round(abr))
        if key not in best or audio_score(f) > audio_score(best[key]):
            best[key] = f

    formats = [
        {
            "format_id": f["format_id"],
            "ext": f.get("ext"),
            "abr": f.get("abr") or f.get("tbr"),
            "acodec": f["acodec"].split(".")[0],
        }
        for f in best.values()
    ]
    return sorted(formats, key=lambda f: f["abr"] or 0, reverse=True)


def show_formats(info, mode):
    """Mostra as qualidades realmente disponíveis e devolve a lista exibida."""
    if mode == "mp4":
        formats = get_video_formats(info)
        labels = []
        for f in formats:
            fps = f" {round(f['fps'])}fps" if f["fps"] else ""
            audio = "vídeo + áudio" if f["has_audio"] else "áudio separado (FFmpeg)"
            labels.append(f"{f['height']}p{fps} · {f['ext']} ({f['vcodec']}) · {audio}")
        title = "Qualidades de vídeo disponíveis"
    else:
        formats = get_audio_formats(info)
        labels = []
        for f in formats:
            abr = f"{round(f['abr'])} kbps" if f["abr"] else "bitrate desconhecido"
            labels.append(f"{abr} · {f['ext']} ({f['acodec']})")
        title = "Áudio original disponível no YouTube"

    if formats:
        show_menu(title, labels)
    return formats


def choose_mp3_bitrate(source):
    """Pergunta a qualidade de conversão do MP3 (None = voltar)."""
    clean()
    header()

    show_menu("Qualidade de conversão para MP3", [f"{k} kbps" for k in MP3_BITRATES])
    show("São configurações de codificação, não bitrates originais do YouTube.", YELLOW)

    choice = ask_number("\nConversão: ", len(MP3_BITRATES))
    if choice == 0:
        return None

    kbps = MP3_BITRATES[choice - 1]
    if source["abr"] and kbps > source["abr"]:
        show(
            f"Aviso: a fonte escolhida tem ~{round(source['abr'])} kbps. "
            f"Converter para {kbps} kbps aumenta o arquivo, mas não a qualidade.",
            YELLOW,
        )
    return kbps


# ---------------------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------------------

def check_download_exists(info, mode, base):
    file_info = {**info, "ext": mode}

    with yt_dlp.YoutubeDL(base) as ydl:
        filepath = ydl.prepare_filename(file_info)

    return os.path.isfile(filepath)

def run_download(info, opts):
    """Baixa usando os dados já consultados, sem nova análise da URL."""
    info = {k: v for k, v in info.items() if k not in ("requested_formats", "requested_subtitles")}

    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.process_ie_result(info, download=True)

def download_video(info, quality, base):
    video_id = quality["format_id"]

    if quality["has_audio"]:
        selector = video_id
    else:
        selector = f"{video_id}+bestaudio[ext=m4a]/{video_id}+bestaudio"

    opts = {
        **base,
        "format": selector,
        "merge_output_format": "mp4",
        "postprocessors": [
            {"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"}
        ],
    }

    run_download(info, opts)
    
def download_audio(info, quality, base):
    opts = {
        **base,
        "format": quality["format_id"],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": str(quality["kbps"]),
        }],
    }
    run_download(info, opts)


# ---------------------------------------------------------------------------
# Fluxo principal
# ---------------------------------------------------------------------------


def format_error(error):
    message = str(error).lower()

    if "private video" in message:
        return "Não foi possível acessar: vídeo privado."

    if "unavailable" in message or "removed" in message:
        return "Vídeo indisponível ou removido."

    if (
        "is not a valid url" in message
        or "unsupported url" in message
        or "incomplete youtube id" in message
        or "truncated_id" in message
    ):
        return "URL inválida ou não suportada."
    
    if "unable to download webpage" in message or "connection" in message:
        return "Falha de conexão com o servidor."

    if "ffmpeg" in message:
        return "FFmpeg não encontrado ou não foi possível executá-lo."

    if isinstance(error, OSError):
        return "Erro ao acessar ou salvar o arquivo."

    return f"Erro inesperado: {error}"


def download_flow(base):
    clean()
    header()
    url = input("\nURL do vídeo (Enter para voltar): ").strip()
    if not url:
        return

    show("\nAnalisando vídeo...", YELLOW)
    info = analyze_video(url, base)

    clean()
    header()
    show_video_info(info)

    show_menu("Escolha o formato", ["MP4 — baixar vídeo", "MP3 — baixar áudio"])
    option = ask_number("\nOpção: ", 2)
    if option == 0:
        return
    mode = "mp4" if option == 1 else "mp3"

    clean()
    header()
    show_video_info(info)

    formats = show_formats(info, mode)
    if not formats:
        show("\nNenhuma qualidade disponível para esta opção.", RED)
        pause()
        return

    choice = ask_number("\nQualidade: ", len(formats))
    if choice == 0:
        return

    quality = formats[choice - 1]

    if mode == "mp3":
        kbps = choose_mp3_bitrate(quality)
        if kbps is None:
            return
        quality = {**quality, "kbps": kbps}

    if check_download_exists(info, mode, base):
        show("\nEste arquivo já existe na pasta downloads!", YELLOW)
        pause()
        return

    clean()
    header()
    show_video_info(info)
    show("\nBaixando...", YELLOW)

    try:
        if mode == "mp4":
            download_video(info, quality, base)
        else:
            download_audio(info, quality, base)

    except (YoutubeDLError, OSError) as erro:
        clean()
        header()
        show("\nFalha no download!", RED)
        show(format_error(erro), RED)
        pause()
        return

    show(f"\nDownload concluído! Arquivo salvo em '{DOWNLOAD_DIR}'.", GREEN)
    pause()


def main():
    base = init()

    while True:
        clean()
        header()
        if not shutil.which("ffmpeg"):
            show("Aviso: FFmpeg não encontrado no PATH. Alguns downloads e a conversão MP3 podem falhar.", YELLOW)

        show_menu("Menu", ["Baixar de uma URL"], back="Sair")
        option = ask_number("\nEscolha uma opção: ", 1)

        if option == 0:
            show("\nEncerrando...", CYAN)
            break

        try:
            download_flow(base)
        except (YoutubeDLError, ValueError, OSError) as erro:
            clean()
            header()
            show(format_error(erro), RED)
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        show("\n\nInterrompido pelo usuário.", YELLOW)