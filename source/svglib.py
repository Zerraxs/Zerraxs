# Texte converti en tracés : un SVG affiché comme image ne charge aucune police, et celles du lecteur changeraient
# les largeurs. Les contours viennent de polices libres installées sur le serveur (TeX Gyre Adventor, Lato, DejaVu).
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = {
    'display': '/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreadventor-bold.otf',
    'display-regular': '/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreadventor-regular.otf',
    'text': '/usr/share/fonts/truetype/lato/Lato-Regular.ttf',
    'text-medium': '/usr/share/fonts/truetype/lato/Lato-Medium.ttf',
    'text-bold': '/usr/share/fonts/truetype/lato/Lato-Bold.ttf',
    'mono': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    'mono-bold': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
}

# Palette « encre et or ».
INK, INK_SOFT, INK_LINE = '#0E1014', '#171A22', '#262A35'
GOLD, GOLD_LIGHT, GOLD_DEEP = '#D4AF37', '#F3D98A', '#9C7A1E'
CREAM, MUTED = '#EDE6D3', '#9A9484'


class Face:
    def __init__(self, key):
        self.font = TTFont(FONTS[key])
        self.cmap = self.font.getBestCmap()
        self.glyphs = self.font.getGlyphSet()
        self.upm = self.font['head'].unitsPerEm
        self.hmtx = self.font['hmtx']
        self._pairs = self._pair_tables()

    def _pair_tables(self):
        if 'GPOS' not in self.font:
            return []
        gpos = self.font['GPOS'].table
        wanted = set()
        for record in gpos.FeatureList.FeatureRecord:
            if record.FeatureTag == 'kern':
                wanted.update(record.Feature.LookupListIndex)
        tables = []
        for index in sorted(wanted):
            lookup = gpos.LookupList.Lookup[index]
            for sub in lookup.SubTable:
                kind = lookup.LookupType
                if kind == 9:
                    kind, sub = sub.ExtensionLookupType, sub.ExtSubTable
                if kind == 2:
                    tables.append(sub)
        return tables

    def kern(self, left, right):
        """Crénage d'une paire de glyphes, en unités de la police (première table qui couvre la paire)."""
        for sub in self._pairs:
            glyphs = sub.Coverage.glyphs
            if left not in glyphs:
                continue
            if sub.Format == 1:
                for record in sub.PairSet[glyphs.index(left)].PairValueRecord:
                    if record.SecondGlyph == right:
                        return getattr(record.Value1, 'XAdvance', 0) or 0
            else:
                first = sub.ClassDef1.classDefs.get(left, 0)
                second = sub.ClassDef2.classDefs.get(right, 0)
                value = sub.Class1Record[first].Class2Record[second].Value1
                amount = getattr(value, 'XAdvance', 0) or 0 if value else 0
                if amount:
                    return amount
        return 0

    def layout(self, text, size, tracking=0.0):
        """Positions (glyphe, x) et largeur totale, à la taille demandée."""
        scale = size / self.upm
        x, placed, previous = 0.0, [], None
        for char in text:
            name = self.cmap[ord(char)]
            if previous is not None:
                x += self.kern(previous, name) * scale + tracking
            placed.append((name, x))
            x += self.hmtx[name][0] * scale
            previous = name
        return placed, x

    def width(self, text, size, tracking=0.0):
        return self.layout(text, size, tracking)[1]

    def path(self, text, size, x=0.0, y=0.0, tracking=0.0, anchor='start'):
        """Le tracé SVG du texte, ligne de base en (x, y)."""
        placed, width = self.layout(text, size, tracking)
        if anchor == 'middle':
            x -= width / 2
        elif anchor == 'end':
            x -= width
        scale = size / self.upm
        commands = []
        for name, offset in placed:
            pen = SVGPathPen(self.glyphs, ntos=lambda value: f'{value:.2f}'.rstrip('0').rstrip('.'))
            self.glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x + offset, y)))
            drawn = pen.getCommands()
            if drawn:
                commands.append(drawn)
        return ''.join(commands)


_faces = {}


def face(key):
    if key not in _faces:
        _faces[key] = Face(key)
    return _faces[key]


def text(key, content, size, x, y, fill, tracking=0.0, anchor='start', extra=''):
    return f'<path d="{face(key).path(content, size, x, y, tracking, anchor)}" fill="{fill}"{(" " + extra) if extra else ""}/>'


def panel(width, height, radius=26, ident='p'):
    """Le fond commun des visuels : un panneau d'encre aux coins arrondis, bordé d'un filet d'or discret."""
    return (
        f'<defs><linearGradient id="{ident}-bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#15171E"/><stop offset="1" stop-color="#0B0C10"/></linearGradient></defs>'
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{radius}" fill="url(#{ident}-bg)"/>'
        f'<rect x="0.75" y="0.75" width="{width - 1.5}" height="{height - 1.5}" rx="{radius}" fill="none" stroke="{GOLD}" stroke-opacity="0.30" stroke-width="1.5"/>'
    )


def svg(width, height, body, title, style=''):
    """Un SVG autonome. Les animations s'arrêtent pour qui a demandé moins de mouvement."""
    reduced = '@media (prefers-reduced-motion: reduce){*{animation:none!important}}'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{title}">'
        f'<title>{title}</title><style>{style}{reduced}</style>{body}</svg>\n'
    )
