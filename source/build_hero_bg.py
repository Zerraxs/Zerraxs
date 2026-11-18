# Fond fixe du bandeau : panneau d'encre, halo derrière l'emblème, nom et accroches. L'emblème 3D animé
# vient s'y poser ensuite (build_hero.sh). Sortie : hero-bg.svg, rendu en PNG par render-svg.mjs.
import sys
from svglib import CREAM, GOLD, GOLD_DEEP, GOLD_LIGHT, MUTED, face, panel, text

W, H = 1280, 480
LEFT = 520  # bord gauche du bloc de texte
# Sur un téléphone le bandeau s'affiche au quart de sa taille : le nom et l'accroche sont donc composés très grand,
# et tout ce qui serait illisible à cette échelle a été retiré.
wordmark = face('display')
size, tracking = 150, 8
width = wordmark.width('ZERRAX', size, tracking)

body = [
    '<defs>'
    '<radialGradient id="halo" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(250 242) scale(340)">'
    f'<stop offset="0" stop-color="{GOLD}" stop-opacity="0.20"/><stop offset="0.55" stop-color="{GOLD}" stop-opacity="0.05"/>'
    f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>'
    '<linearGradient id="or" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{GOLD_LIGHT}"/><stop offset="0.48" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_DEEP}"/></linearGradient>'
    f'<clipPath id="cadre"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26"/></clipPath>'
    '</defs>',
    panel(W, H),
    f'<g clip-path="url(#cadre)"><rect width="{W}" height="{H}" fill="url(#halo)"/></g>',
    # Repères d'angle, comme sur un plan : ils cadrent le bloc de texte sans l'encombrer.
    f'<g stroke="{GOLD}" stroke-opacity="0.55" stroke-width="2.5" fill="none">'
    f'<path d="M{LEFT} 84v-18h18"/><path d="M1212 66h18v18"/><path d="M1230 396v18h-18"/><path d="M{LEFT + 18} 414h-18v-18"/></g>',
    text('mono', '@Zerraxs', 28, LEFT + 36, 124, GOLD, tracking=2),
    f'<path d="{wordmark.path("ZERRAX", size, LEFT + 30, 262, tracking)}" fill="url(#or)"/>',
    f'<rect x="{LEFT + 36}" y="290" width="84" height="4" rx="2" fill="{GOLD}"/>',
    text('text-medium', 'Web full-stack · Bots Discord', 43, LEFT + 36, 350, CREAM, tracking=0.3),
    text('text', 'Développeur · Developer', 31, LEFT + 36, 394, MUTED, tracking=0.4),
]

print(f'largeur du nom : {width:.0f} px ; accroche : {face("text-medium").width("Web full-stack · Bots Discord", 43, 0.3):.0f} px (place disponible : {1230 - LEFT - 36})', file=sys.stderr)
out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">' + ''.join(body) + '</svg>\n')
open(sys.argv[1], 'w', encoding='utf-8').write(out)
