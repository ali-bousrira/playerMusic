import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
import customtkinter as ctk
from mutagen.mp3 import MP3
import threading
import pygame
import time
import os
from random import randint

# Initialiser le mélangeur pygame
pygame.mixer.init()

# Stocker la position actuelle de la musique
position_actuelle = 0
en_pause = False
en_stop = False
# Stocker le chemin du dossier sélectionné
chemin_dossier_selectionne = ""  

def mettre_a_jour_progression():
    global position_actuelle
    while True:
        if pygame.mixer.music.get_busy() and not en_pause:
            position_actuelle = pygame.mixer.music.get_pos() / 1000
            pbar["value"] = position_actuelle

            # Vérifier si la chanson actuelle a atteint sa durée maximale
            if position_actuelle >= pbar["maximum"]:
                arreter_musique()  # Arrêter la lecture de la musique
                pbar["value"] = 0  # Réinitialiser la barre de progression

            window.update()


# Créer un thread pour mettre à jour la barre de progression
pt = threading.Thread(target=mettre_a_jour_progression)
pt.daemon = True
pt.start()

def selectionner_dossier_musique():
    global chemin_dossier_selectionne
    chemin_dossier_selectionne = filedialog.askdirectory()
    if chemin_dossier_selectionne:
        lbox.delete(0, tk.END)
        for nom_fichier in os.listdir(chemin_dossier_selectionne):
            if nom_fichier.endswith(".mp3"):
                lbox.insert(tk.END, nom_fichier)  # Insérer uniquement le nom du fichier, pas le chemin complet

def chanson_precedente():
    if len(lbox.curselection()) > 0:
        index_actuel = lbox.curselection()[0]
        if index_actuel > 0:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(index_actuel - 1)
            jouer_chanson_selectionnee()

def chanson_suivante():
    if len(lbox.curselection()) > 0:
        index_actuel = lbox.curselection()[0]
        if index_actuel < lbox.size() - 1:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(index_actuel + 1)
            jouer_chanson_selectionnee()

def chanson_aleatoire ():
    if len(lbox.curselection()) > 0:
        arreter_musique()
        pygame.mixer.music.unload()
        alea = randint (0, lbox.size() - 1)
        while alea == lbox.curselection()[0] :
            alea = randint (0, lbox.size() - 1)
        lbox.selection_clear(0, tk.END)
        lbox.selection_set(alea)
        jouer_chanson_selectionnee()
        

def jouer_musique():
    global en_pause
    global en_stop
    if en_pause:
        # Si la musique est en pause, reprendre la lecture
        pygame.mixer.music.unpause()
        en_pause = False
    elif en_stop :
        pygame.mixer.music.play()
        en_stop = False
    else :
        # Si la musique n'est pas en pause, jouer la chanson sélectionnée
        jouer_chanson_selectionnee()

def jouer_chanson_selectionnee():
    global position_actuelle, en_pause, en_stop
    if len(lbox.curselection()) > 0:
        index_actuel = lbox.curselection()[0]
        chanson_selectionnee = lbox.get(index_actuel)
        chemin_complet = os.path.join(chemin_dossier_selectionne, chanson_selectionnee)  # Ajouter le chemin complet
        pygame.mixer.music.load(chemin_complet)  # Charger la chanson sélectionnée
        pygame.mixer.music.play(start=position_actuelle)  # Jouer la chanson à partir de la position actuelle
        en_pause = False
        en_stop = False
        audio = MP3(chemin_complet)
        duree_chanson = audio.info.length
        pbar["maximum"] = duree_chanson  # Définir la valeur maximale de la barre de progression sur la durée de la chanson

def mettre_en_pause():
    global en_pause
    # Mettre en pause la musique en cours de lecture
    pygame.mixer.music.pause()
    en_pause = True

def arreter_musique():
    global en_pause
    global en_stop
    # Arrêter la musique en cours de lecture et réinitialiser la barre de progression
    pygame.mixer.music.stop()
    pbar["value"] = 0  # Réinitialiser la barre de progression
    en_pause = False
    en_stop = True

def volum_plus ():
        volume = pygame.mixer.music.get_volume()
        if volume < 1.0:
            pygame.mixer.music.set_volume(volume + 0.1)

def volum_moin ():
    volume = pygame.mixer.music.get_volume()
    if volume > 0.0:
            pygame.mixer.music.set_volume(volume - 0.1)

# Créer la fenêtre principale
window = tk.Tk()
window.title("Lecteur de Musique")
window.geometry("600x650")

# Créer une étiquette pour le titre du lecteur de musique
l_music_player = tk.Label(window, text="Lecteur de Musique", font=("TkDefaultFont", 30, "bold"))
l_music_player.pack(pady=10)

# Créer un bouton pour sélectionner le dossier de musique
btn_select_folder = ctk.CTkButton(window, text="Sélectionner le Dossier de Musique", command=selectionner_dossier_musique, font=("TkDefaultFont", 18))
btn_select_folder.pack(pady=20)

# Créer une liste pour afficher les chansons disponibles
lbox = tk.Listbox(window, width=50, font=("TkDefaultFont", 16))
lbox.pack(pady=10)

# Créer un cadre pour contenir les boutons de contrôle
btn_frame = tk.Frame(window)
btn_frame.pack(pady=20)

#selection aléatoire
btn_alea = ctk.CTkButton(btn_frame, text="aléatoire", command=chanson_aleatoire, width=50, font=("TkDefaultFont", 18))
btn_alea.pack(side=tk.LEFT, padx=5)

# Créer un bouton pour aller à la chanson précédente
btn_previous = ctk.CTkButton(btn_frame, text="<", command=chanson_precedente, width=50, font=("TkDefaultFont", 18))
btn_previous.pack(side=tk.LEFT, padx=5)

# Créer un bouton pour lire la musique
btn_play = ctk.CTkButton(btn_frame, text="Lire", command=jouer_musique, width=50, font=("TkDefaultFont", 18))
btn_play.pack(side=tk.LEFT, padx=5)

# Créer un bouton pour arrêter la musique
btn_stop = ctk.CTkButton(btn_frame, text="Arrêter", command=arreter_musique, width=50, font=("TkDefaultFont", 18))
btn_stop.pack(side=tk.LEFT, padx=5)

# Créer un bouton pour mettre en pause la musique
btn_pause = ctk.CTkButton(btn_frame, text="Pause", command=mettre_en_pause, width=50, font=("TkDefaultFont", 18))
btn_pause.pack(side=tk.LEFT, padx=5)

# Créer un bouton pour aller à la chanson suivante
btn_next = ctk.CTkButton(btn_frame, text=">", command=chanson_suivante, width=50, font=("TkDefaultFont", 18))
btn_next.pack(side=tk.LEFT, padx=5)

#créer un bouton pour augmenter le volume
btn_volum_plus = ctk.CTkButton(btn_frame, text = "volum +", command = volum_plus, width = 50, font=("TkDefaultFont", 18))
btn_volum_plus.pack (side = tk.LEFT, padx = 5)

#créer un bouton pour augmenter le volume
btn_volum_plus = ctk.CTkButton(btn_frame, text = "volum -", command = volum_moin, width = 50, font=("TkDefaultFont", 18))
btn_volum_plus.pack (side = tk.LEFT, padx = 5)

# Créer une barre de progression pour indiquer la progression de la chanson actuelle
pbar = Progressbar(window, length=300, mode="determinate")
pbar.pack(pady=10)

window.mainloop()
