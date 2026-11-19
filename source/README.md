# Sources des visuels

Tout ce qui s’affiche sur le profil est fabriqué ici, sans service extérieur : rien ne dépend d’un site tiers pour s’afficher.

| Fichier | Ce qu’il produit |
| --- | --- |
| `emblem.py` | L’emblème 3D (Blender, moteur Cycles) : les images de l’animation, et le modèle `monogram.stl` affiché dans la visionneuse 3D du README. |
| `build_hero_bg.py` | Le fond fixe du bandeau : nom, accroches, repères d’angle. |
| `build_hero.sh` | Le bandeau animé `assets/hero.webp` : l’emblème posé sur son fond. |
| `build_typing.py` | La ligne tapée au clavier, `assets/typing.svg`. |
| `build_cards.py` | Les deux cartes, les outils et le pied de page. |
| `svglib.py` | Palette, panneau commun, et conversion des textes en tracés. |

Les textes des images sont convertis en tracés : une image SVG ne charge aucune police, et celles du lecteur changeraient les largeurs. Polices utilisées, toutes libres : TeX Gyre Adventor (nom et titres), Lato (textes), DejaVu Sans Mono (lignes de code). Leurs auteurs et leurs licences sont dans [FONTS.md](FONTS.md).

Les animations des SVG sont en CSS, sans script, et s’arrêtent pour qui a demandé moins de mouvement à son système.

## Refaire les visuels

Il faut Blender 4, Python 3 avec `fonttools`, `ffmpeg` (avec `libwebp`), Node.js et Chromium.

`render-svg.mjs` pilote Chromium avec `playwright-core`, à installer une fois dans ce dossier :

```bash
npm install playwright-core
```

Deux variables indiquent où trouver les programmes quand ils ne sont pas à leur place habituelle : `BLENDER` (par défaut `blender`) et `CHROMIUM` (par défaut `/usr/bin/chromium`).

```bash
python3 build_typing.py ../assets/typing.svg
python3 build_cards.py ../assets
bash build_hero.sh
```

Pour changer un texte, modifiez-le dans le script correspondant puis relancez-le.
