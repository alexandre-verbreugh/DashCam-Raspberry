#!/bin/bash
# ============================================================================
# SCRIPT DE NETTOYAGE AUTOMATIQUE DES VIDÉOS - VERSION GLOBALE
# ============================================================================
# Ce script supprime les vidéos les plus anciennes en considérant
# LES DEUX CLÉS ENSEMBLE (pas séparément)
#
# Exemple : Si MAX_VIDEOS=100 et qu'il y a 120 vidéos au total
# (60 sur usb1 + 60 sur usb2), il supprimera les 20 plus anciennes
# peu importe sur quelle clé elles se trouvent
# ============================================================================

# ---------- CONFIGURATION ----------

# Liste des chemins vers les deux clés USB
USB_PATHS=("/mnt/usb1" "/mnt/usb2")

# Nombre TOTAL maximum de vidéos à conserver sur LES DEUX CLÉS
# Exemple : 100 = maximum 100 vidéos au total (réparties sur usb1 et usb2)
MAX_VIDEOS=100

# ---------- VÉRIFICATION DES CLÉS MONTÉES ----------

# Créer une liste des clés qui sont effectivement montées
MOUNTED_PATHS=()
for USB_PATH in "${USB_PATHS[@]}"; do
    # Vérifier que le chemin existe et est monté
    if [ -d "$USB_PATH" ] && mountpoint -q "$USB_PATH"; then
        MOUNTED_PATHS+=("$USB_PATH")  # Ajouter à la liste des clés montées
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $USB_PATH non monté, ignoré"
    fi
done

# Si aucune clé n'est montée, arrêter le script
if [ ${#MOUNTED_PATHS[@]} -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Aucune clé USB montée, arrêt du nettoyage"
    exit 0
fi

# ---------- COMPTAGE GLOBAL DES VIDÉOS ----------

# Compter le nombre TOTAL de vidéos sur toutes les clés montées
# Cette commande combine les résultats de find sur toutes les clés
TOTAL_VIDEOS=$(find "${MOUNTED_PATHS[@]}" -maxdepth 1 -name "video_*.avi" 2>/dev/null | wc -l)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Total de vidéos sur toutes les clés: $TOTAL_VIDEOS"

# ---------- VÉRIFICATION : Faut-il nettoyer ? ----------

# Si le nombre total de vidéos est inférieur ou égal à MAX_VIDEOS, rien à faire
if [ "$TOTAL_VIDEOS" -le "$MAX_VIDEOS" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pas de nettoyage nécessaire (limite: $MAX_VIDEOS)"
    exit 0
fi

# ---------- CALCUL : Combien de vidéos à supprimer ? ----------

# Calculer combien de vidéos supprimer pour revenir à MAX_VIDEOS
TO_DELETE=$((TOTAL_VIDEOS - MAX_VIDEOS))

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Suppression de $TO_DELETE anciennes vidéos..."

# ---------- SUPPRESSION DES PLUS ANCIENNES ----------

# Cette commande complexe fonctionne ainsi :
#
# 1. find "${MOUNTED_PATHS[@]}" -maxdepth 1 -name "video_*.avi" -type f -printf '%T+ %p\n' 2>/dev/null
#    Cherche TOUTES les vidéos sur TOUTES les clés montées
#    Affiche pour chaque fichier : date_de_modification chemin_complet
#    Exemple :
#    2025-10-03+14:35:20 /mnt/usb1/video_20251003_143520.avi
#    2025-10-03+14:40:25 /mnt/usb2/video_20251003_144025.avi
#    2025-10-04+09:15:10 /mnt/usb1/video_20251004_091510.avi
#
# 2. sort
#    Trie TOUTES les vidéos par date (les plus anciennes en premier)
#    Peu importe sur quelle clé elles se trouvent
#
# 3. head -n "$TO_DELETE"
#    Garde seulement les N plus anciennes (à supprimer)
#
# 4. cut -d' ' -f2-
#    Extrait le chemin du fichier (enlève la date)
#
# 5. while read file; do ... done
#    Pour chaque fichier à supprimer :

find "${MOUNTED_PATHS[@]}" -maxdepth 1 -name "video_*.avi" -type f -printf '%T+ %p\n' 2>/dev/null | \
sort | head -n "$TO_DELETE" | cut -d' ' -f2- | \
while read file; do
    # Supprimer le fichier (peu importe sur quelle clé il se trouve)
    rm -f "$file"
    
    # Afficher quel fichier a été supprimé et de quelle clé
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Supprimé: $(basename "$file") de $(dirname "$file")"
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Nettoyage terminé. Vidéos restantes: $MAX_VIDEOS"

# ============================================================================
# FIN DU SCRIPT
# ============================================================================
# Résultat : Les vidéos les plus anciennes sont supprimées EN PREMIER,
# peu importe sur quelle clé USB elles se trouvent.
# Les vidéos les plus récentes sont toujours conservées.
# ============================================================================
