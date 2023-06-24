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
