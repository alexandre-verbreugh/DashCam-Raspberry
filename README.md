# DashCam-Raspberry
Dashcam automatique avec Raspberry Pi 3 et double clé USB

# Dashcam Raspberry Pi 3

Système de dashcam automatique pour enregistrer un trajet.

## Caractéristiques

- Enregistrement automatique au démarrage
- Vidéos en 1280x720 à 30 fps (format MJPEG)
- Segments de 5 minutes
- Gestion automatique de 2 clés USB (64 Go chacune)
- Bascule intelligente entre les clés selon l'espace disponible
- Nettoyage automatique (garde les 100 vidéos les plus récentes)

## Matériel

- Raspberry Pi 3 Model B
- Webcam USB (Jieli Technology USB PHY 2.0)
- 2 clés USB 64 Go (format exFAT)
- Alimentation 5V 2.5A minimum
- Carte SD 16 Go minimum


### Installation rapide
```bash
# 0. Installer git
sudo apt update
sudo apt install git -y

# 1. Cloner le dépôt
git clone https://github.com/TON_USERNAME/dashcam-raspberry-pi.git
cd dashcam-raspberry-pi

# 2. Installer les dépendances
sudo apt update
sudo apt install ffmpeg exfat-fuse exfat-utils -y

## 4. Installer et activer le service SystemD

Le service SystemD permet au script de démarrer automatiquement au boot du Raspberry Pi.
```bash
# Copier le fichier de configuration du service vers le dossier système
# Ce fichier dit à SystemD comment démarrer et gérer l'application
sudo cp dashcam.service /etc/systemd/system/

# Recharger la configuration de SystemD pour qu'il prenne en compte le nouveau service
sudo systemctl daemon-reload

# Activer le service pour qu'il démarre automatiquement au boot
# Cela crée un lien symbolique qui lance le service au démarrage
sudo systemctl enable dashcam.service

# Démarrer le service immédiatement (sans attendre le prochain redémarrage)
sudo systemctl start dashcam.service
