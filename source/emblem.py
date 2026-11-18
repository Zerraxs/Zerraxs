# Emblème 3D du profil : un « Z » doré au centre de trois anneaux qui tournent, sur fond transparent.
# Usage : blender -b -P emblem.py -- test <image.png> [instant 0..1] [taille]
#         blender -b -P emblem.py -- anim <dossier> <images> [taille] [échantillons]
#         blender -b -P emblem.py -- stl  <fichier.stl>
import bpy, bmesh, math, os, sys

argv = sys.argv[sys.argv.index('--') + 1:]
mode, out = argv[0], argv[1]
FONT = '/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreadventor-bold.otf'
TAU = math.tau

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def material(name, color, roughness, metallic=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat


# Or : valeurs de réflectance mesurées, en linéaire. Le Z est satiné, les anneaux polis.
GOLD = (1.0, 0.766, 0.336)
gold_satin = material('or satiné', GOLD, 0.26)
gold_polished = material('or poli', GOLD, 0.12)
gold_pale = material('or pâle', (1.0, 0.86, 0.57), 0.16)


def pivot(name, parent=None):
    empty = bpy.data.objects.new(name, None)
    scene.collection.objects.link(empty)
    if parent:
        empty.parent = parent
    return empty


def monogram(detail):
    """Le Z, debout face à l'objectif (qui regarde le long de +Y)."""
    font = bpy.data.fonts.load(FONT)
    curve = bpy.data.curves.new('Z', 'FONT')
    curve.body = 'Z'
    curve.font = font
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.extrude = 0.085
    curve.bevel_depth = 0.014
    curve.bevel_resolution = detail
    curve.resolution_u = 4 if detail < 2 else 12
    obj = bpy.data.objects.new('Z', curve)
    scene.collection.objects.link(obj)
    obj.rotation_euler = (math.radians(90), 0, 0)
    obj.scale = (3.35, 3.35, 3.35)
    obj.data.materials.append(gold_satin)
    return obj


def ring(name, radius, thickness, mat, parent):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    # Tore dans le plan XZ : vu de face, c'est un cercle.
    segments, sides = 160, 20
    for i in range(segments):
        a = TAU * i / segments
        for j in range(sides):
            b = TAU * j / sides
            r = radius + thickness * math.cos(b)
            bm.verts.new((r * math.cos(a), thickness * math.sin(b), r * math.sin(a)))
    bm.verts.ensure_lookup_table()
    for i in range(segments):
        for j in range(sides):
            v = [bm.verts[i * sides + j], bm.verts[((i + 1) % segments) * sides + j],
                 bm.verts[((i + 1) % segments) * sides + (j + 1) % sides], bm.verts[i * sides + (j + 1) % sides]]
            bm.faces.new(v)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.parent = parent
    obj.data.materials.append(mat)
    return obj


def write_stl(path):
    """Le monogramme seul, en STL ASCII : c'est lui que GitHub affiche dans sa visionneuse 3D."""
    obj = monogram(detail=0)
    # Dans la visionneuse, l'axe Z est vertical : le modèle y est posé debout, tel qu'il se lit.
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = obj.evaluated_get(depsgraph).to_mesh()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts, edges=bm.edges)
    # Un socle à six pans sous la lettre : posée dessus, elle se lit comme un objet, et la visionneuse a un sol.
    import mathutils
    lowest = min(vert.co.z for vert in bm.verts)
    centre = sum((vert.co.x for vert in bm.verts)) / len(bm.verts)
    plinth = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.86, radius2=0.80, depth=0.17,
                                   matrix=mathutils.Matrix.Translation((centre, 0, lowest - 0.085)))
    if len(argv) > 2 and argv[2] == 'retourné':
        # La même pièce vue de l'autre côté, si la visionneuse regarde le modèle par l'arrière.
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=mathutils.Matrix.Rotation(math.pi, 3, 'Z'))
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    lines = ['solid zerrax']
    for face in bm.faces:
        n = face.normal
        lines.append(f'facet normal {n.x:.4f} {n.y:.4f} {n.z:.4f}')
        lines.append('outer loop')
        for vert in face.verts:
            # Dixièmes de millimètre : le modèle mesure environ 30 unités de haut.
            lines.append(f'vertex {vert.co.x * 10:.3f} {vert.co.y * 10:.3f} {vert.co.z * 10:.3f}')
        lines.append('endloop')
        lines.append('endfacet')
    lines.append('endsolid zerrax')
    with open(path, 'w') as handle:
        handle.write('\n'.join(lines) + '\n')
    print(f'STL : {len(bm.faces)} triangles, {os.path.getsize(path)} octets')
    bm.free()


if mode == 'stl':
    write_stl(out)
    sys.exit(0)

# ——— Scène ———
swing = pivot('balancement')
z = monogram(detail=4)
z.parent = swing

rings = []
# Les anneaux sont des orbites inclinées autour du Z : chacune tourne sur elle-même face à l'objectif et respire
# de quelques degrés. Aucune ne se présente jamais par la tranche — un anneau vu par la tranche est un trait qui
# barre le Z (vertical, il en faisait un « $ ») — et leur inclinaison les garde toujours autour de la lettre.
# (rayon, épaisseur, matière, inclinaison en degrés, tours par boucle, phase)
for index, (radius, thickness, mat, tilt, turns, phase) in enumerate([
    (1.50, 0.046, gold_polished, 44, 1, 0.06),
    (1.72, 0.036, gold_pale, 52, -1, 0.40),
    (1.93, 0.030, gold_polished, 57, 1, 0.72),
]):
    spin = pivot(f'orbite {index}')
    lean = pivot(f'inclinaison {index}', spin)
    hoop = ring(f'anneau {index}', radius, thickness, mat, lean)
    # Une perle court sur chaque anneau : elle passe devant, puis derrière, et donne la profondeur.
    runner = pivot(f'course {index}', lean)
    bead_mesh = bpy.data.meshes.new(f'perle {index}')
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.098 - index * 0.010)
    bm.to_mesh(bead_mesh)
    bm.free()
    for poly in bead_mesh.polygons:
        poly.use_smooth = True
    bead = bpy.data.objects.new(f'perle {index}', bead_mesh)
    scene.collection.objects.link(bead)
    bead.parent = runner
    bead.location = (radius, 0, 0)
    bead.data.materials.append(gold_pale if mat is gold_polished else gold_polished)
    rings.append((spin, lean, runner, tilt, turns, phase))


def pose(t):
    """t de 0 à 1 : une boucle. Tout y fait un nombre entier de tours, la fin rejoint le début."""
    swing.rotation_euler = (0, 0, math.radians(22) * math.sin(TAU * t))
    for spin, lean, runner, tilt, turns, phase in rings:
        spin.rotation_euler = (0, TAU * (turns * t + phase), 0)
        lean.rotation_euler = (math.radians(tilt + 5 * math.sin(TAU * (t + phase))), 0, 0)
        runner.rotation_euler = (0, TAU * (2 * turns * t + phase * 3), 0)


# Lumière : trois boîtes à lumière que le métal reflète, et un ciel sombre pour les ombres du métal.
def softbox(name, location, rotation, size, power, color):
    light = bpy.data.lights.new(name, 'AREA')
    light.shape = 'RECTANGLE'
    light.size, light.size_y = size
    light.energy = power
    light.color = color
    obj = bpy.data.objects.new(name, light)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = tuple(math.radians(v) for v in rotation)
    return obj


softbox('principale', (-3.6, -5.2, 4.2), (58, 0, -34), (5.0, 3.0), 520, (1.0, 0.96, 0.90))
softbox('contre', (4.6, 3.4, 2.6), (-62, 0, 125), (3.5, 5.0), 620, (0.90, 0.94, 1.0))
softbox('débouchage', (3.8, -5.5, -2.0), (110, 0, 32), (4.0, 2.0), 150, (1.0, 0.88, 0.72))
softbox('bandeau', (0, -6.5, 1.6), (78, 0, 0), (9.0, 0.35), 70, (1.0, 0.97, 0.92))

world = bpy.data.worlds.new('atelier')
world.use_nodes = True
nodes, links = world.node_tree.nodes, world.node_tree.links
background = nodes['Background']
coords = nodes.new('ShaderNodeTexCoord')
separate = nodes.new('ShaderNodeSeparateXYZ')
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.25
ramp.color_ramp.elements[0].color = (0.012, 0.011, 0.010, 1)
ramp.color_ramp.elements[1].position = 0.85
ramp.color_ramp.elements[1].color = (0.16, 0.13, 0.09, 1)
links.new(coords.outputs['Generated'], separate.inputs['Vector'])
links.new(separate.outputs['Z'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], background.inputs['Color'])
background.inputs['Strength'].default_value = 1.0
scene.world = world

camera_data = bpy.data.cameras.new('objectif')
camera_data.lens = 85
camera = bpy.data.objects.new('objectif', camera_data)
scene.collection.objects.link(camera)
camera.location = (0, -10.4, 0.55)
camera.rotation_euler = (math.radians(87.0), 0, 0)
scene.camera = camera

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 60
scene.view_settings.view_transform = 'Standard'
try:
    scene.view_settings.look = 'Medium High Contrast'
except TypeError:
    pass

if mode == 'test':
    t = float(argv[2]) if len(argv) > 2 else 0.0
    size = int(argv[3]) if len(argv) > 3 else 420
    scene.cycles.samples = 48
    scene.render.resolution_x = scene.render.resolution_y = size
    pose(t)
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
elif mode == 'anim':
    count = int(argv[2])
    size = int(argv[3]) if len(argv) > 3 else 560
    scene.cycles.samples = int(argv[4]) if len(argv) > 4 else 96
    scene.render.resolution_x = scene.render.resolution_y = size
    os.makedirs(out, exist_ok=True)
    for frame in range(count):
        target = os.path.join(out, f'emblem_{frame:04d}.png')
        if os.path.exists(target):
            continue
        pose(frame / count)
        scene.render.filepath = target
        bpy.ops.render.render(write_still=True)
    print('rendu terminé')
