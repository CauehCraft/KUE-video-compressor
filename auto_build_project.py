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