# Ligne « tapée au clavier » : quatre phrases, en français puis en anglais, qui s'écrivent et s'effacent.
# Tout est en CSS (aucun script ne s'exécute dans une image) : chaque lettre est visible entre l'instant où elle
# est tapée et celui où elle est effacée, par deux fenêtres d'opacité emboîtées qui partagent la même animation.
import sys
from svglib import CREAM, GOLD, face, panel, svg

# 840 unités de large, comme les autres panneaux : sur un téléphone le texte garde une dizaine de pixels.
W, H = 840, 80
X0, BASE, SIZE = 78, 50, 27
PHRASES = [
    'Sites et applications web sur mesure.',
    'Custom websites and web apps.',
    'Des bots sur mesure pour Discord.',
    'Custom bots for Discord.',
]
SLOT = 5.0                      # secondes par phrase
TOTAL = SLOT * len(PHRASES)
START, HOLD_UNTIL, ERASE = 0.25, 4.05, 0.45
WINDOW = 4.8                    # durée d'une fenêtre d'opacité : plus longue que la vie d'une lettre, plus courte qu'un créneau

mono = face('mono')
advance = mono.hmtx[mono.cmap[ord('a')]][0] * SIZE / mono.upm

symbols, used = [], {}
def glyph(char):
    if char not in used:
        used[char] = f'g{len(used)}'
        symbols.append(f'<path id="{used[char]}" d="{mono.path(char, SIZE, 0, 0)}"/>')
    return used[char]

letters, cursors, cursor_rules = [], [], []
for index, phrase in enumerate(PHRASES):
    count = len(phrase)
    begin = index * SLOT
    step = min(0.045, 2.5 / count)
    for position, char in enumerate(phrase):
        if char == ' ':
            continue
        typed = begin + START + position * step
        erased = begin + HOLD_UNTIL + (count - 1 - position) * (ERASE / count)
        # Fenêtre extérieure : s'ouvre quand la lettre est tapée. Fenêtre intérieure : se ferme quand elle est effacée.
        outer, inner = typed - TOTAL, erased - WINDOW - TOTAL
        letters.append(
            f'<g class="w" style="animation-delay:{outer:.3f}s"><use class="w" style="animation-delay:{inner:.3f}s" '
            f'href="#{glyph(char)}" x="{X0 + position * advance:.2f}" y="{BASE}"/></g>')
    # Le curseur de cette phrase : avance d'une lettre à la fois, attend, recule, puis disparaît jusqu'au tour suivant.
    pct = lambda seconds: f'{100 * seconds / TOTAL:.3f}%'
    end = count * advance
    typing_end = begin + START + count * step
    erase_start, erase_end = begin + HOLD_UNTIL, begin + HOLD_UNTIL + ERASE
    frames = [f'0%,{pct(begin + START)}{{transform:translateX(0);animation-timing-function:steps({count})}}',
              f'{pct(typing_end)},{pct(erase_start)}{{transform:translateX({end:.2f}px);animation-timing-function:steps({count})}}',
              f'{pct(erase_end)},100%{{transform:translateX(0)}}']
    shown = [f'0%,{pct(begin)}{{opacity:0}}', f'{pct(begin + 0.01)},{pct(begin + SLOT - 0.01)}{{opacity:1}}', f'{pct(begin + SLOT)},100%{{opacity:0}}']
    cursor_rules.append(f'@keyframes m{index}{{{"".join(frames)}}}@keyframes s{index}{{{"".join(shown)}}}')
    cursors.append(
        f'<g style="animation:s{index} {TOTAL}s linear infinite"><g style="animation:m{index} {TOTAL}s linear infinite">'
        f'<rect class="c" x="{X0 + 2}" y="{BASE - 24}" width="13" height="30" rx="2" fill="{GOLD}"/></g></g>')

ratio = 100 * WINDOW / TOTAL
style = (
    f'.w{{animation:w {TOTAL}s linear infinite}}'
    f'@keyframes w{{0%,{ratio:.3f}%{{opacity:1}}{ratio + 0.01:.3f}%,100%{{opacity:0}}}}'
    '.c{animation:b 1.06s steps(1) infinite}@keyframes b{0%{opacity:1}50%{opacity:0}}'
    + ''.join(cursor_rules)
    # Moins de mouvement demandé : la première phrase reste affichée, sans curseur.
    + '@media (prefers-reduced-motion: reduce){.w{opacity:0}.p0 .w{opacity:1}.k{display:none}}'
)
body = (
    panel(W, H, radius=20)
    + f'<defs>{"".join(symbols)}</defs>'
    # Invite de commande : un chevron d'or.
    + f'<path d="M38 26l14 14-14 14" fill="none" stroke="{GOLD}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    + f'<g fill="{CREAM}">'
)
# Les lettres sont regroupées par phrase pour le repli « moins de mouvement ».
offset = 0
for index, phrase in enumerate(PHRASES):
    count = sum(1 for char in phrase if char != ' ')
    body += f'<g class="p{index}">{"".join(letters[offset:offset + count])}</g>'
    offset += count
body += f'</g><g class="k">{"".join(cursors)}</g>'

title = 'Sites et applications web sur mesure, bots sur mesure pour Discord — Custom websites and web apps, custom bots for Discord'
open(sys.argv[1], 'w', encoding='utf-8').write(svg(W, H, body, title, style))
print(f'{len(letters)} lettres, {len(used)} glyphes distincts', file=sys.stderr)
