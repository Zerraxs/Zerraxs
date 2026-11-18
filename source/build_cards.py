# Les panneaux animés du profil : deux cartes (web, Discord), les outils, le pied de page.
# Tous font 840 unités de large : c'est la largeur d'un README sur ordinateur, et sur un téléphone (≈ 340 px)
# un texte de 26 unités reste lisible. Sortie dans le dossier donné en argument.
import os
import sys
from svglib import CREAM, GOLD, GOLD_LIGHT, MUTED, face, panel, svg, text

out = sys.argv[1]
W = 840
FACE_TOP, FACE_LEFT, FACE_RIGHT = '#1D2130', '#141722', '#0E1017'


def write(name, height, body, title, style):
    with open(os.path.join(out, name), 'w', encoding='utf-8') as handle:
        handle.write(svg(W, height, body, title, style))
    print(f'{name} : {os.path.getsize(os.path.join(out, name))} octets', file=sys.stderr)


def card_text(number, label, title, french, english, left=272):
    parts = [
        text('mono-bold', f'{number} · {label}', 17, left, 62, GOLD, tracking=3),
        text('display', title, 40, left - 2, 112, CREAM, tracking=0.5),
    ]
    for index, line in enumerate(french):
        parts.append(text('text-medium', line, 26, left, 156 + index * 33, CREAM, tracking=0.1))
    for index, line in enumerate(english):
        parts.append(text('text', line, 22, left, 232 + index * 28, MUTED, tracking=0.1))
    widest = max([face('text-medium').width(line, 26, 0.1) for line in french] + [face('text').width(line, 22, 0.1) for line in english])
    assert left + widest < W - 28, f'texte trop large : {widest:.0f}'
    return ''.join(parts)


# ——— Carte 1 : trois plaques isométriques empilées (interface, API, base de données) qui flottent ———
def slab(cx, cy, a=82, b=31, t=12):
    top = f'M{cx} {cy - b}L{cx + a} {cy}L{cx} {cy + b}L{cx - a} {cy}Z'
    left = f'M{cx - a} {cy}L{cx} {cy + b}L{cx} {cy + b + t}L{cx - a} {cy + t}Z'
    right = f'M{cx + a} {cy}L{cx} {cy + b}L{cx} {cy + b + t}L{cx + a} {cy + t}Z'
    return (f'<path d="{left}" fill="{FACE_LEFT}" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<path d="{right}" fill="{FACE_RIGHT}" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<path d="{top}" fill="{FACE_TOP}" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>')


def on_face(cx, cy, u, v, a=82, b=31):
    """Un point de la face supérieure d'une plaque, en coordonnées (u, v) de 0 à 1 le long de ses deux bords."""
    return cx + (u - v) * a, cy - b + (u + v) * b


def line(cx, cy, start, end, color, opacity, width=2.2):
    (x1, y1), (x2, y2) = on_face(cx, cy, *start), on_face(cx, cy, *end)
    return f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke="{color}" stroke-opacity="{opacity}" stroke-width="{width}" stroke-linecap="round"/>'


CX = 132
layers = []
for index, cy in enumerate((214, 148, 82)):          # du bas vers le haut : base de données, API, interface
    marks = ''
    if index == 0:                                    # base de données : cercles posés à plat
        for scale, opacity in ((0.62, 0.9), (0.36, 0.55)):
            marks += f'<ellipse cx="{CX}" cy="{cy}" rx="{82 * scale:.1f}" ry="{31 * scale:.1f}" fill="none" stroke="{GOLD}" stroke-opacity="{opacity}" stroke-width="2"/>'
    elif index == 1:                                  # API : trois points reliés
        marks += line(CX, cy, (0.24, 0.5), (0.76, 0.5), GOLD, 0.5, 1.8)
        for u in (0.24, 0.5, 0.76):
            x, y = on_face(CX, cy, u, 0.5)
            marks += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{GOLD_LIGHT}"/>'
    else:                                             # interface : une fenêtre et ses lignes de texte
        marks += line(CX, cy, (0.16, 0.22), (0.84, 0.22), GOLD, 0.95, 2.6)
        for v, end, opacity in ((0.44, 0.74, 0.75), (0.60, 0.56, 0.55), (0.76, 0.66, 0.4)):
            marks += line(CX, cy, (0.2, v), (end, v), CREAM, opacity, 2.2)
    layers.append(f'<g class="s s{index}">{slab(CX, cy)}{marks}</g>')

flows = ''.join(
    f'<path class="f" d="M{x} 94V226" stroke="{GOLD}" stroke-opacity="0.5" stroke-width="2" stroke-dasharray="3 8" stroke-linecap="round" style="animation-delay:{delay}s"/>'
    for x, delay in ((CX - 82, 0), (CX + 82, -0.6)))
web = (
    panel(W, 290, radius=24)
    + f'<ellipse cx="{CX}" cy="262" rx="88" ry="12" fill="{GOLD}" fill-opacity="0.10"/>'
    + flows + ''.join(layers)
    + card_text('01', 'WEB', 'Web full-stack',
                ['Sites et applications sur mesure,', 'de la base de données à l’interface.'],
                ['Custom websites and web apps,', 'from the database to the interface.'])
)
web_style = (
    '.s{animation:bob 4.4s ease-in-out infinite}.s1{animation-delay:-.5s}.s2{animation-delay:-1s}'
    '@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}'
    '.f{animation:flow 1.3s linear infinite}@keyframes flow{to{stroke-dashoffset:-11}}'
)
write('card-web.svg', 290, web,
      'Web full-stack — sites et applications sur mesure, de la base de données à l’interface · custom websites and web apps, from the database to the interface', web_style)

# ——— Carte 2 : un robot qui cligne des yeux, son antenne émet, une bulle « écrit » ———
bot = (
    panel(W, 290, radius=24)
    + f'<ellipse cx="128" cy="252" rx="84" ry="13" fill="{GOLD}" fill-opacity="0.10"/>'
    # Antenne et ondes.
    + f'<circle class="o" cx="118" cy="70" r="8" fill="none" stroke="{GOLD}" stroke-width="2"/>'
    + f'<circle class="o o2" cx="118" cy="70" r="8" fill="none" stroke="{GOLD}" stroke-width="2"/>'
    + f'<path d="M118 78V104" stroke="{GOLD}" stroke-width="3.5" stroke-linecap="round"/><circle cx="118" cy="70" r="7.5" fill="{GOLD_LIGHT}"/>'
    # Tête : une face arrière décalée lui donne son épaisseur.
    + f'<rect x="56" y="114" width="148" height="110" rx="24" fill="{FACE_RIGHT}" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="1.5"/>'
    + f'<rect x="44" y="104" width="148" height="110" rx="24" fill="{FACE_TOP}" stroke="{GOLD}" stroke-width="2.2"/>'
    + f'<rect x="34" y="142" width="10" height="30" rx="4" fill="{GOLD}" fill-opacity="0.85"/>'
    + f'<g fill="{CREAM}"><rect class="e" x="78" y="136" width="24" height="32" rx="11"/><rect class="e" x="134" y="136" width="24" height="32" rx="11"/></g>'
    + f'<path d="M96 186q22 13 44 0" fill="none" stroke="{GOLD}" stroke-width="3.5" stroke-linecap="round"/>'
    # Bulle de message : trois points qui s'allument tour à tour.
    + f'<path d="M190 44h44a12 12 0 0 1 12 12v18a12 12 0 0 1-12 12h-26l-12 12v-12h-6a12 12 0 0 1-12-12v-18a12 12 0 0 1 12-12z" fill="{FACE_LEFT}" stroke="{GOLD}" stroke-width="2" stroke-linejoin="round"/>'
    + ''.join(f'<circle class="d" cx="{x}" cy="65" r="4" fill="{GOLD_LIGHT}" style="animation-delay:{delay}s"/>' for x, delay in ((198, 0), (212, 0.22), (226, 0.44)))
    + card_text('02', 'DISCORD', 'Bots Discord',
                ['Des bots et des outils sur mesure', 'pour vos serveurs Discord.'],
                ['Custom bots and tools', 'for your Discord servers.'])
)
bot_style = (
    '.e{transform-box:fill-box;transform-origin:center;animation:blink 4.6s infinite}'
    '@keyframes blink{0%,44%,50%,100%{transform:scaleY(1)}47%{transform:scaleY(.12)}}'
    '.o{transform-box:fill-box;transform-origin:center;animation:wave 2.6s ease-out infinite}.o2{animation-delay:-1.3s}'
    '@keyframes wave{0%{transform:scale(1);opacity:.75}100%{transform:scale(3.4);opacity:0}}'
    '.d{animation:dot 1.5s ease-in-out infinite}@keyframes dot{0%,60%,100%{opacity:.25}30%{opacity:1}}'
)
write('card-discord.svg', 290, bot,
      'Bots Discord — des bots et des outils sur mesure pour vos serveurs Discord · custom bots and tools for your Discord servers', bot_style)

# ——— Les outils : des étiquettes dont le filet s'éclaire tour à tour ———
ROWS = [['TypeScript', 'React', 'Tailwind CSS', 'Node.js'], ['JavaScript', 'PostgreSQL', 'Express', 'discord.js']]
mono = face('mono')
chips, delay = '', 0.0
for row, names in enumerate(ROWS):
    x = 40
    for name in names:
        width = mono.width(name, 23) + 40
        y = 84 + row * 54
        chips += (f'<g class="t" style="animation-delay:{delay:.2f}s"><rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="40" rx="20" fill="{GOLD}" fill-opacity="0.06" stroke="{GOLD}" stroke-width="1.6"/></g>'
                  + text('mono', name, 23, x + 20, y + 28, CREAM))
        x += width + 14
        delay += 0.4
    assert x - 14 < W - 30, f'rangée trop large : {x:.0f}'
stack = (
    panel(W, 208, radius=24)
    + text('mono-bold', 'OUTILS · STACK', 17, 42, 56, GOLD, tracking=3)
    + f'<path d="M232 50H798" stroke="{GOLD}" stroke-opacity="0.25" stroke-width="1.5"/>'
    + chips
)
stack_style = ('.t{animation:lit 6.4s ease-in-out infinite}'
               '@keyframes lit{0%,18%,100%{opacity:.42}8%{opacity:1}}')
write('stack.svg', 208, stack, 'Outils — Stack : TypeScript, React, Tailwind CSS, Node.js, JavaScript, PostgreSQL, Express, discord.js', stack_style)

# ——— Pied de page : un filet d'or parcouru par un reflet, sans panneau (l'or se lit sur fond clair comme sombre) ———
label = '@Zerraxs'
label_width = face('mono-bold').width(label, 20, 2)
gap = label_width / 2 + 22
footer = (
    '<defs><linearGradient id="trait" x1="0" x2="1"><stop offset="0" stop-color="#D4AF37" stop-opacity="0"/>'
    '<stop offset="0.5" stop-color="#D4AF37"/><stop offset="1" stop-color="#D4AF37" stop-opacity="0"/></linearGradient>'
    f'<clipPath id="g"><rect x="40" y="26" width="{W / 2 - gap - 40:.1f}" height="8"/><rect x="{W / 2 + gap:.1f}" y="26" width="{W / 2 - gap - 40:.1f}" height="8"/></clipPath></defs>'
    f'<g clip-path="url(#g)"><rect x="40" y="29" width="{W - 80}" height="2" fill="#C39A2B" fill-opacity="0.6"/>'
    f'<rect class="r" x="-160" y="28" width="160" height="4" rx="2" fill="url(#trait)"/></g>'
    # Un or un peu plus soutenu : ce pied de page n'a pas de panneau, il doit se lire aussi sur fond blanc.
    + text('mono-bold', label, 20, W / 2, 37, '#C39A2B', tracking=2, anchor='middle')
)
footer_style = '.r{animation:run 5.5s linear infinite}@keyframes run{to{transform:translateX(1000px)}}'
write('footer.svg', 60, footer, '@Zerraxs', footer_style)
