[English](https://github.com/CauehCraft/KUE-video-compressor#english)
<p align="right"><a href="https://ko-fi.com/cauehcraft"><img src="https://www.buymeacoffee.com/assets/img/BMC-btn-logo.svg" alt="Tip">Donate on Ko-fi</a></p>

# KUE Video Compressor

KUE Video Compressor é um programa de compressão de vídeo que permite aos usuários reduzir o tamanho de seus arquivos de vídeo sem perder muita qualidade. Ele usa o ffmpeg para codificar os vídeos com aceleração de hardware da NVIDIA, AMD ou Intel, dependendo da placa gráfica do usuário.

## Como usar

1. Inicie o programa e arraste e solte um arquivo de vídeo na janela do programa ou clique na janela para selecionar um arquivo de vídeo usando o diálogo de arquivo.

2. Insira o tamanho desejado (em MB) para o arquivo de vídeo comprimido na caixa de texto "Tamanho (MB)".

3. Insira o FPS desejado para o arquivo de vídeo comprimido na caixa de texto "FPS".

4. Insira a resolução desejada (em pixels) para o arquivo de vídeo comprimido na caixa de texto "Resolução (px)".

5. Selecione o codec desejado (h264 ou h265) no menu suspenso "Codec".

6. Se desejar que o áudio seja removido do arquivo de vídeo comprimido, marque a caixa "Mutar vídeo".

7. Clique no botão "Comprimir" para iniciar a compressão do vídeo.

8. O programa exibirá uma animação enquanto o vídeo estiver sendo comprimido e atualizará a porcentagem de progresso em tempo real.

9. Quando a compressão estiver concluída, um novo arquivo de vídeo será criado com o sufixo "_compressed" adicionado ao nome do arquivo original.

## Requisitos

- Windows
- Placa gráfica NVIDIA, AMD ou Intel compatível com codificação de hardware
- Driver da placa gráfica atualizado
- ffmpeg

## Criando o executável

Para criar um executável do programa, você pode usar o PyInstaller. Primeiro, instale as dependências do Pip a partir do arquivo `requirements.txt`:

```
pip install -r requirements.txt
```

Em seguida, execute o comando PyInstaller para criar o executável:

```
pyinstaller --icon=imgs/icon.ico --windowed --add-data "imgs;imgs" --add-data "ffmpeg;ffmpeg" --add-data "tkinterdnd2_path;tkinterdnd2" --onefile main.py
```

Substitua `tkinterdnd2_path` pelo caminho correto para o módulo `tkinterdnd2` em seu sistema.

Você também pode usar o script `auto_build_project.py` fornecido para criar automaticamente o executável:

```python
import sys
import subprocess

# Caminho para o arquivo requirements.txt
requirements_path = "requirements.txt"

# Instalar as dependências do Pip a partir do arquivo requirements.txt
subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path])

# Caminho para o arquivo tkinterdnd2, altere caso necessario.
tkinterdnd2_path = "C:/Users/Caueh/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/site-packages/tkinterdnd2"

# Executar o comando PyInstaller para criar o executável
subprocess.run([
    "pyinstaller",
    "--icon=imgs/icon.ico",
    "--windowed",
    "--add-data", f"imgs;imgs",
    "--add-data", f"ffmpeg;ffmpeg",
    "--add-data", f"{tkinterdnd2_path};tkinterdnd2",
    "--onefile",
    "main.py"
])
```

Certifique-se de alterar `tkinterdnd2_path` para o caminho correto para o módulo `tkinterdnd2` em seu sistema antes de executar este script.


### English
# KUE Video Compressor

KUE Video Compressor is a video compression program that allows users to reduce the size of their video files without losing much quality. It uses ffmpeg to encode videos with hardware acceleration from NVIDIA, AMD or Intel, depending on the user's graphics card.

## How to use

1. Start the program and drag and drop a video file into the program window or click on the window to select a video file using the file dialog.

2. Enter the desired size (in MB) for the compressed video file in the "Size (MB)" text box.

3. Enter the desired FPS for the compressed video file in the "FPS" text box.

4. Enter the desired resolution (in pixels) for the compressed video file in the "Resolution (px)" text box.

5. Select the desired codec (h264 or h265) from the "Codec" dropdown menu.

6. If you want the audio to be removed from the compressed video file, check the "Mute video" box.

7. Click on the "Compress" button to start compressing the video.

8. The program will display an animation while the video is being compressed and update the progress percentage in real time.

9. When compression is complete, a new video file will be created with the suffix "_compressed" added to the original file name.

## Requirements

- Windows
- NVIDIA, AMD or Intel graphics card compatible with hardware encoding
- Updated graphics card driver
- ffmpeg

## Creating the executable

To create an executable of the program, you can use PyInstaller. First, install Pip dependencies from `requirements.txt`:

```
pip install -r requirements.txt
```

Then run the PyInstaller command to create the executable:

```
pyinstaller --icon=imgs/icon.ico --windowed --add-data "imgs;imgs" --add-data "ffmpeg;ffmpeg" --add-data "tkinterdnd2_path;tkinterdnd2" --onefile main.py
```

Replace `tkinterdnd2_path` with the correct path to `tkinterdnd2` module on your system.

You can also use `auto_build_project.py` script provided to automatically create executable:

```python
import sys
import subprocess

# Path to requirements.txt file
requirements_path = "requirements.txt"

# Install Pip dependencies from requirements.txt file
subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path])

# Path to tkinterdnd2 file, change if necessary.
tkinterdnd2_path = "C:/Users/Caueh/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/site-packages/tkinterdnd2"

# Run PyInstaller command to create executable
subprocess.run([
    "pyinstaller",
    "--icon=imgs/icon.ico",
    "--windowed",
    "--add-data", f"imgs;imgs",
    "--add-data", f"ffmpeg;ffmpeg",
    "--add-data", f"{tkinterdnd2_path};tkinterdnd2",
    "--onefile",
    "main.py"
])
```

Make sure to change `tkinterdnd2_path` to correct path for `tkinterdnd2` module on your system before running this script.
