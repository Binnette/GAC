#!/bin/bash
# Ce script récupère tous les fichiers JPG du dossier ./orig, puis utilise
# ImageMagick pour convertir leur taille à une largeur de 300px et les
# enregistrer avec le même nom dans le dossier courant.

# Détermine si le script est exécuté sur Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then

  echo "Environnement: Windows"
  convert_cmd="magick convert"
  # Vérifie si ImageMagick est installé
  if ! type "magick" > /dev/null; then
    echo "La commande 'magick' d'ImageMagick n'est pas installé."
    exit 1
  fi

else

  echo "Environnement: Linux"
  convert_cmd="convert"
  # Vérifie si ImageMagick est installé
  if ! type "convert" > /dev/null; then
    echo "La commande 'convert' d'ImageMagick n'est pas installée."
    exit 1
  fi

fi

# Boucle à travers tous les fichiers JPG dans le dossier ./orig
for file in ./orig/*.jpg; do
  # Obtient le nom du fichier sans le chemin
  filename=$(basename "$file")
  # Vérifie si le fichier existe déjà dans le répertoire courant
  if [ ! -e "$filename" ]; then
    # Utilise ImageMagick pour redimensionner l'image et l'enregistrer dans le dossier courant
    $convert_cmd "$file" -resize 300x "$filename"
    # Affiche le nom de la miniature
    echo "Converti $file vers $filename"
  fi
done
