"""Palace gate fly-through, rendered headless with Blender (bpy) + Cycles.

usage: python3 hall.py OUT_DIR N_FRAMES RES SAMPLES [first last]
Frames already on disk are skipped, so an interrupted run can be resumed.
"""
import math
import os
import sys

import bpy

out, N, RES, SAMPLES = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
first = int(sys.argv[5]) if len(sys.argv) > 5 else 0
last = int(sys.argv[6]) if len(sys.argv) > 6 else N - 1
os.makedirs(out, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection

# ---------- measurements (metres) ----------
OW, OH = 2.2, 2.2 * 1.58          # arch opening: same ogee proportions as the gate drawn on the page
ARCH_Y = [0.0, 5.0, 10.0, 15.0]   # the gate, then three arches down the hall
END_Y = 21.0                      # wall of light at the far end
HALL_W, HALL_H = 6.4, 6.2
EYE = OH / 2                      # camera rides at the middle of the opening, so the arch stays centred
LENS, SENSOR = 28.0, 36.0
START_Y = -OW / (0.22 * 2 * (SENSOR / 2 / LENS))   # gate opening is 22% of frame width on frame 0
STOP_Y = END_Y - 0.35


def ogee(w, h, n=14):
    """Outline of the opening from left foot, over the point, to right foot."""
    pts = [(-w / 2, 0.0), (-w / 2, h * 0.5)]
    p0, p1, p2, p3 = (-w / 2, h * 0.5), (-w / 2, h * 0.86), (-w * 0.1, h * 0.8), (0.0, h)
    for i in range(1, n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    right = [(-x, z) for x, z in reversed(pts[:-1])]
    return pts + right


def material(name, color, rough=0.8, emit=None, strength=0.0, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


STONE = material("sandstone", (0.50, 0.25, 0.12), 0.85)
STONE_IN = material("sandstone_inner", (0.46, 0.22, 0.11), 0.8)
FLOOR = material("marble", (0.42, 0.30, 0.22), 0.12)
BRASS = material("brass", (0.80, 0.55, 0.20), 0.3, metallic=1.0)
MARI_A = material("marigold_a", (1.0, 0.36, 0.02), 0.6)
MARI_B = material("marigold_b", (1.0, 0.62, 0.05), 0.6)
BULB = material("bulb", (1, 0.8, 0.5), 0.5, emit=(1.0, 0.72, 0.34), strength=7.0)
FLAME = material("flame", (1, 0.8, 0.5), 0.5, emit=(1.0, 0.62, 0.22), strength=14.0)
GLOW = material("endlight", (1, 1, 1), 0.5, emit=(1.0, 0.86, 0.62), strength=2.6)


def add(name, verts, faces, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    col.objects.link(ob)
    return ob


def arch_wall(y, half_w, height, thick, mat):
    """A wall across the hall with the ogee opening cut out. Built as quads column by column."""
    o = ogee(OW, OH)
    xs = sorted(set([-half_w, half_w] + [p[0] for p in o]))

    def top_of_hole(x):
        if abs(x) >= OW / 2 - 1e-6:
            return 0.0 if abs(x) > OW / 2 + 1e-6 else OH * 0.5
        best = 0.0
        for (x0, z0), (x1, z1) in zip(o, o[1:]):
            if x0 != x1 and min(x0, x1) - 1e-9 <= x <= max(x0, x1) + 1e-9:
                best = max(best, z0 + (z1 - z0) * (x - x0) / (x1 - x0))
        return best

    verts, faces = [], []
    for side, yy in enumerate((y, y + thick)):
        for x in xs:
            inside = abs(x) < OW / 2 - 1e-6
            zb = top_of_hole(x) if (inside or abs(abs(x) - OW / 2) < 1e-6) else 0.0
            verts += [(x, yy, zb), (x, yy, height)]
    n = len(xs)
    for s in range(2):
        for i in range(n - 1):
            a = s * 2 * n + i * 2
            xm = (xs[i] + xs[i + 1]) / 2
            if abs(xm) < OW / 2:      # column above the opening
                faces.append((a, a + 2, a + 3, a + 1))
            else:                     # full-height column beside it
                v0 = len(verts)
                yy = y + s * thick
                verts += [(xs[i], yy, 0), (xs[i + 1], yy, 0), (xs[i + 1], yy, height), (xs[i], yy, height)]
                faces.append((v0, v0 + 1, v0 + 2, v0 + 3))
    # the reveal: inner surface of the opening, joining front to back
    for (x0, z0), (x1, z1) in zip(o, o[1:]):
        v0 = len(verts)
        verts += [(x0, y, z0), (x1, y, z1), (x1, y + thick, z1), (x0, y + thick, z0)]
        faces.append((v0, v0 + 1, v0 + 2, v0 + 3))
    return add("arch", verts, faces, mat)


def quad(name, pts, mat):
    return add(name, pts, [(0, 1, 2, 3)], mat)


ball = bpy.data.meshes.new("ball")
import bmesh  # noqa: E402
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
bm.to_mesh(ball)
bm.free()
for p in ball.polygons:
    p.use_smooth = True


def sphere(loc, r, mat):
    me = ball.copy()
    me.materials.append(mat)
    ob = bpy.data.objects.new("s", me)
    ob.location, ob.scale = loc, (r, r, r)
    col.objects.link(ob)
    return ob


def point(loc, watts, color=(1.0, 0.66, 0.36), radius=0.08):
    li = bpy.data.lights.new("p", "POINT")
    li.energy, li.color, li.shadow_soft_size = watts, color, radius
    ob = bpy.data.objects.new("p", li)
    ob.location = loc
    col.objects.link(ob)


# ---------- build ----------
arch_wall(ARCH_Y[0], 30.0, 24.0, 0.7, STONE)                 # the palace front: big enough to fill frame 0
for y in ARCH_Y[1:]:
    arch_wall(y, HALL_W / 2, HALL_H, 0.5, STONE_IN)
h = HALL_W / 2
quad("floor", [(-30, -30, 0), (30, -30, 0), (30, END_Y, 0), (-30, END_Y, 0)], FLOOR)
quad("left", [(-h, 0.7, 0), (-h, END_Y, 0), (-h, END_Y, HALL_H), (-h, 0.7, HALL_H)], STONE_IN)
quad("right", [(h, END_Y, 0), (h, 0.7, 0), (h, 0.7, HALL_H), (h, END_Y, HALL_H)], STONE_IN)
quad("ceil", [(-h, 0.7, HALL_H), (-h, END_Y, HALL_H), (h, END_Y, HALL_H), (h, 0.7, HALL_H)], STONE_IN)
quad("end", [(-h, END_Y, 0), (h, END_Y, 0), (h, END_Y, HALL_H), (-h, END_Y, HALL_H)], GLOW)

outline = ogee(OW + 0.5, OH + 0.3, 10)
for k, y in enumerate(ARCH_Y):
    front = y - 0.04
    for i in range(0, len(outline)):                          # string of bulbs round every arch
        x, z = outline[i]
        if i % 1 == 0:
            sphere((x, front, z), 0.035, BULB)
    if k == 0:
        continue
    # marigold swag across the arch and a strand down each side
    for i in range(27):
        t = i / 26
        x = -1.45 + 2.9 * t
        z = OH + 1.25 - 0.85 * math.sin(math.pi * t)
        sphere((x, front - 0.06, z), 0.075, MARI_A if i % 2 else MARI_B)
    for sx in (-1.45, 1.45):
        for i in range(1, 15):
            sphere((sx, front - 0.06, OH + 1.25 - i * 0.16), 0.07, MARI_B if i % 2 else MARI_A)

for k in range(len(ARCH_Y)):                                  # between arches: lantern above, diyas along the floor
    y0 = ARCH_Y[k] + 0.7
    y1 = ARCH_Y[k + 1] if k + 1 < len(ARCH_Y) else END_Y
    ym = (y0 + y1) / 2
    sphere((0, ym, HALL_H - 1.1), 0.16, BULB)
    sphere((0, ym, HALL_H - 0.82), 0.09, BRASS)
    point((0, ym, HALL_H - 1.5), 26)
    n = 4
    for i in range(n):
        yy = y0 + (y1 - y0) * (i + 0.5) / n
        for sx in (-h + 0.45, h - 0.45):
            sphere((sx, yy, 0.05), 0.05, FLAME)
            sphere((sx, yy, 0.0), 0.11, BRASS)
        if i % 2 == 0:
            point((-h + 0.6, yy, 0.35), 5)
            point((h - 0.6, yy, 0.35), 5)

# the lit palace front, as on the page: floodlit from below and in front
area = bpy.data.lights.new("flood", "AREA")
area.energy, area.color, area.size = 1500, (1.0, 0.70, 0.42), 14
ao = bpy.data.objects.new("flood", area)
ao.location = (0, -9, 0.6)
ao.rotation_euler = (math.radians(78), 0, 0)
col.objects.link(ao)

world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.005, 0.016, 1)
scene.world = world

cam = bpy.data.cameras.new("cam")
cam.lens, cam.sensor_width, cam.clip_start, cam.clip_end = LENS, SENSOR, 0.05, 200
co = bpy.data.objects.new("cam", cam)
co.rotation_euler = (math.radians(90), 0, 0)
col.objects.link(co)
scene.camera = co

r = scene.render
r.engine = "CYCLES"
r.resolution_x = r.resolution_y = RES
r.resolution_percentage = 100
r.image_settings.file_format = "JPEG"
r.image_settings.quality = 86
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.device = "CPU"
scene.cycles.max_bounces = 5
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.05
r.threads_mode = "AUTO"
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception as e:
    print("look not set", e)

for i in range(first, last + 1):
    path = os.path.join(out, f"h{i:02d}.jpg")
    if os.path.exists(path):
        continue
    t = i / (N - 1)
    co.location = (0, START_Y + (STOP_Y - START_Y) * t, EYE)
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    print("frame", i, flush=True)
