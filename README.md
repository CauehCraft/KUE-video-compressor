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
