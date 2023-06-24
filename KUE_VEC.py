import subprocess, os, json, imageio, sys, vlc, requests, tkinterdnd2
import customtkinter as ctk
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_ALL
from tkinter import filedialog
from datetime import timedelta
from threading import Thread
from tkinterdnd2 import *
from io import BytesIO
from PIL import Image
from send2trash import send2trash


class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


# global
player = None
is_playing = False
comp_file_path = None
cut_file_path = None
settings = None
twostep = None

check_url = "https://raw.githubusercontent.com/CauehCraft/KUE-video-compressor/main/check"
current_version = "1.000"
def check_for_updates():
    try:
        response = requests.get(check_url)
        data = response.json()
        latest_version = data["version"]
        download_url = data["download_url"]
        if float(latest_version) > float(current_version):
            answer = tk.messagebox.askyesno("Atualização disponível", f"Uma nova versão do aplicativo está disponível: {latest_version}. Deseja baixá-la agora?")
            if answer:
                os.startfile(download_url)
   
    except Exception as e:
        tk.messagebox.showerror("Erro", f"Não foi possível verificar se há atualizações: {e}")
check_for_updates()

if hasattr(sys, '_MEIPASS'):
    # Running as packaged executable
    base_path = sys._MEIPASS
else:
    # Running as script
    base_path = os.path.dirname(__file__)

def get_trash_path(trash_file_path):
    trash_path = trash_file_path.replace("/", "\\")
    return trash_path

# --                    -- #
# --- CUTTER FUNCTIONS --- # 
# --                    -- #

def cut_select_video():
    global player, is_playing, cut_file_path
    if player:
        player.stop()
    cut_file_path = filedialog.askopenfilename(filetypes=[("Arquivos de Vídeo", "*.mp4;*.avi;*.mov;*.flv")])
    if cut_file_path:
        if not cut_file_path.lower().endswith((".mp4", ".avi", ".mov", ".flv")):
            tk.messagebox.showerror("Erro", "Arquivo inválido")
            return
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(cut_file_path)
        player.set_media(media)
        player.set_hwnd(video_label.winfo_id())
        player.play()
        update_time_slider()
        is_playing = True
        play_pause_button.configure(text="Pause", fg_color="darkblue", state=ctk.NORMAL)
        cut_button.configure(state=ctk.NORMAL)
        while player.get_length() == 0:
            continue
        duration = player.get_length()
        time_slider.configure(to=duration)
        cut_start_slider.configure(to=duration)
        cut_end_slider.configure(to=duration)
        cut_end_slider.set(duration)

def on_time_slider_change(value):
    global player
    cut_start = cut_start_slider.get()
    cut_end = cut_end_slider.get()
    if value < cut_start:
        value = cut_start
    if value > cut_end:
        value = cut_end
    time_slider.set(value)
    if player.get_state() == vlc.State.Ended:
        player.stop()
        player.play()
        player.pause()
    player.set_time(int(value))

def on_cut_start_slider_change(value):
    cut_start = int(value)
    cut_end = cut_end_slider.get()
    if cut_start > cut_end:
        cut_end_slider.set(cut_start)
    time_slider.set(cut_start)
    on_time_slider_change(cut_start)

def on_cut_end_slider_change(value):
    cut_end = int(value)
    cut_start = cut_start_slider.get()
    if cut_end < cut_start:
        cut_start_slider.set(cut_end)
    time_slider.set(cut_end)
    on_time_slider_change(cut_end)

def format_time(milliseconds):
    td = timedelta(milliseconds=milliseconds)
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}:{milliseconds % 1000:02d}"

def update_time_slider():
    global player, is_playing
    current_time = player.get_time()
    cut_end = cut_end_slider.get()
    if current_time > cut_end and is_playing:
        player.pause()
        is_playing = False
        play_pause_button.configure(text="Play", fg_color="blue")
    time_slider.set(current_time)
    current_time_var.set(f"{format_time(current_time)}")
    root.after(250, update_time_slider)

def on_play_pause_button_click():
    global player, is_playing
    if is_playing:
        player.pause()
        play_pause_button.configure(text="Play", fg_color="blue")
    else:
        player.play()
        play_pause_button.configure(text="Pause", fg_color="blue")
    is_playing = not is_playing

def on_drop(event):
    global player, is_playing, cut_file_path
    if event.data:
        cut_file_path = event.data.strip("{}")
        if not cut_file_path.lower().endswith((".mp4", ".avi", ".mov", ".flv")):
            tk.messagebox.showerror("Erro", "Arquivo inválido")
            return
        if player:
            if player.get_state() == vlc.State.Playing:
                player.pause()
                is_playing = False
                play_pause_button.configure(text="Play", fg_color="blue")

        if cut_file_path:
            instance = vlc.Instance()
            media = instance.media_new(cut_file_path)
            if not player:
                player = instance.media_player_new()
            player.set_media(media)
            player.set_hwnd(video_label.winfo_id())
            player.play()
            update_time_slider()
            is_playing = True
            play_pause_button.configure(text="Pause", fg_color="darkblue", state=ctk.NORMAL)
            cut_button.configure(state=ctk.NORMAL)
            time_slider.configure(state=ctk.NORMAL)
            cut_end_slider.configure(state=ctk.NORMAL)
            cut_start_slider.configure(state=ctk.NORMAL)
            
            while player.get_length() == 0:
                continue
            duration = player.get_length()
            time_slider.configure(to=duration)
            cut_start_slider.configure(to=duration)
            cut_end_slider.configure(to=duration)
            cut_end_slider.set(duration)
    return event.action

def on_cut_button_click():
    cutthread = Thread(target=cut_video_thread)
    cutthread.start()

def on_cut_abort_button_click():
    global cut_process
    cut_process.stdin.write(b'q')
    cut_process.stdin.flush()



def cut_video_thread():
    global cut_file_path
    cut_button.configure(state=ctk.DISABLED)
    cut_abort.configure(state=ctk.NORMAL)
    if cut_file_path:
        cut_start = cut_start_slider.get()/1000
        cut_end = cut_end_slider.get()/1000
        cut_duration = cut_end - cut_start

        input_file = cut_file_path
        input_filename, input_extension = os.path.splitext(input_file)
        output_file = f"{input_filename}_kueclip{input_extension}"
        ffprobe_command = ["ffmpeg\\bin\\ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file]
        result = subprocess.run(ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        input_duration = float(result.stdout)
        if cut_start < 0 or cut_start > input_duration:
            tk.messagebox.showerror("Erro", f"cut_start {cut_start} está fora do intervalo válido [0, {input_duration}]")
            return
        if cut_duration < 0:
            tk.messagebox.showerror("Erro", f"cut_duration {cut_duration} está fora do intervalo válido [0, {input_duration - cut_start}]")
            return
        if cut_duration > input_duration - cut_start:
            cut_duration = input_duration - cut_start
            
        gpu_var = tk.BooleanVar(value=True)
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                gpu_var.set(config["use_gpu"])
        except:
            pass
        if gpu_var.get():
            gpu = get_gpu_brand()
            if gpu == "NVIDIA":
                codec = "h264_nvenc"
            elif gpu == "AMD":
                codec = "h264_amf"
            elif gpu == "Intel":
                codec = "h264_qsv"
            else:
                codec = 'libx264'
        else:
            codec = 'libx264'

        ffprobe_command = f'"ffmpeg\\bin\\ffprobe" -v error -show_entries format=bit_rate -of default=noprint_wrappers=1:nokey=1 "{input_file}"'
        input_bitrate = subprocess.check_output(ffprobe_command, shell=True).decode("utf-8").strip()
        target_bitrate = float(input_bitrate) * 1

        ffmpeg_command = ["ffmpeg\\bin\\ffmpeg", "-y", "-loglevel", "level+debug", "-i", input_file, "-ss", str(cut_start), "-t", str(cut_duration), "-c:v", codec, "-b:v", f"{target_bitrate:.0f}", "-filter_complex", "[0:v]setpts=PTS-STARTPTS[v];[0:a]asetpts=PTS-STARTPTS[a]", "-map", "[v]", "-map", "[a]", output_file]

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        global cut_process
        cut_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)

        while True:
            
            if cut_process.poll() is not None:
                break
            line = cut_process.stderr.readline().strip()
            if not line:
                break
            line_str = line.decode("utf-8")
            if "time=" in line_str:
                time_str = line_str.split("time=")[1].split(" ")[0]
                time_parts = time_str.split(":")
                hours, minutes = int(time_parts[0]), int(time_parts[1])
                seconds = float(time_parts[2])
                current_time = hours * 3600 + minutes * 60 + seconds
                progress_percentage = (current_time / cut_duration)
                cut_progress_label.set(progress_percentage)
    cut_process.wait()

    if cut_process.returncode is not None:
        print("O processo de corte foi encerrado")
        if tk.messagebox.askyesno("Apagar vídeo", "Deseja apagar o vídeo original?"):
            player.stop()
            send2trash(get_trash_path(cut_file_path))
        if tk.messagebox.askyesno("Comprimir vídeo", "Deseja comprimir o vídeo cortado?"):
            sendto_compress(output_file)
            comp_button_event()
    cut_button.configure(state=ctk.NORMAL)
    cut_abort.configure(state=ctk.DISABLED)
    time_slider.configure(state=ctk.NORMAL)
    cut_end_slider.configure(state=ctk.NORMAL)
    cut_start_slider.configure(state=ctk.NORMAL)

def sendto_compress(output_file):
    comp_button_event()
    video_path.set(output_file)
    update_thumbnail(output_file)
    


# --                          -- #
# ---      SETTINGS DEF      --- # 
# --                          -- #

def on_settings_close():
    global settings
    save_settings()
    on_theme_change()
    settings.destroy()
    settings = None

def open_settings(event):
    global settings
    if settings is None:
        settings = ctk.CTk()
        settings.title("Settings - KUE Video Compressor")
        settings.resizable(False, False)
        settings.geometry("300x270")
        settings.iconbitmap(base_path+'/imgs/icon.ico')
        settings.tabview = ctk.CTkTabview(settings, width=270)
        settings.tabview.grid(row=0, column=0, padx=(15, 15), pady=(10, 10), sticky="nsew")
        settings.tabview.add("Configurações")
        settings.tabview.add("Informações")
        
        description_label = ctk.CTkLabel(settings.tabview.tab("Configurações"), text="Opções disponiveis:")
        description_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='NSEW')
        
        theme_label = ctk.CTkLabel(settings.tabview.tab("Configurações"), text="Tema: ")
        theme_label.grid(row=1, column=0, sticky='E', pady=(3, 3))
        global theme_var
        theme_var = tk.StringVar(value="Dark")
        theme_combobox = ctk.CTkOptionMenu(settings.tabview.tab("Configurações"), variable=theme_var, values=["System", "Dark", "Light"], state="readonly", width=90, command=on_theme_change)
        theme_combobox.set("System")
        theme_combobox.grid(row=1, column=1, sticky='W')

        highlight_color_label = ctk.CTkLabel(settings.tabview.tab("Configurações"), text="Cor de destaque: ")
        highlight_color_label.grid(row=2, column=0, sticky='E', pady=(3, 3))
        global highlight_color_var
        highlight_color_var = tk.StringVar(value="blue")
        highlight_color_combobox = ctk.CTkOptionMenu(settings.tabview.tab("Configurações"), variable=highlight_color_var, values=["blue", "dark-blue", "green"], state="readonly", width=90, command=on_theme_change)
        highlight_color_combobox.set("blue")
        highlight_color_combobox.grid(row=2, column=1, sticky='W')
        
        global gpu_var
        gpu_var = tk.BooleanVar(value=True)
        gpu_switch = ctk.CTkSwitch(settings.tabview.tab("Configurações"), text="Usar GPU", variable=gpu_var, cursor="hand2", onvalue=True, offvalue=False)
        gpu_switch.grid(row=3, column=0, columnspan=2)

        two_step_switch = ctk.CTkSwitch(settings.tabview.tab("Configurações"), text="2-step compress", variable=two_step_var, cursor="hand2", onvalue=True, offvalue=False)
        two_step_switch.grid(row=4, column=0, columnspan=2)
        
        
        save_button = ctk.CTkButton(settings.tabview.tab("Configurações"), text="Salvar", command=on_settings_close, height=30, width=120,)
        save_button.grid(row=5, column=0, columnspan=2, pady=(10, 0))

        load_settings()

        info_text = "KUE Video Compressor\nVersão: 0.2 Beta\nAutor: Caueh O.\nData de lançamento: TBD\n"
        info_label = ctk.CTkLabel(settings.tabview.tab("Informações"), text=info_text)
        info_label.grid(row=0, column=0, columnspan=2, pady=(10, 10), sticky='NSEW')

        settings.tabview.tab("Configurações").grid_columnconfigure(0, weight=1)
        settings.tabview.tab("Configurações").grid_columnconfigure(1, weight=1)
        settings.tabview.tab("Informações").grid_columnconfigure(0, weight=1)
        settings.tabview.tab("Informações").grid_columnconfigure(1, weight=1)
        
        settings.protocol("WM_DELETE_WINDOW", on_settings_close)
        settings.mainloop()
    else:
        settings.deiconify()
        settings.lift()



# --                       -- #
# ---    NAV FUNCTIONS    --- # 
# --                       -- #


def home_button_event():
    comp_nav_button.configure(fg_color="transparent")
    cut_nav_button.configure(fg_color="transparent")
    home_nav_button.configure(fg_color=("gray75", "gray25"))
    config_nav_button.configure(fg_color="transparent")
    video_frame.pack_forget()
    slider_frame.pack_forget()
    button_frame.pack_forget()
    app_frame.pack_forget()
    comp_video_frame.pack_forget()
    bottom_options_frame.pack_forget()
    home_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

def cut_button_event():
    comp_nav_button.configure(fg_color="transparent")
    cut_nav_button.configure(fg_color=("gray75", "gray25"))
    home_nav_button.configure(fg_color="transparent")
    config_nav_button.configure(fg_color="transparent")
    video_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
    button_frame.pack(side="bottom", fill=ctk.X)
    slider_frame.pack(side="bottom", fill=ctk.X)
    app_frame.pack_forget()
    comp_video_frame.pack_forget()
    bottom_options_frame.pack_forget()
    home_frame.pack_forget()

def comp_button_event():
    comp_nav_button.configure(fg_color=("gray75", "gray25"))
    cut_nav_button.configure(fg_color="transparent")
    home_nav_button.configure(fg_color="transparent")
    config_nav_button.configure(fg_color="transparent")
    video_frame.pack_forget()
    slider_frame.pack_forget()
    button_frame.pack_forget()
    bottom_options_frame.pack(padx=10,fill="both", side="bottom", expand=True)
    app_frame.pack(padx=10, fill="both", side="bottom", expand=True)
    comp_video_frame.pack(pady=10, padx=10, side="top", fill="both", expand=True)
    home_frame.pack_forget()
    
    

# --                            -- #
# ---    COMPRESS FUNCTIONS    --- # 
# --                            -- #

def on_theme_change(*args):
    ctk.set_default_color_theme(highlight_color_var.get())
    ctk.set_appearance_mode(theme_var.get())

def load_settings(*args):
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            gpu_var.set(config["use_gpu"])
            theme_var.set(config["theme"])
            highlight_color_var.set(config["color"])
            two_step_var.set(config["two_step_compress"])
    except:
        pass

def save_settings():
    with open("config.json", "w") as f:
        json.dump({"use_gpu": gpu_var.get(), "theme": theme_var.get(), "color": highlight_color_var.get(), "two_step_compress": two_step_var.get()}, f)

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

def compress_video():
    thread = Thread(target=compress_video_thread)
    thread.start()

def abort_compression():
    global compress_process
    compress_process.communicate(input=b'q')


def compress_video_thread():
    global compress_process, comp_file_path, twostep

    comp_file_path = video_path.get()
    file_size = os.path.getsize(comp_file_path) / (1024 * 1024)
    ffprobe_path = os.path.join(base_path, "ffmpeg", "bin", "ffprobe.exe")
    ffprobe_path = ffprobe_path.replace("\\", "\\\\")
    ffprobe_command = f'"{ffprobe_path}" -v quiet -print_format json -show_format -show_streams "{comp_file_path}"'
    ffprobe_output = subprocess.check_output(ffprobe_command, shell=True)
    ffprobe_data = json.loads(ffprobe_output)
    video_stream = next(stream for stream in ffprobe_data["streams"] if stream["codec_type"] == "video")
    fps = eval(video_stream["avg_frame_rate"])
    height = video_stream["height"]

    if (size_entry.get() == ""):
        target_size = file_size
    else:
        target_size = float(size_entry.get())
    if (fps_entry.get() == ""):
        target_fps = fps
    else:
        target_fps = float(fps_entry.get())
    if (resolution_entry.get() == ""):
        target_resolution = height
    else:
        target_resolution = int(resolution_entry.get())

    if target_size > file_size:
        tk.messagebox.showerror("Erro", "O tamanho especificado é maior que o tamanho do arquivo original")
        compress_button.configure(state=tk.NORMAL)
        return
    if target_fps > fps:
        tk.messagebox.showerror("Erro", "O FPS especificado é maior que o FPS do arquivo original")
        compress_button.configure(state=tk.NORMAL)
        return
    if target_resolution > height:
        tk.messagebox.showerror("Erro", "A resolução especificada é maior que a resolução do arquivo original")
        compress_button.configure(state=tk.NORMAL)
        return
    
    abort_button.configure(state=tk.NORMAL, cursor="hand2")

    compress_button.configure(state="disabled", cursor="")
    size_entry.configure(state="disabled")
    fps_entry.configure(state="disabled")
    resolution_entry.configure(state="disabled")
    codec_combobox.configure(state="disabled")
    mute_check.configure(state="disabled")

    processing_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    

    duration = float(ffprobe_data["format"]["duration"])
    target_bitrate = max((target_size * 8192) / (1.05 * duration) - 128, 100)

    ffmpeg_path = os.path.join(base_path, "ffmpeg", "bin", "ffmpeg.exe")
    ffmpeg_path = ffmpeg_path.replace("\\", "\\\\")
    comp_file_path = comp_file_path.replace("\\", "\\\\")
    output_file_path = comp_file_path.rsplit(".", 1)[0] + "_comp.mp4"
    output_file_path = output_file_path.replace("\\", "\\\\")
    mute_option = "-an" if mute_var.get() else ""

    compress_video_once(ffmpeg_path, comp_file_path, output_file_path, target_bitrate, target_fps, target_resolution, duration, mute_option)

    if two_step_var.get():
        size_difference = os.path.getsize(output_file_path) / (1024 * 1024) - target_size

        if size_difference > 1:
            target_bitrate -= size_difference * 8192 / (1.05 * duration) * 0.8
            second_output_file_path = comp_file_path.rsplit(".", 1)[0] + "_comp2.mp4"
            second_output_file_path = second_output_file_path.replace("\\", "\\\\")
            twostep = 1
            compress_video_once(ffmpeg_path, output_file_path, second_output_file_path, target_bitrate, target_fps, target_resolution, duration, mute_option)
            
        else:
            if tk.messagebox.askyesno("Apagar vídeo", "Deseja apagar o vídeo original?"):
                send2trash(get_trash_path(comp_file_path))
                update_thumbnail(output_file_path)


twostep = 0
def compress_video_once(ffmpeg_path, input_file_path, output_file_path, target_bitrate, target_fps, target_resolution, duration, mute_option):
    global frame, twostep
    frame = 0
    gpu_var = tk.BooleanVar(value=True)
    load_settings()
    if gpu_var.get():
        gpu_brand = get_gpu_brand()
        if gpu_brand == "NVIDIA":
            codec = f"{codec_var.get()}_nvenc"
        elif gpu_brand == "AMD":
            codec = f"{codec_var.get()}_amf"
        elif gpu_brand == "Intel":
            codec = f"{codec_var.get()}_qsv"
        else:
            codec = codec_var.get()
    else:
        codec = codec_var.get()

    unsharp_value = unsharp_options[unsharp_var.get()]
    unsharp_option = f'unsharp={unsharp_value},' if unsharp_value else ""
    command = f'"{ffmpeg_path}" -y -loglevel level+debug -i "{input_file_path}" -c:v {codec} -b:v {target_bitrate:.0f}k -r {target_fps:.2f} -vf "{unsharp_option}scale=-2:{target_resolution}" {mute_option} "{output_file_path}"'

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    global compress_process
    compress_process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
    counter = 0
    while True:
        if compress_process.poll() is not None:
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
            progress_percentage = (current_time / duration)

            progress_label.set(progress_percentage)
        
        counter += 1
        if counter % 10 == 0:
            frame = (frame + 1) % len(combined_frames)
            processing_label.configure(image=combined_frames[frame])
            processing_label.image = combined_frames[frame]

    compress_process.wait()
    if compress_process.returncode is not None:
        print("O processo de compressão foi encerrado")
        if two_step_var.get():
            if (twostep == 1):
                send2trash(get_trash_path(input_file_path))
                twostep = 0
                if tk.messagebox.askyesno("Apagar vídeo", "Deseja apagar o vídeo original?"):
                    send2trash(get_trash_path(comp_file_path))
        else:
            if tk.messagebox.askyesno("Apagar vídeo", "Deseja apagar o vídeo original?"):
                send2trash(get_trash_path(comp_file_path))
                update_thumbnail(output_file_path)
            
                

    processing_label.place_forget()
    compress_button.configure(state=tk.NORMAL, cursor="hand2")
    abort_button.configure(state=ctk.DISABLED, cursor="")
    compress_button.configure(state=tk.NORMAL, cursor="hand2")
    size_entry.configure(state=tk.NORMAL)
    fps_entry.configure(state=tk.NORMAL)
    resolution_entry.configure(state=tk.NORMAL)
    codec_combobox.configure(state=tk.NORMAL)
    mute_check.configure(state=tk.NORMAL)


'''
def del_originalvideo(comp_file_path):
    try:
        os.remove(comp_file_path)
    except Exception as e:
        tk.messagebox.showerror("Erro", f"Não foi possível apagar o arquivo: {e}")
'''

def select_video(event):
    comp_file_path = filedialog.askopenfilename(filetypes=[("Arquivos de Vídeo", "*.mp4;*.avi;*.mov;*.flv")])
    if comp_file_path:
        video_path.set(comp_file_path)
        update_thumbnail(comp_file_path)

def drop_video(event):
    if event.data:
        comp_file_path = event.data.strip("{}")
        video_path.set(comp_file_path)
        update_thumbnail(comp_file_path)
        return event.action

def update_thumbnail(comp_file_path):
    try:
        if not comp_file_path.lower().endswith((".mp4", ".avi", ".mov", ".flv")):
            raise Exception("Arquivo inválido")
        ffmpeg_path = os.path.join(base_path, "ffmpeg", "bin", "ffmpeg.exe")
        ffmpeg_path = ffmpeg_path.replace("\\", "\\\\")
        comp_file_path = comp_file_path.replace("\\", "\\\\")
        command = f'"{ffmpeg_path}" -y -i "{comp_file_path}" -ss 00:00:01.000 -vframes 1 -f image2pipe -'
        thumbnail_data = subprocess.check_output(command, shell=True)
        photo = ctk.CTkImage(light_image=Image.open(BytesIO(thumbnail_data)),
                    dark_image=Image.open(BytesIO(thumbnail_data)),
                    size=(400, 225))
        photo._light_image = photo._light_image.convert("RGBA")
        photo._dark_image = photo._dark_image.convert("RGBA")
        photo._light_image.thumbnail((400, 225))
        thumbnail_label.configure(image=photo)
        thumbnail_label.image = photo

        gif = imageio.mimread(base_path+'/imgs/carregando.gif')

        global combined_frames
        combined_frames = []
        
        try:
            for i, frame in enumerate(gif):
                frame_image = Image.fromarray(frame)
                frame_image = frame_image.resize(photo._size)
                thumbnail_image = photo._light_image.resize(photo._size)
                if (i!=0):
                    combined_frame = Image.alpha_composite(thumbnail_image, frame_image)
                    combined_ctk_frame = ctk.CTkImage(light_image=combined_frame, dark_image=combined_frame, size=(400, 225))
                    combined_frames.append(combined_ctk_frame)
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Erro: {e}")

        file_size = os.path.getsize(comp_file_path) / (1024 * 1024)
        size_entry.delete(0, tk.END)
        size_entry._placeholder_text = f"{file_size:.2f}"
        size_entry.focus_force()

        ffprobe_path = os.path.join(base_path, "ffmpeg", "bin", "ffprobe.exe")
        ffprobe_path = ffprobe_path.replace("\\", "\\\\")
        ffprobe_command = f'"{ffprobe_path}" -v quiet -print_format json -show_streams "{comp_file_path}"'
        ffprobe_output = subprocess.check_output(ffprobe_command, shell=True)
        ffprobe_data = json.loads(ffprobe_output)

        video_stream = next(stream for stream in ffprobe_data["streams"] if stream["codec_type"] == "video")
        fps = eval(video_stream["avg_frame_rate"])
        height = video_stream["height"]

        fps_entry.delete(0, tk.END)
        fps_entry._placeholder_text = f"{fps:.2f}"
        fps_entry.focus_force()

        resolution_entry.delete(0, tk.END)
        resolution_entry._placeholder_text = f"{height}"
        resolution_entry.focus_force()

        compress_button.configure(state=tk.NORMAL, cursor="hand2")
        abort_button.configure(state=ctk.DISABLED, cursor="")
        app_frame.focus()
        thumbnail_label.configure(text="")

    except:
        photo = ctk.CTkImage(light_image=Image.open(base_path+"/imgs/thumb_error.jpeg"),
                    dark_image=Image.open(base_path+"/imgs/thumb_error.jpeg"),
                    size=(400, 225))

        compress_button.configure(state=ctk.DISABLED, cursor="")
        abort_button.configure(state=ctk.DISABLED, cursor="")
        thumbnail_label.configure(image=photo, text="Erro ao carregar arquivo.", font=ctk.CTkFont(size=18, weight="bold"))
        

    thumbnail_label.configure(image=photo)
    thumbnail_label.image = photo

def on_app_frame_click(event):
    app_frame.focus_set()



# --                     -- #
# ---      APP DEF      --- # 
# --                     -- #

root = Tk()
root.geometry("700x500")
root.minsize(800,500)
root.iconbitmap(base_path+'/imgs/icon.ico')
root.title("KUE Video-Editor Colection")

theme_var = tk.StringVar(value="System")
highlight_color_var = tk.StringVar(value="blue")
gpu_var = tk.BooleanVar(value=True)
two_step_var = tk.BooleanVar(value=True)
load_settings()
on_theme_change()

image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "imgs")
icon_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "compressIco.png")),
                                            dark_image=Image.open(os.path.join(image_path, "compressIco.png")), size=(40, 40))
home_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                            dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
cut_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "cut_dark.png")),
                                            dark_image=Image.open(os.path.join(image_path, "cut_light.png")), size=(20, 20))
comp_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "comp_dark.png")),
                                            dark_image=Image.open(os.path.join(image_path, "comp_light.png")), size=(20, 20))
config_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "config_dark.png")),
                                            dark_image=Image.open(os.path.join(image_path, "config_light.png")), size=(20, 20))

navigation_frame = ctk.CTkFrame(root, corner_radius=0)
navigation_frame.pack(side="left", fill="y")

navigation_frame_label = ctk.CTkLabel(navigation_frame, text="  KUE - VEC  ", compound="left", image=icon_image, font=ctk.CTkFont(size=18, weight="bold"))
navigation_frame_label.pack(fill="x", pady=5, padx=5)

home_nav_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), image=home_image, anchor="w", command=home_button_event)
home_nav_button.pack(fill="x")

cut_nav_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Cortar Video", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), image=cut_image, anchor="w", command=cut_button_event)
cut_nav_button.pack(fill="x")

comp_nav_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Comprimir Video", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), image=comp_image, anchor="w", command=comp_button_event)
comp_nav_button.pack(fill="x")

config_nav_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Configurações", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), image=config_image, anchor="w", cursor="hand2")
config_nav_button.pack(fill="x", side="bottom")
config_nav_button.bind("<Button-1>", open_settings)



# --                    -- #
# ---     HOME DEF     --- #
# --                    -- #

home_frame = ctk.CTkScrollableFrame(root)

description_label = ctk.CTkLabel(home_frame, text="""Bem-vindo ao KUE Video-Editor Colection!
Este aplicativo permite cortar e comprimir vídeos de maneira fácil e rápida.""", font=ctk.CTkFont(size=14, weight="bold"))
description_label.pack(fill=ctk.X, padx=10, pady=10)

text_frame = ctk.CTkFrame(home_frame)
text_frame.pack(fill=ctk.X, padx=10)

tutorial_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
tutorial_frame.pack(fill=ctk.BOTH, expand=True)

tutorial_label = ctk.CTkLabel(tutorial_frame, text="Como usar o aplicativo:", font=ctk.CTkFont(size=18, weight="bold"))
tutorial_label.pack(fill=ctk.X, pady=(5,0))

tutorial_text = """1. Selecione a aba Cortar ou Comprimir na barra de navegação à esquerda.
2. Arraste e solte um arquivo de vídeo na janela do programa
    ou cliquena janela para selecionar um arquivo.
3. Use os controles deslizantes e as caixas de entrada para
    ajustar as configurações de corte ou compressão.
4. Clique no botão Cortar ou Comprimir para iniciar o processo.
5. Aguarde até que o processo seja concluído.
    O arquivo de saída será salvo na mesma pasta do arquivo de entrada."""

tutorial_text_label = ctk.CTkLabel(tutorial_frame, text=tutorial_text, justify="left")
tutorial_text_label.pack(fill=ctk.X, side="left", padx=15, pady=(0,10))

github_label = ctk.CTkLabel(text_frame, text="Para mais informações e atualizações, visite o repositório no Github:", font=ctk.CTkFont(size=14, weight="bold"))
github_label.pack(fill=ctk.X, padx=10, pady=(0, 5))

github_link = ctk.CTkButton(text_frame, text="KUE-VEC on GITHUB", command=lambda: os.startfile("https://github.com/CauehCraft/KUE-video-compressor"))
github_link.pack()

updates_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
updates_frame.pack(fill=ctk.BOTH, expand=True)

updates_label = ctk.CTkLabel(updates_frame, text="Atualizações recentes:", font=ctk.CTkFont(size=18, weight="bold"))
updates_label.pack(fill=ctk.X, pady=(5,0))

updates_text = """# Versão 1.0
- Adicionado suporte para compressão e cortes de vídeo usando GPU.
- Melhorias na interface do usuário e correções de bugs."""

updates_text_label = ctk.CTkLabel(updates_frame, text=updates_text, justify="left")
updates_text_label.pack(fill=ctk.X, side="left", padx=15, pady=(0,10))



# --                     -- #
# ---      CUT DEF      --- # 
# --                     -- #

video_frame = ctk.CTkFrame(root)
video_frame.pack(fill=ctk.BOTH, expand=True)
video_frame.drop_target_register(DND_FILES)
video_frame.dnd_bind('<<Drop>>', on_drop)

video_label = ctk.CTkLabel(video_frame, text="Arraste um video aqui", font=ctk.CTkFont(size=36, weight="bold"))
video_label.pack(fill=ctk.BOTH, expand=True)

slider_frame = ctk.CTkFrame(root, fg_color="transparent")
slider_frame.pack(fill=ctk.X)

button_frame = ctk.CTkFrame(root, fg_color="transparent")
button_frame.pack(side="bottom", fill=ctk.X)

play_pause_button = ctk.CTkButton(button_frame, text="⏯️", command=on_play_pause_button_click, state=ctk.DISABLED, width=50)
play_pause_button.pack(side="left", padx=(10, 10), pady=10)

cut_progress_label = ctk.CTkProgressBar(button_frame, orientation="horizontal")
cut_progress_label.pack(side="left", padx=(10, 0), pady=10, anchor="center")
cut_progress_label.set(0)

select_button = ctk.CTkButton(button_frame, text="Select Video", command=cut_select_video, width=100)
select_button.pack(side="right", padx=(10, 10), pady=10)

cut_abort = ctk.CTkButton(button_frame, text="Abortar", command=on_cut_abort_button_click, state=ctk.DISABLED, width=75, fg_color="#a10f0f")
cut_abort.pack(side="right", padx=(10, 0), pady=10)

cut_button = ctk.CTkButton(button_frame, text="Cortar", command=on_cut_button_click, state=ctk.DISABLED, width=75)
cut_button.pack(side="right", padx=(10, 0), pady=10)

current_time_var = ctk.StringVar(value="00:00")
current_time_label = ctk.CTkLabel(button_frame, textvariable=current_time_var)
current_time_label.pack(side="right", padx=(10, 0), pady=10)

time_slider = ctk.CTkSlider(slider_frame, from_=0, to=1000, orientation=ctk.HORIZONTAL, command=on_time_slider_change, state=ctk.DISABLED)
time_slider.pack(fill=ctk.X, padx=10)

cut_start_slider = ctk.CTkSlider(slider_frame, from_=0, to=1000, orientation=ctk.HORIZONTAL, command=on_cut_start_slider_change, progress_color="transparent", state=ctk.DISABLED)
cut_start_slider.pack(fill=ctk.X, padx=10)
cut_start_slider.set(0)

cut_end_slider = ctk.CTkSlider(slider_frame, from_=0, to=1000, orientation=ctk.HORIZONTAL, command=on_cut_end_slider_change, progress_color="transparent", state=ctk.DISABLED)
cut_end_slider.pack(fill=ctk.X, padx=10)
cut_end_slider.set(1000)




# --                          -- #
# ---      COMPRESS DEF      --- # 
# --                          -- #

app_frame = ctk.CTkFrame(root, fg_color="transparent")
app_frame.bind("<Button-1>", on_app_frame_click)

comp_video_frame = ctk.CTkFrame(root, fg_color="transparent")
comp_video_frame.bind("<Button-1>", on_app_frame_click)

left_options_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
left_options_frame.pack(pady=10, padx=15, fill="both", side="left", expand=True)
left_options_frame.bind("<Button-1>", on_app_frame_click)

right_options_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
right_options_frame.pack(pady=10, padx=15, fill="both", side="right", expand=True)
right_options_frame.bind("<Button-1>", on_app_frame_click)

bottom_options_frame = ctk.CTkFrame(root, fg_color="transparent")
bottom_options_frame.bind("<Button-1>", on_app_frame_click)

video_path = tk.StringVar()

drop_frame = ctk.CTkFrame(comp_video_frame, fg_color="transparent")
drop_frame.pack(fill="both", expand=True)
drop_frame.grid_rowconfigure(0, weight=1)
drop_frame.grid_columnconfigure(0, weight=1)
drop_frame.drop_target_register(tkinterdnd2.DND_FILES)
drop_frame.dnd_bind("<<Drop>>", drop_video)
drop_frame.bind("<Button-1>", select_video)

thumbnail_label = ctk.CTkLabel(drop_frame, text="Arraste um video aqui.", font=ctk.CTkFont(size=18, weight="bold"))
thumbnail_label.grid(row=0, column=0, sticky="nsew")



processing_label = ctk.CTkLabel(thumbnail_label, text="")

size_label = ctk.CTkLabel(left_options_frame, text="Tamanho (MB)")
size_label.pack(side="top")
size_entry = ctk.CTkEntry(left_options_frame, width=90)
size_entry.configure(justify='left')
size_entry.pack(side="top")



fps_label = ctk.CTkLabel(left_options_frame, text="FPS")
fps_label.pack(side="top")
fps_entry = ctk.CTkEntry(left_options_frame, width=90)
fps_entry.pack(side="top")
fps_entry._placeholder_text = ""
fps_entry._placeholder_text_active = True

resolution_label = ctk.CTkLabel(left_options_frame, text="Resolução (px)")
resolution_label.pack(side="top")
resolution_entry = ctk.CTkEntry(left_options_frame, width=90)
resolution_entry.configure(justify='left')
resolution_entry.pack(side="top")

codec_var = tk.StringVar(value="h264")
codec_label = ctk.CTkLabel(right_options_frame, text="Codec")
codec_label.pack(side="top")
codec_combobox = ctk.CTkComboBox(right_options_frame, variable=codec_var,values=["h264", "hevc"], state="readonly", width=90)
codec_combobox.set("h264")
codec_combobox.pack(side="top")

unsharp_var = tk.StringVar(value="")
unsharp_options = {
    "OFF": "",
    "+Forte": "13:13:5",
    "Forte": "13:13:2.5",
    "Médio": "3:3:5",
    "Fraco": "5:5:2",
    "+Fraco": "3:3:1.5"
}
unsharp_label = ctk.CTkLabel(right_options_frame, text="Nitidez adicional")
unsharp_label.pack(side="top", pady=(0))
unsharp_combobox = ctk.CTkComboBox(right_options_frame, variable=unsharp_var, values=list(unsharp_options.keys()), state="readonly", width=90)
unsharp_combobox.set("OFF")
unsharp_combobox.pack(side="top")

mute_var = tk.BooleanVar()
mute_check = ctk.CTkSwitch(right_options_frame, text="Mutar vídeo", variable=mute_var, cursor="hand2", onvalue=True, offvalue=False)
mute_check.pack(side="top", pady=(10))

abort_button = ctk.CTkButton(bottom_options_frame, text="Abortar", command=abort_compression, 
                            height=30, 
                            width=120,
                            fg_color="#a10f0f",
                            corner_radius=7,
                            anchor="center",
                            font=("Helvetica", 16))
abort_button.pack(side="right", padx=(10, 0), pady=10)
abort_button.configure(state=ctk.DISABLED)

compress_button = ctk.CTkButton(bottom_options_frame, text="Comprimir", command=compress_video, 
                            height=30, 
                            width=120,
                            corner_radius=7,
                            font=("Helvetica", 16))
compress_button.pack(side="right", padx=(10, 0), pady=10)
compress_button.configure(state=ctk.DISABLED)

photo = ctk.CTkImage(light_image=Image.open(base_path+"/imgs/thumb_sample.jpeg"),
                    dark_image=Image.open(base_path+"/imgs/thumb_sample.jpeg"),
                    size=(400, 225))
thumbnail_label.configure(image=photo)
thumbnail_label.image = photo

progress_label = ctk.CTkProgressBar(bottom_options_frame, orientation="horizontal")
progress_label.pack(side="left", padx=(10, 0), pady=10, anchor="center")
progress_label.set(0)


def validate_float_input(new_value):
    return new_value.replace(".", "", 1).isdecimal() or new_value == ""

def validate_int_input(new_value):
    return new_value.isdecimal() or new_value == ""

validate_float_command = root.register(validate_float_input)
validate_int_command = root.register(validate_int_input)

size_entry.configure(validate="key", validatecommand=(validate_float_command, "%P"))
fps_entry.configure(validate="key", validatecommand=(validate_float_command, "%P"))
resolution_entry.configure(validate="key", validatecommand=(validate_int_command, "%P"))


home_button_event()
root.mainloop()
