import tkinter as tk
from tkinter import filedialog, ttk
from threading import Thread
from PIL import Image, ImageTk
import os
import tkinterdnd2
import subprocess
import json
import webbrowser
import imageio
import sys
from io import BytesIO
# import time


if hasattr(sys, '_MEIPASS'):
    # Running as packaged executable
    base_path = sys._MEIPASS
else:
    # Running as script
    base_path = os.path.dirname(__file__)

def open_link(event):
    webbrowser.open("https://github.com/cauehcraft")

# função para detectar a marca da GPU
def get_gpu_brand():
    try:
        output = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode("utf-8")
        if "NVIDIA" in output:
            return "NVIDIA"
        elif "AMD" in output or "Radeon" in output:
            return "AMD"
        elif "Intel" in output:
            return "Intel"
        else:
            return None
    except:
        return None
global gpu_brand
gpu_brand = get_gpu_brand()
if (gpu_brand== None):
    tk.messagebox.showerror("Erro", "Não foi detectado nenhuma GPU.")

""" old code
def animate():
    global frame
    frame = (frame + 1) % len(combined_frames)
    photo = ImageTk.PhotoImage(combined_frames[frame])
    processing_label.config(image=photo)
    processing_label.image = photo
    if compress_button["text"] == "Abortar":
        root.after(10, animate)
"""

def compress_video():
    # Executar a função em uma thread separada
    thread = Thread(target=compress_video_thread)
    thread.start()

def abort_compression():
    global compress_process
    compress_process.communicate(input=b'q')

# Função para comprimir o vídeo usando ffmpeg e GPU
def compress_video_thread():
    global compress_process

    # Obter os valores especificados pelo usuário
    target_size = float(size_entry.get())
    target_fps = float(fps_entry.get())
    target_resolution = int(resolution_entry.get())

    # Obter informações sobre o arquivo de vídeo original
    file_path = video_path.get()
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    ffprobe_path = os.path.join(base_path, "ffmpeg", "bin", "ffprobe.exe")
    ffprobe_path = ffprobe_path.replace("\\", "\\\\")
    ffprobe_command = f'"{ffprobe_path}" -v quiet -print_format json -show_format -show_streams "{file_path}"'
    ffprobe_output = subprocess.check_output(ffprobe_command, shell=True)
    ffprobe_data = json.loads(ffprobe_output)
    video_stream = next(stream for stream in ffprobe_data["streams"] if stream["codec_type"] == "video")
    fps = eval(video_stream["avg_frame_rate"])
    height = video_stream["height"]

    # Verificar se os valores especificados pelo usuário são válidos
    if target_size > file_size:
        tk.messagebox.showerror("Erro", "O tamanho especificado é maior que o tamanho do arquivo original")
        compress_button.config(state=tk.NORMAL)
        return
    if target_fps > fps:
        tk.messagebox.showerror("Erro", "O FPS especificado é maior que o FPS do arquivo original")
        compress_button.config(state=tk.NORMAL)
        return
    if target_resolution > height:
        tk.messagebox.showerror("Erro", "A resolução especificada é maior que a resolução do arquivo original")
        compress_button.config(state=tk.NORMAL)
        return
    
    # Alterar o botão Comprimir e Abortar
    abort_button.config(state=tk.NORMAL, cursor="hand2")

    # desabilitando widgets
    compress_button.config(state=tk.DISABLED, cursor="")
    size_entry.config(state=tk.DISABLED)
    fps_entry.config(state=tk.DISABLED)
    resolution_entry.config(state=tk.DISABLED)
    codec_combobox.config(state=tk.DISABLED)
    mute_check.config(state=tk.DISABLED)
    

    # Alterar o label para exibir o GIF
    processing_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    # Label do progresso
    progress_label.grid(row=5, column=0, columnspan=2, sticky='S')
    progress_label.config(text="Iniciando compressão...")

    # Iniciar a animação do GIF (part of an old code)
    global frame
    frame = 0

    # Calcular a taxa de bits alvo com base no tamanho especificado pelo usuário
    duration = float(ffprobe_data["format"]["duration"])
    target_bitrate = (target_size * 8192) / duration

    # Construir o comando ffmpeg para comprimir o vídeo
    ffmpeg_path = os.path.join(base_path, "ffmpeg", "bin", "ffmpeg.exe")
    ffmpeg_path = ffmpeg_path.replace("\\", "\\\\")
    file_path = file_path.replace("\\", "\\\\")
    output_file_path = file_path.rsplit(".", 1)[0] + "_compressed.mp4"
    output_file_path = output_file_path.replace("\\", "\\\\")
    mute_option = "-an" if mute_var.get() else ""
    if gpu_brand == "NVIDIA":
        codec = f"{codec_var.get()}_nvenc"
    elif gpu_brand == "AMD":
        codec = f"{codec_var.get()}_amf"
    elif gpu_brand == "Intel":
        codec = f"{codec_var.get()}_qsv"
    else:
        codec = codec_var.get()
    command = f'"{ffmpeg_path}" -y -loglevel level+debug -i "{file_path}" -c:v {codec} -b:v {target_bitrate:.0f}k -r {target_fps:.2f} -vf "scale=-2:{target_resolution}" {mute_option} "{output_file_path}"'
    
    # Executar o comando ffmpeg para comprimir o vídeo
    # em segundo plano sem exibir uma janela de terminal.
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    compress_process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
    # Ler a saída do ffmpeg em tempo real e calcular a porcentagem de progresso
    counter = 0
    while True:
        if compress_process.poll() is not None:
            # O processo ffmpeg foi encerrado
            break
        line = compress_process.stderr.readline().strip()
        if not line:
            break
        line_str = line.decode("utf-8")
        if "time=" in line_str:
            time_str = line_str.split("time=")[1].split(" ")[0]
            time_parts = time_str.split(":")
            hours, minutes = int(time_parts[0]), int(time_parts[1])
            seconds = float(time_parts[2])
            current_time = hours * 3600 + minutes * 60 + seconds
            progress_percentage = (current_time / duration) * 100

            # Atualizar a interface do usuário com a porcentagem de progresso calculada
            progress_label.config(text=f"Progresso: {progress_percentage:.1f}%")
        
        # Atualizar a animação a cada 5 iterações do loop while
        counter += 1
        if counter % 10 == 0:
            frame = (frame + 1) % len(combined_frames)
            photo = ImageTk.PhotoImage(combined_frames[frame])
            processing_label.config(image=photo)
            processing_label.image = photo

        # Adicionar um atraso para controlar a velocidade da animação (causa bugs, a compressão é interrompida)
        # time.sleep(0.1)

    # Aguardar a conclusão do processo
    compress_process.wait()

    if compress_process.returncode is not None:
        print("O processo foi encerrado")
        # interrupção/finalização do processo

    processing_label.place_forget()
    progress_label.grid(row=5, column=5, columnspan=2, sticky='S')
    compress_button.config(state=tk.NORMAL, cursor="hand2")
    abort_button.config(state=tk.DISABLED, cursor="")
    progress_label.config(text="")
    
    # habilitando widgets
    compress_button.config(state=tk.NORMAL, cursor="hand2")
    size_entry.config(state=tk.NORMAL)
    fps_entry.config(state=tk.NORMAL)
    resolution_entry.config(state=tk.NORMAL)
    codec_combobox.config(state=tk.NORMAL)
    mute_check.config(state=tk.NORMAL)


def select_video(event):
    # Função para selecionar o vídeo usando filedialog
    file_path = filedialog.askopenfilename(filetypes=[("Arquivos de Vídeo", "*.mp4;*.avi;*.mov;*.flv")])
    if file_path:
        video_path.set(file_path)
        update_thumbnail(file_path)

def drop_video(event):
    # Função para lidar com o evento de soltar um arquivo de vídeo na janela do programa
    if event.data:
        file_path = event.data.strip("{}")
        video_path.set(file_path)
        update_thumbnail(file_path)
        return event.action

def update_thumbnail(file_path):
    # Função para atualizar a miniatura do vídeo
    try:
        # Verificar se o arquivo é um arquivo de vídeo válido
        if not file_path.lower().endswith((".mp4", ".avi", ".mov", ".flv")):
            raise Exception("Arquivo inválido")
        # Gerar a miniatura do vídeo usando ffmpeg (substitua pelo comando correto para gerar a miniatura)
        ffmpeg_path = os.path.join(base_path, "ffmpeg", "bin", "ffmpeg.exe")
        ffmpeg_path = ffmpeg_path.replace("\\", "\\\\")
        file_path = file_path.replace("\\", "\\\\")
        command = f'"{ffmpeg_path}" -y -i "{file_path}" -ss 00:00:01.000 -vframes 1 -f image2pipe -'
        thumbnail_data = subprocess.check_output(command, shell=True)

        # Carregar e exibir a miniatura do vídeo
        # image = Image.open("thumbnail.jpg")
        image = Image.open(BytesIO(thumbnail_data))
        image = image.convert("RGBA")
        image.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(image)
        thumbnail_label.config(image=photo)
        thumbnail_label.image = photo

        # Carregar o GIF
        gif = imageio.mimread(base_path+'/imgs/carregando.gif')

        # Criar uma lista para armazenar os quadros combinados
        global combined_frames
        combined_frames = []
        
        # Combinar cada quadro do GIF com a miniatura do vídeo
        try:
            for i, frame in enumerate(gif):
                frame_image = Image.fromarray(frame)
                frame_image = frame_image.resize(image.size)
                if (i!=0):
                    combined_frame = Image.alpha_composite(image, frame_image)
                    combined_frames.append(combined_frame)
        except Exception as e:
            print("DEU ERRO:")
            print(e)

        # Obter e exibir o tamanho do arquivo de vídeo
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        size_entry.delete(0, tk.END)
        size_entry.insert(0, f"{file_size:.2f}")

        # Obter e exibir informações sobre o FPS e a resolução do arquivo de vídeo
        ffprobe_path = os.path.join(base_path, "ffmpeg", "bin", "ffprobe.exe")
        ffprobe_path = ffprobe_path.replace("\\", "\\\\")
        ffprobe_command = f'"{ffprobe_path}" -v quiet -print_format json -show_streams "{file_path}"'
        ffprobe_output = subprocess.check_output(ffprobe_command, shell=True)
        ffprobe_data = json.loads(ffprobe_output)

        video_stream = next(stream for stream in ffprobe_data["streams"] if stream["codec_type"] == "video")
        fps = eval(video_stream["avg_frame_rate"])
        height = video_stream["height"]

        fps_entry.delete(0, tk.END)
        fps_entry.insert(0, f"{fps:.2f}")
        resolution_entry.delete(0, tk.END)
        resolution_entry.insert(0, f"{height}")

        # Habilitar o botão Comprimir e desabilitar o de abortar
        compress_button.config(state=tk.NORMAL, cursor="hand2")
        abort_button.config(state=tk.DISABLED, cursor="")

    except:
        # Carregar e exibir a imagem de erro
        image = Image.open(base_path+"/imgs/thumb_error.jpeg")

        # Desabilitar o botão Iniciar
        compress_button.config(state=tk.DISABLED, cursor="")
        abort_button.config(state=tk.DISABLED, cursor="")

    image.thumbnail((300, 300))
    photo = ImageTk.PhotoImage(image)
    thumbnail_label.config(image=photo)
    thumbnail_label.image = photo



root = tkinterdnd2.TkinterDnD.Tk()
root.title("KUE Video Compressor")
root.geometry("307x400")
root.resizable(False, False)
root.configure(bg="#101130")
root.iconbitmap(base_path+'/imgs/icon.ico')


# Variável para armazenar o caminho do vídeo selecionado
video_path = tk.StringVar()

# Caixa para arrastar ou selecionar o vídeo
drop_frame = tk.LabelFrame(root, text="Arraste ou selecione o vídeo aqui", height=300, width=300, background="#101130")
drop_frame.grid(row=0, column=0, columnspan=2)
drop_frame.drop_target_register(tkinterdnd2.DND_FILES)
drop_frame.dnd_bind("<<Drop>>", drop_video)
drop_frame.bind("<Button-1>", select_video)

# Label para exibir a miniatura do vídeo
thumbnail_label = ttk.Label(drop_frame)
thumbnail_label.pack()

# Criar o label para exibir o GIF
processing_label = tk.Label(thumbnail_label)

# Caixas de texto para inserir atributos do vídeo
size_label = ttk.Label(root, text="Tamanho (MB):")
size_label.grid(row=1, column=0, sticky='E', pady=(3, 3))
size_entry = ttk.Entry(root)
size_entry.config(justify='left')
size_entry.grid(row=1, column=1, sticky='W')

fps_label = ttk.Label(root, text="FPS:")
fps_label.grid(row=2, column=0, sticky='E')
fps_entry = ttk.Entry(root)
fps_entry.config(justify='left')
fps_entry.grid(row=2, column=1, sticky='W')

resolution_label = ttk.Label(root, text="Resolução (px):")
resolution_label.grid(row=3, column=0, sticky='E', pady=(3, 3))
resolution_entry = ttk.Entry(root)
resolution_entry.config(justify='left')
resolution_entry.grid(row=3, column=1, sticky='W')

# Checkbox para mutar o vídeo
mute_var = tk.BooleanVar()
mute_check = tk.Checkbutton(root, text="Mutar vídeo", variable=mute_var, background="#101130", highlightbackground="#101130", cursor="hand2")
mute_check.grid(row=5, column=0, columnspan=2)

# Menu suspenso para seleção de codec
codec_var = tk.StringVar(value="h264")
codec_label = ttk.Label(root, text="Codec:")
codec_label.grid(row=4, column=0, sticky='E', pady=(3, 3))
codec_combobox = ttk.Combobox(root, textvariable=codec_var, values=["h264", "hevc"], state="readonly")
codec_combobox.grid(row=4, column=1, sticky='W')

# Botão para comprimir o vídeo
compress_button = tk.Button(root, text="Comprimir", command=compress_video, 
                            bg="#252670", 
                            activebackground="#252670", 
                            fg="white", 
                            activeforeground="white", 
                            height=1, 
                            width=10,
                            font=("Helvetica", 16))
compress_button.grid(row=6, column=0, padx=(10, 5), pady=(10, 10), sticky='EW')
compress_button.config(state=tk.DISABLED)

# Botão para Abortar a compressão do vídeo
abort_button = tk.Button(root, text="Abortar", command=abort_compression, 
                            bg="#a10f0f", 
                            activebackground="#a10f0f", 
                            fg="white", 
                            activeforeground="white", 
                            height=1, 
                            width=10,
                            font=("Helvetica", 16))
abort_button.grid(row=6, column=1, padx=(5, 10), pady=(10, 10), sticky='EW')
abort_button.config(state=tk.DISABLED)


# Carregar e exibir a imagem padrão na inicialização do programa
image = Image.open(base_path+"/imgs/thumb_sample.jpeg")
image.thumbnail((300, 300))
photo = ImageTk.PhotoImage(image)
thumbnail_label.config(image=photo)
thumbnail_label.image = photo

# Barra de progresso
progress_label = tk.Label(root, background="#101130", font=("Helvetica", 10))


# Footer com link github
footer_label = tk.Label(root, text="v0.1b - @CauehCraft", cursor="hand2", background="#101130")
footer_label.grid(row=7, column=0, columnspan=2, sticky='S')
footer_label.bind("<Button-1>", open_link)

# Definindo estilo
style = ttk.Style()
style.configure("TButton", background="#3f47cc", borderwidth=1)
style.configure("TEntry", background="#101130", borderwidth=1)
style.configure("TLabel", background="#101130", borderwidth=1)
style.configure("TCombobox", background="#101130", borderwidth=1)
size_label.config(foreground="white")
drop_frame.config(foreground="white")
fps_label.config(foreground="white")
resolution_label.config(foreground="white")
mute_check.config(foreground="white", selectcolor="#101130")
compress_button.config(foreground="white")
abort_button.config(foreground="white")
progress_label.config(foreground="white")
codec_label.config(foreground="white")
footer_label.config(foreground="white")

def validate_float_input(new_value):
    # Função para validar a entrada numérica com ponto decimal
    return new_value.replace(".", "", 1).isdecimal() or new_value == ""

def validate_int_input(new_value):
    # Função para validar a entrada numérica inteira
    return new_value.isdecimal() or new_value == ""

validate_float_command = root.register(validate_float_input)
validate_int_command = root.register(validate_int_input)

size_entry.config(validate="key", validatecommand=(validate_float_command, "%P"))
fps_entry.config(validate="key", validatecommand=(validate_float_command, "%P"))
resolution_entry.config(validate="key", validatecommand=(validate_int_command, "%P"))

root.mainloop()