#!/bin/bash
# This script gets all JPG files from the ./orig folder, then uses image magick to convert their size to width 300px and save them with the same name in the . folder

# Loop through all JPG files in the ./orig folder
for file in ./orig/*.jpg; do
  # Get the file name without the path
  filename=$(basename "$file")
  # Use image magick to resize the image and save it in the . folder
  convert "$file" -resize 400x "$filename"
done
