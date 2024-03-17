#!/bin/bash
# Ce script récupère tous les fichiers JPG du dossier ./orig, puis utilise
# ImageMagick pour convertir leur taille à une largeur de 300px et les
# enregistrer avec le même nom dans le dossier courant.

# Vérifie si ImageMagick est installé
if ! type "convert" > /dev/null; then
  echo "Le programme 'convert' d'ImageMagick n'est pas installé."
  exit 1
fi

# Boucle à travers tous les fichiers JPG dans le dossier ./orig
for file in ./orig/*.jpg; do
  # Obtient le nom du fichier sans le chemin
  filename=$(basename "$file")
  # Vérifie si le fichier existe déjà dans le répertoire courant
  if [ ! -e "$filename" ]; then
    # Utilise ImageMagick pour redimensionner l'image et l'enregistrer dans le dossier courant
    convert "$file" -resize 300x "$filename"
    # Affiche le nom de la miniature
    echo "Converti : $filename"
  fi
done
