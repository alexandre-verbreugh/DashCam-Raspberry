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

## Installation

Voir le fichier [DOCUMENTATION.md](DOCUMENTATION.md) pour l'installation complète.

### Installation rapide
```bash
# 1. Cloner le dépôt
git clone https://github.com/TON_USERNAME/dashcam-raspberry-pi.git
cd dashcam-raspberry-pi

# 2. Installer les dépendances
sudo apt update
sudo apt install ffmpeg exfat-fuse exfat-utils -y

# 3. Configurer les clés USB (voir documentation)

# 4. Installer le service
sudo cp dashcam.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dashcam.service
sudo systemctl start dashcam.service
