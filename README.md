<p align="center">
  <img src="assets/youtube-downloader-pixel-icon.png" width="350" alt="YouTube Downloader"/>
</p>

<p align="center">
  <img src="assets/pixelarttitle.png"
       alt="YouTube Downloader"
       width="700"/>
</p>

<p align="center">
  Um downloader de vídeos e áudios do YouTube desenvolvido em Python,
  com interface via terminal e suporte à conversão de áudio para MP3.
</p>

**Versão:** 1.0.0

## Funcionalidades

- Download de vídeos em MP4.
- Download de áudio em MP3.
- Seleção da qualidade de vídeo disponível.
- Seleção do bitrate do áudio (128, 192, 256 e 320 kbps).
- Exibição de informações do vídeo antes do download.
- Verificação de arquivos existentes para evitar downloads duplicados.
- Tratamento de erros durante a análise e o download.
- Organização dos arquivos baixados em uma pasta `downloads`.

## Tecnologias utilizadas

<p align="left">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40" height="40" alt="Python" title="Python" style="display:inline-block; vertical-align:middle;"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nodejs/nodejs-original.svg" width="40" height="40" alt="Node.js" title="Node.js" style="display:inline-block; vertical-align:middle;"/>
  <img src="https://cdn.simpleicons.org/ffmpeg/007808" width="40" height="40" alt="FFmpeg" title="FFmpeg" style="display:inline-block; vertical-align:middle;"/>
</p>

- **Python:** lógica principal e interface da aplicação.
- **yt-dlp:** extração de informações e download de conteúdo.
- **Node.js:** execução de JavaScript para auxiliar na extração de conteúdo.
- **FFmpeg:** processamento, mesclagem e conversão de mídia.

## Estrutura do projeto

```text
youtube-downloader/
├── downloads/
├── main.py
├── requirements.txt
├── .gitignore
├── config.conf
└── README.md
```

## Requisitos

Antes de executar o projeto, instale:

- **Python 3:** ambiente de execução da aplicação.
- **Node.js:** runtime JavaScript utilizado pelo yt-dlp.
- **FFmpeg:** ferramenta utilizada para processamento e conversão de mídia.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/brunolucas2/youtube-downloader.git
cd youtube-downloader
```

Instale as dependências do Python:

```bash
pip install -r requirements.txt
```

Verifique se as ferramentas estão instaladas:

```bash
python --version
node --version
ffmpeg -version
```

## Instalação do FFmpeg

O FFmpeg é necessário para mesclar áudio e vídeo e extrair áudio no formato MP3.

### Windows

Abra o PowerShell e execute:

```powershell
winget install Gyan.FFmpeg
```

Alternativamente, utilizando Chocolatey:

```powershell
choco install ffmpeg
```

Após a instalação, reinicie o terminal.

### Linux

Escolha o comando correspondente à sua distribuição.

**Debian / Ubuntu / Kali Linux**

```bash
sudo apt update
sudo apt install ffmpeg
```

**Arch Linux / Manjaro**

```bash
sudo pacman -S ffmpeg
```

**Fedora**

```bash
sudo dnf install ffmpeg
```

### Verificação

Para confirmar a instalação, execute:

```bash
ffmpeg -version
```

Se o terminal reconhecer o comando e exibir as informações da versão, a instalação foi concluída.

**Observação:** O `ffprobe`, utilizado para analisar arquivos de mídia, normalmente é instalado junto com o FFmpeg.

## Como usar

Execute o programa na pasta do projeto:

```bash
python main.py
```

No Linux, caso necessário:

```bash
python3 main.py
```

Siga as instruções apresentadas no terminal:

1. Informe a URL do vídeo do YouTube.
2. Escolha entre baixar em MP4 ou MP3.
3. Selecione a qualidade desejada.
4. Caso escolha MP3, selecione o bitrate.
5. Aguarde a conclusão do download.

Os arquivos serão salvos automaticamente na pasta `downloads`.

## Aviso

Utilize esta ferramenta apenas para baixar conteúdos que você tem autorização para baixar, respeitando os direitos autorais e os termos de serviço do YouTube.

## Versão

**v1.0.0** — Primeira versão do YouTube Downloader.