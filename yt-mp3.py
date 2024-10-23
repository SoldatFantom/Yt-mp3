import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk, scrolledtext
import yt_dlp
from pydub import AudioSegment
import os
import threading

def browse_folder():
    selected_folder = filedialog.askdirectory(initialdir=os.path.expanduser("~/Music"))
    if selected_folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, selected_folder)

def create_new_folder_dialog():
    new_folder_window = tk.Toplevel(root)
    new_folder_window.title("Créer un nouveau dossier")

    tk.Label(new_folder_window, text="Nom du nouveau dossier :").pack(padx=10, pady=10)
    new_folder_name_entry = tk.Entry(new_folder_window)
    new_folder_name_entry.pack(padx=10, pady=10)

    def create_folder():
        base_folder = folder_entry.get()
        new_folder_name = new_folder_name_entry.get().strip()
        if base_folder and new_folder_name:
            new_folder_path = os.path.join(base_folder, new_folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=True)
                log_console.insert(tk.END, f"Dossier créé : {new_folder_path}\n")
                folder_entry.delete(0, tk.END)
                folder_entry.insert(0, new_folder_path)
                new_folder_window.destroy()
            except Exception as e:
                log_console.insert(tk.END, f"Erreur lors de la création du dossier : {str(e)}\n")
        else:
            log_console.insert(tk.END, "Erreur : Veuillez entrer un nom de dossier.\n")

    create_button = tk.Button(new_folder_window, text="Créer", command=create_folder)
    create_button.pack(padx=10, pady=10)

def update_log_console(message):
    log_console.insert(tk.END, message)
    log_console.see(tk.END)

def show_messagebox(title, message):
    messagebox.showinfo(title, message)

def download_and_convert_to_mp3():
    url = url_entry.get()
    download_folder = folder_entry.get()

    if not url or not download_folder:
        update_log_console("Erreur: Veuillez entrer une URL valide et un dossier de destination.\n")
        return

    download_progress_bar["value"] = 0
    download_progress_bar["maximum"] = 100
    conversion_progress_bar["value"] = 0
    conversion_progress_bar["maximum"] = 100

    def run_download():
        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
            'progress_hooks': [hook]
        }

        try:
            # Extraire les informations de la vidéo avant de commencer le téléchargement
            with yt_dlp.YoutubeDL(options) as ydl:
                root.after(0, update_log_console, "Début de l'opération ...\n")
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get('title', None)

                # Afficher le nom de la musique dans la console avant de télécharger
                root.after(0, update_log_console, f"Nom de la musique : {title}\n")
                root.after(0, update_log_console, "Téléchargement en cours...\n")

                # Télécharger la vidéo
                ydl.download([url])
        except Exception as e:
            root.after(0, update_log_console, f"Erreur lors du téléchargement: {str(e)}\n")
            return

        webm_filepath = os.path.join(download_folder, f'{title}.webm')
        mp3_filepath = os.path.join(download_folder, f'{title}.mp3')

        try:
            audio = AudioSegment.from_file(webm_filepath, format="webm")
            root.after(0, update_log_console, f"Conversion en MP3 en cours: {mp3_filepath}\n")

            # Conversion segmentée et mise à jour de la barre de progression
            segment_duration_ms = 1000  # Segment de 1 seconde
            total_duration_ms = len(audio)  # Durée totale en millisecondes
            progress_step = 100 / (total_duration_ms // segment_duration_ms)

            converted_audio = AudioSegment.silent(duration=0)
            for start in range(0, total_duration_ms, segment_duration_ms):
                end = min(start + segment_duration_ms, total_duration_ms)
                segment = audio[start:end]
                converted_audio += segment

                conversion_progress_bar["value"] += progress_step
                root.update_idletasks()  # Mise à jour de l'interface

            converted_audio.export(mp3_filepath, format="mp3")
            os.remove(webm_filepath)
            root.after(0, update_log_console, f"Conversion en MP3 terminée: {mp3_filepath}\n")
            root.after(0, show_messagebox, "Succès", f"Conversion terminée.\nFichier MP3 sauvegardé à : {mp3_filepath}")
        except Exception as e:
            root.after(0, update_log_console, f"Erreur lors de la conversion en MP3: {str(e)}\n")

    def hook(d):
        if d['status'] == 'downloading':
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            download_progress_bar["value"] = percent
            root.update_idletasks()

        if d['status'] == 'finished':
            root.after(0, update_log_console, "Téléchargement terminé.\n")

    threading.Thread(target=run_download).start()

# Création de l'interface utilisateur
root = tk.Tk()
root.title("Téléchargeur et Convertisseur MP3 YouTube")

url_label = tk.Label(root, text="URL de la vidéo :")
url_label.pack()

url_entry = tk.Entry(root, width=50)
url_entry.pack()

folder_frame = tk.Frame(root)
folder_frame.pack(pady=5)

folder_label = tk.Label(folder_frame, text="Destination :")
folder_label.grid(row=0, column=0)

create_button = tk.Button(folder_frame, text="Créer Dossier", command=create_new_folder_dialog)
create_button.grid(row=0, column=3)

folder_entry = tk.Entry(folder_frame, width=30)
folder_entry.grid(row=0, column=1, padx=5)

folder_button = tk.Button(folder_frame, text="Parcourir", command=browse_folder)
folder_button.grid(row=0, column=2)

download_button = tk.Button(root, text="Télécharger et Convertir en MP3", command=download_and_convert_to_mp3)
download_button.pack()

# Barre de progression pour le téléchargement
download_progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
download_progress_bar.pack(pady=5)
download_label = tk.Label(root, text="Téléchargement")
download_label.pack()

# Barre de progression pour la conversion
conversion_progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
conversion_progress_bar.pack(pady=5)
conversion_label = tk.Label(root, text="Conversion")
conversion_label.pack()

log_console = scrolledtext.ScrolledText(root, height=10, width=60, bg="black", fg="white")
log_console.pack(pady=10)

root.mainloop()
