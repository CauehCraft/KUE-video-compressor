| [English](#english) | [Donate on Ko-fi](https://ko-fi.com/cauehcraft) |
|:---------------------------|--------------------------:|

# KUE Video-Editor Colection

KUE-VEC é um programa de corte e compressão de vídeo que permite aos usuários reduzir o tamanho de seus arquivos de vídeo e corta-los sem perder muita qualidade. Ele usa o ffmpeg para codificar os vídeos com aceleração de hardware da NVIDIA, AMD ou Intel, dependendo da placa gráfica do usuário.

## Índice

- [KUE VEC](#kue-video-editor-colection)
- [Como usar](#como-usar)
- [Requisitos](#requisitos)
- [Criando o executável](#criando-o-executável)

## Como usar

- #### Cortar videos

  Execute o programa e clique na aba `Cortar Video`.

  1. Arraste e solte um arquivo de vídeo na janela do programa ou clique no botão de `Select video` para selecionar um arquivo de vídeo usando o diálogo de arquivo.

  2. Utilize os sliders para controlar o tempo do video e os marcadores de corte.

  3. Clique no botão `Cortar` para iniciar o processo de corte do vídeo.

  4. A barra de progresso no canto inferior esquerdo irá mostrar o progresso do corte no video.

  5. Quando o processo de corte estiver concluído, um novo arquivo de vídeo será criado com o sufixo "_kueclip" adicionado ao nome do arquivo original.

- #### Compressão de video

  Execute o programa e clique na aba `Comprimir Video`.

  1. Arraste e solte um arquivo de vídeo na janela do programa ou clique na janela para selecionar um arquivo de vídeo usando o diálogo de arquivo.

  2. Insira o tamanho desejado (em MB) para o arquivo de vídeo comprimido na caixa de texto "Tamanho (MB)".

  3. Insira o FPS desejado para o arquivo de vídeo comprimido na caixa de texto "FPS".

  4. Insira a resolução desejada (em pixels) para o arquivo de vídeo comprimido na caixa de texto "Resolução (px)".

  5. Selecione o codec desejado (h264 ou h265) no menu suspenso "Codec".

  6. Se desejar que o áudio seja removido do arquivo de vídeo comprimido, marque a caixa "Mutar vídeo".

  7. Clique no botão "Comprimir" para iniciar a compressão do vídeo.

  8. O programa exibirá uma animação enquanto o vídeo estiver sendo comprimido e atualizará a porcentagem de progresso em tempo real.

  9. Quando a compressão estiver concluída, um novo arquivo de vídeo será criado com o sufixo "_comp" adicionado ao nome do arquivo original.



## Requisitos

- Windows
- (Opcional) Placa gráfica NVIDIA, AMD ou Intel compatível com codificação de hardware
- ffmpeg

## Criando o executável

Para criar um executável do programa, você pode usar o script `auto_build_project.py` fornecido para criar automaticamente o executável:

```python
import sys
import subprocess

def get_package_location(package_name):
    result = subprocess.run([sys.executable, "-m", "pip", "show", package_name], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    for line in output.split('\n'):
        if line.startswith('Location:'):
            return line.split()[-1]
    return None

# Caminho para o arquivo requirements.txt
requirements_path = "requirements.txt"

# Instalar as dependências do Pip a partir do arquivo requirements.txt
subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path])

# Obter o caminho de instalação das bibliotecas tkinterdnd2 e customtkinter
tkinterdnd2_path = get_package_location("tkinterdnd2")+"\\tkinterdnd2"
customtkinter_path = get_package_location("customtkinter")+"\\customtkinter"

# Executar o comando PyInstaller para criar o executável
subprocess.run([
    "pyinstaller",
    "--icon=imgs/icon.ico",
    "--windowed",
    "--add-data", f"imgs;imgs",
    "--add-data", f"ffmpeg;ffmpeg",
    "--add-data", f"{tkinterdnd2_path};tkinterdnd2",
    "--add-data", f"{customtkinter_path};customtkinter/",
    "KUE-VEC.py"
])
```


###### English:
# KUE Video-Editor Colection

KUE-VEC is a video cutting and compression program that allows users to reduce the size of their video files and cut them without losing much quality. It uses ffmpeg to encode videos with NVIDIA, AMD or Intel hardware acceleration, depending on the user’s graphics card.

## Table of Contents

- [KUE VEC](#kue-video-editor-colection)
- [How to use](#how-to-use)
- [Requirements](#requirements)
- [Creating the executable](#creating-the-executable)

## How to use

- #### Cutting videos

  Run the program and click on the `Cut Video` tab.

  1. Drag and drop a video file into the program window or click on the `Select video` button to select a video file using the file dialog.

  2. Use the sliders to control the video time and cut markers.

  3. Click on the `Cut` button to start the video cutting process.

  4. The progress bar in the lower left corner will show the progress of cutting the video.

  5. When the cutting process is complete, a new video file will be created with the suffix "_kueclip" added to the original file name.

- #### Video compression

  Run the program and click on the `Compress Video` tab.

  1. Drag and drop a video file into the program window or click on the window to select a video file using the file dialog.

  2. Enter the desired size (in MB) for the compressed video file in the "Size (MB)" text box.

  3. Enter the desired FPS for the compressed video file in the "FPS" text box.

  4. Enter the desired resolution (in pixels) for the compressed video file in the "Resolution (px)" text box.

  5. Select the desired codec (h264 or h265) from the "Codec" drop-down menu.

  6. If you want audio to be removed from the compressed video file, check the "Mute video" box.

  7. Click on "Compress" button to start compressing video.

  8. The program will display an animation while compressing video and update progress percentage in real time.

  9. When compression is complete, a new video file will be created with "_comp" suffix added to original file name.

## Requirements

- Windows
- (Optional) NVIDIA, AMD or Intel graphics card compatible with hardware encoding
- ffmpeg

## Creating executable
To create an executable of program, you can use provided `auto_build_project.py` script to automatically create executable:

```python
import sys
import subprocess

def get_package_location(package_name):
    result = subprocess.run([sys.executable, "-m", "pip", "show", package_name], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    for line in output.split('\n'):
        if line.startswith('Location:'):
            return line.split()[-1]
    return None

# Caminho para o arquivo requirements.txt
requirements_path = "requirements.txt"

# Instalar as dependências do Pip a partir do arquivo requirements.txt
subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path])

# Obter o caminho de instalação das bibliotecas tkinterdnd2 e customtkinter
tkinterdnd2_path = get_package_location("tkinterdnd2")+"\\tkinterdnd2"
customtkinter_path = get_package_location("customtkinter")+"\\customtkinter"

print(tkinterdnd2_path)
print(customtkinter_path)

# Executar o comando PyInstaller para criar o executável
subprocess.run([
    "pyinstaller",
    "--icon=imgs/icon.ico",
    "--windowed",
    "--add-data", f"imgs;imgs",
    "--add-data", f"ffmpeg;ffmpeg",
    "--add-data", f"{tkinterdnd2_path};tkinterdnd2",
    "--add-data", f"{customtkinter_path};customtkinter/",
    "KUE-VEC.py"
])
```
