#!/usr/bin/env python3
# ============================================================================
# DASHCAM AUTOMATIQUE POUR RASPBERRY PI 3
# ============================================================================
# Ce script enregistre automatiquement des vidéos de 5 minutes en boucle
# sur deux clés USB, en basculant sur la deuxième quand la première est pleine
# ============================================================================

# ---------- IMPORTS (bibliothèques nécessaires) ----------
import subprocess  # Pour exécuter des commandes système (ffmpeg)
import os          # Pour gérer les fichiers et dossiers
import time        # Pour faire des pauses entre les enregistrements
from datetime import datetime  # Pour obtenir la date et l'heure actuelles

# ---------- CONFIGURATION GLOBALE ----------
# Ces paramètres définissent comment la dashcam fonctionne

# Chemins vers les deux clés USB montées
USB_PATHS = ["/mnt/usb1", "/mnt/usb2"]

# Durée de chaque segment vidéo en secondes (300 = 5 minutes)
VIDEO_DURATION = 300

# Résolution de la vidéo (largeur x hauteur en pixels)
VIDEO_WIDTH = 1280   # Largeur : 1280 pixels (qualité HD 720p)
VIDEO_HEIGHT = 720   # Hauteur : 720 pixels

# Périphérique de la webcam USB détecté par le système
DEVICE = "/dev/video0"

# Temps d'attente entre deux enregistrements (en secondes)
# 1 seconde permet au système de respirer entre deux vidéos
INTERVAL = 1

# Espace minimum requis sur une clé avant de basculer sur l'autre (en Go)
# Avec 2 Go, la clé sera utilisée jusqu'à ce qu'il reste seulement 2 Go libres
# Cela permet de stocker environ 200 vidéos (~16-17h) sur une clé de 64 Go
MIN_FREE_SPACE_GB = 2


# ============================================================================
# FONCTION : get_free_space_gb
# ============================================================================
# Rôle : Calculer l'espace disponible sur une clé USB en Go
# Paramètre : path = chemin vers la clé USB (ex: "/mnt/usb1")
# Retourne : Espace libre en Go (ex: 58.5), ou 0 si erreur
# ============================================================================
def get_free_space_gb(path):
    """Retourne l'espace disponible en Go sur le chemin spécifié"""
    
    try:
        # os.statvfs() récupère les statistiques du système de fichiers
        stat = os.statvfs(path)
        
        # Calcul de l'espace libre en octets
        # f_bavail = nombre de blocs disponibles pour utilisateurs non-root
        # f_frsize = taille d'un bloc en octets
        free_bytes = stat.f_bavail * stat.f_frsize
        
        # Conversion des octets en Go (1 Go = 1024^3 octets)
        free_gb = free_bytes / (1024**3)
        
        return free_gb
        
    except:
        # En cas d'erreur (clé non montée, etc.), retourne 0
        return 0


# ============================================================================
# FONCTION : select_usb_path
# ============================================================================
# Rôle : Choisir automatiquement quelle clé USB utiliser pour enregistrer
# Logique : 
#   1. Vérifie les deux clés USB
#   2. Filtre celles qui ont au moins MIN_FREE_SPACE_GB (2 Go) de libre
#   3. Choisit celle avec le PLUS d'espace disponible
#   4. Si aucune n'a assez d'espace, prend celle avec le plus d'espace quand même
# Retourne : Le chemin de la clé sélectionnée (ex: "/mnt/usb1"), ou None si aucune
# ============================================================================
def select_usb_path():
    """Sélectionne la clé USB avec le plus d'espace disponible"""
    
    # Liste qui va contenir les clés disponibles et leur espace libre
    # Format : [(chemin, espace_en_Go), ...]
    available_usbs = []
    
    # ---------- ÉTAPE 1 : Vérifier chaque clé USB ----------
    for usb_path in USB_PATHS:  # Pour chaque clé (/mnt/usb1 puis /mnt/usb2)
        
        # Vérifier si le chemin existe ET si la clé est bien montée
        if os.path.exists(usb_path) and os.path.ismount(usb_path):
            
            # Calculer l'espace libre sur cette clé
            free_space = get_free_space_gb(usb_path)
            
            # Si la clé a assez d'espace (au moins MIN_FREE_SPACE_GB = 2 Go)
            if free_space >= MIN_FREE_SPACE_GB:
                # Ajouter cette clé à la liste des clés utilisables
                available_usbs.append((usb_path, free_space))
                
                # Afficher l'espace disponible pour information
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"{usb_path}: {free_space:.2f} Go disponibles")
    
    # ---------- ÉTAPE 2 : Gérer le cas où aucune clé n'a assez d'espace ----------
    if not available_usbs:
        # Afficher un avertissement : les deux clés sont presque pleines
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
              f"ATTENTION: Aucune clé n'a assez d'espace libre (< 2 Go)!")
        
        # Dans ce cas, on prend quand même celle avec le PLUS d'espace
        # même si c'est moins de 2 Go (pour éviter de bloquer l'enregistrement)
        for usb_path in USB_PATHS:
            if os.path.exists(usb_path) and os.path.ismount(usb_path):
                free_space = get_free_space_gb(usb_path)
                available_usbs.append((usb_path, free_space))
        
        # Si vraiment aucune clé n'est détectée, retourner None
        if not available_usbs:
            return None
    
    # ---------- ÉTAPE 3 : Choisir la meilleure clé ----------
    # Trier la liste par espace disponible (du plus grand au plus petit)
    # lambda x: x[1] signifie "trier selon le 2ème élément du tuple (l'espace en Go)"
    # reverse=True signifie "ordre décroissant" (du plus grand au plus petit)
    available_usbs.sort(key=lambda x: x[1], reverse=True)
    
    # Prendre la première clé de la liste (celle avec le plus d'espace)
    # [0] = premier élément de la liste
    # [0] = première valeur du tuple (le chemin, pas l'espace)
    selected_usb = available_usbs[0][0]
    
    # Afficher quelle clé a été choisie
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
          f"Clé sélectionnée: {selected_usb}")
    
    return selected_usb


# ============================================================================
# FONCTION : record_video
# ============================================================================
# Rôle : Enregistrer UNE vidéo de 5 minutes sur la clé USB spécifiée
# Paramètre : usb_path = chemin de la clé où enregistrer (ex: "/mnt/usb1")
# Retourne : True si succès, False si erreur
# ============================================================================
def record_video(usb_path):
    """Enregistre une vidéo MJPEG de 5 minutes"""
    
    # ---------- ÉTAPE 1 : Créer le nom du fichier ----------
    # Générer un horodatage au format : AAAAMMJJ_HHMMSS
    # Exemple : 20251003_143520 = 3 oct 2025 à 14h35m20s
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Créer le nom complet du fichier
    # Exemple : video_20251003_143520.avi
    filename = f"video_{timestamp}.avi"
    
    # Créer le chemin complet vers le fichier
    # os.path.join() combine le chemin de la clé + le nom du fichier
    # Exemple : /mnt/usb1/video_20251003_143520.avi
    filepath = os.path.join(usb_path, filename)
    
    # Afficher un message de début d'enregistrement
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
          f"Début enregistrement: {filename} sur {usb_path}")
    
    # ---------- ÉTAPE 2 : Préparer la commande ffmpeg ----------
    # ffmpeg est le logiciel qui va capturer la vidéo depuis la webcam
    # On construit la commande sous forme de liste de paramètres
    cmd = [
        "ffmpeg",                    # Le programme à exécuter
        
        # --- Paramètres d'ENTRÉE (webcam) ---
        "-f", "v4l2",                # Format : Video4Linux2 (standard Linux pour webcam)
        "-input_format", "mjpeg",    # Format d'entrée : MJPEG (Motion JPEG)
        "-video_size", f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}",  # Résolution : 1280x720
        "-i", DEVICE,                # Périphérique d'entrée : /dev/video0 (la webcam)
        
        # --- Paramètres de durée ---
        "-t", str(VIDEO_DURATION),   # Durée : 300 secondes (5 minutes)
        
        # --- Paramètres de SORTIE (fichier vidéo) ---
        "-c:v", "copy",              # Codec vidéo : "copy" = pas de ré-encodage,
                                     # on copie le flux MJPEG tel quel (rapide)
        "-f", "avi",                 # Format de fichier : AVI
        
        filepath                     # Chemin complet du fichier de sortie
    ]
    
    # ---------- ÉTAPE 3 : Lancer l'enregistrement ----------
    try:
        # subprocess.run() exécute la commande ffmpeg
        # check=True : lève une exception si la commande échoue
        subprocess.run(cmd, check=True)
        
        # Si on arrive ici, l'enregistrement s'est bien terminé
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
              f"Enregistrement terminé: {filename}")
        return True
        
    except subprocess.CalledProcessError as e:
        # Si ffmpeg plante, afficher l'erreur
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
              f"Erreur d'enregistrement: {e}")
        return False


# ============================================================================
# FONCTION PRINCIPALE : main
# ============================================================================
# Rôle : Boucle infinie qui enregistre des vidéos en continu
# Logique :
#   1. Choisir la meilleure clé USB (celle avec le plus d'espace)
#   2. Enregistrer une vidéo de 5 minutes dessus
#   3. Attendre 1 seconde
#   4. Recommencer à l'étape 1
# ============================================================================
def main():
    # Message de démarrage du système
    print("=== Dashcam Recorder démarré (mode 2 clés USB) ===")
    
    # Boucle infinie : tourne sans fin jusqu'à l'arrêt du système
    while True:
        
        # ---------- ÉTAPE 1 : Sélectionner la clé USB à utiliser ----------
        usb_path = select_usb_path()
        
        # Si aucune clé n'a été détectée (retourne None)
        if not usb_path:
            # Afficher un message d'erreur
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"ERREUR: Aucune clé USB détectée")
            print("Nouvelle tentative dans 5 secondes...")
            
            # Attendre 5 secondes avant de réessayer
            time.sleep(5)
            
            # Revenir au début de la boucle (ne pas enregistrer)
            continue
        
        # ---------- ÉTAPE 2 : Enregistrer une vidéo ----------
        # Appeler la fonction record_video() avec la clé sélectionnée
        record_video(usb_path)
        
        # ---------- ÉTAPE 3 : Petite pause ----------
        # Attendre 1 seconde avant le prochain enregistrement
        # Cela laisse le temps au système de libérer les ressources
        time.sleep(INTERVAL)
        
        # La boucle repart au début : sélection de clé → enregistrement → pause...


# ============================================================================
# POINT D'ENTRÉE DU PROGRAMME
# ============================================================================
# Ce bloc s'exécute uniquement si on lance le script directement
# (pas si on l'importe comme module dans un autre script)
if __name__ == "__main__":
    main()  # Lancer la fonction principale
