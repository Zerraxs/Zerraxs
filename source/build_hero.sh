#!/usr/bin/env bash
# Fabrique assets/hero.webp : l'emblème 3D animé, posé sur le fond du bandeau.
#   BLENDER=/chemin/vers/blender  bash build_hero.sh
# Trois temps : Blender rend les 120 images de l'emblème (une demi-heure sur huit cœurs ; les images déjà rendues
# sont gardées), Chromium rend le fond, ffmpeg assemble le tout. Le bandeau fait 1680 × 630, soit deux fois la
# largeur d'un README : il reste net sur un écran haute définition.
set -euo pipefail
cd "$(dirname "$0")"

BLENDER="${BLENDER:-blender}"
WORK="${WORK:-./build}"
FRAMES=120          # une boucle de six secondes à vingt images par seconde
SCALE=1.3125        # 1280 × 480 unités de dessin → 1680 × 630 pixels
EMBLEM=578          # côté de l'emblème, en pixels : 440 unités × SCALE

mkdir -p "$WORK"
"$BLENDER" -b -P emblem.py -- anim "$WORK/frames" "$FRAMES" "$EMBLEM" 80
python3 build_hero_bg.py "$WORK/hero-bg.svg"
node render-svg.mjs "$WORK/hero-bg.svg" "$WORK/hero-bg.png" "$SCALE"

# L'emblème se pose à 30 unités du bord gauche et 20 du haut (39 et 26 pixels). Les coins du panneau restent transparents.
ffmpeg -hide_banner -loglevel error -y \
  -loop 1 -framerate 20 -i "$WORK/hero-bg.png" \
  -framerate 20 -i "$WORK/frames/emblem_%04d.png" \
  -filter_complex "[0][1]overlay=39:26:shortest=1,format=yuva420p" \
  -c:v libwebp_anim -lossless 0 -q:v 80 -compression_level 6 -loop 0 -an ../assets/hero.webp
ls -la ../assets/hero.webp
