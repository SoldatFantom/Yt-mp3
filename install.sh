
#!/bin/bash

# Vérifier si le script est exécuté avec les droits d'administrateur
if [ "$EUID" -ne 0 ]; then
    echo "Veuillez exécuter ce script avec sudo"
    exit 1
fi

echo "Installation de yt-mp3"

# Installer les dépendances nécessaires

# Copier des fichiers dans les répertoires appropriés
pip install yt-dlp
pip install pydub
pip install pyinstaller
pyinstaller --onefile yt-mp3.py
cp dist/yt-mp3 /usr/local/bin/yt-mp3
chmod +x /usr/local/bin/yt-mp3
echo "Installation terminée !"
cd ..
sudo rm -rf Yt-mp3

