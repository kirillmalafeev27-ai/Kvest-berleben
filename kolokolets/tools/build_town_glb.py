#!/usr/bin/env python3
"""
КОЛОКОЛЕЦ — процедурная сборка города в один GLB.

Планировка = kolokolets/planirovka_goroda.html и референс-рендер:
  центр      — часовая башня на круглой площади;
  кольцо     — рынок-палатки вокруг площади, кольцевая дорога;
  вокруг     — дома девяти жителей (пекарня, кафе, ратуша, почта, будка,
               мастерская, дом смотрителя), ветряная и водяная мельницы;
  юг         — ворота (приход Алекса в день 1), главная улица;
  север      — холм с беседкой звездочёта, серпантин-тропа;
  запад      — река с мостами; повсюду деревья, камни, заборы, фонари.

Всё — примитивы (box/prism/cyl/cone/sphere) с flat-цветами: тот же стиль,
что референс. Скрипт заодно является МАНИФЕСТОМ РАСКЛАДКИ: координаты и
повороты ниже можно заселить моделями Kenney/KayKit/Tiny Treats один к одному.

Запуск:  python3 build_town_glb.py   →  ../kolokolets_town.glb
Зависимости: numpy, trimesh.
Координаты: Y вверх, земля XZ. Юг = +Z (там ворота), север = −Z (там холм).
"""

import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix

# ---------------------------------------------------------------- палитра
C = {
    "grass":      "7CB158", "grass_dark": "6C9A4C", "cliff": "A98C5B",
    "path":       "D9C08F", "plaza":      "D6BD8E", "plaza2": "C9AC79",
    "wall":       "F2EAD8", "wall2":      "E8DBC0",
    "roof_red":   "C94F43", "roof_teal":  "2FA79B", "roof_blue": "3F6BB5",
    "roof_brown": "8A5A3C",
    "wood":       "A97B4F", "wood_dark":  "7A5233", "fence": "B98A5C",
    "leaf":       "57A05A", "leaf_dark":  "3E7D46", "pine": "3C8552",
    "rock":       "AEB6C4", "water":      "4FA3D8",
    "door":       "6B4A2E", "window":     "E9B44C", "lamp": "F2C14E",
    "dark":       "4A4038", "white":      "F7F3E8", "clock": "F7F3E8",
    "stone":      "C7BCA4",
}
def col(k):
    h = C[k]
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)])

BUCKETS = {}          # цвет → список мешей (склеим по цветам → компактный GLB)

def add(mesh, color_key):
    BUCKETS.setdefault(color_key, []).append(mesh)

# ------------------------------------------------------------- примитивы
def box(w, h, d, at=(0, 0, 0), yaw=0.0):
    m = trimesh.creation.box(extents=[w, h, d])
    m.apply_translation([0, h / 2, 0])
    if yaw:
        m.apply_transform(rotation_matrix(yaw, [0, 1, 0]))
    m.apply_translation(at)
    return m

def prism(w, h, d, at=(0, 0, 0), yaw=0.0):
    """Треугольная призма-крыша: конёк вдоль X, основание w×d, высота h."""
    x, z = w / 2, d / 2
    v = np.array([[-x, 0, -z], [x, 0, -z], [x, 0, z], [-x, 0, z],
                  [-x, h, 0], [x, h, 0]])
    f = np.array([[0, 1, 4], [1, 5, 4], [2, 3, 5], [3, 4, 5],
                  [1, 2, 5], [0, 4, 3], [0, 3, 1], [1, 3, 2]])
    m = trimesh.Trimesh(vertices=v, faces=f, process=False)
    if yaw:
        m.apply_transform(rotation_matrix(yaw, [0, 1, 0]))
    m.apply_translation(at)
    return m

def pyramid(w, h, d, at=(0, 0, 0), yaw=0.0):
    x, z = w / 2, d / 2
    v = np.array([[-x, 0, -z], [x, 0, -z], [x, 0, z], [-x, 0, z], [0, h, 0]])
    f = np.array([[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4],
                  [0, 3, 1], [1, 3, 2]])
    m = trimesh.Trimesh(vertices=v, faces=f, process=False)
    if yaw:
        m.apply_transform(rotation_matrix(yaw, [0, 1, 0]))
    m.apply_translation(at)
    return m

def cyl(r, h, at=(0, 0, 0), seg=12):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=seg)
    m.apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))
    m.apply_translation([0, h / 2, 0])
    m.apply_translation(at)
    return m

def cone(r, h, at=(0, 0, 0), seg=10):
    m = trimesh.creation.cone(radius=r, height=h, sections=seg)
    m.apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))
    m.apply_translation(at)
    return m

def ring(r_in, r_out, h, at=(0, 0, 0), seg=28):
    m = trimesh.creation.annulus(r_min=r_in, r_max=r_out, height=h, sections=seg)
    m.apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))
    m.apply_translation([0, h / 2, 0])
    m.apply_translation(at)
    return m

def ball(r, at=(0, 0, 0), sub=1, squash=1.0):
    m = trimesh.creation.icosphere(subdivisions=sub, radius=r)
    m.apply_scale([1, squash, 1])
    m.apply_translation(at)
    return m

def yaw_to_center(x, z):
    """Поворот, чтобы «лицо» (грань +Z) смотрело на башню в (0,0)."""
    return np.arctan2(-x, -z)

# ------------------------------------------------------------- составные
def house(x, z, roof="roof_red", w=3.4, h=2.5, d=2.9, yaw=None, chimney=False):
    yaw = yaw_to_center(x, z) if yaw is None else yaw
    at = (x, 0, z)
    add(box(w, h, d, at, yaw), "wall")
    add(prism(w + 0.5, 1.5, d + 0.5, (x, h, z), yaw), roof)
    fwd = np.array([np.sin(yaw), 0, np.cos(yaw)])          # куда смотрит дверь
    side = np.array([np.cos(yaw), 0, -np.sin(yaw)])
    dp = np.array([x, 0, z]) + fwd * (d / 2 + 0.03)
    add(box(0.8, 1.3, 0.1, tuple(dp), yaw), "door")
    for s in (-1, 1):
        wp = np.array([x, 1.2, z]) + fwd * (d / 2 + 0.03) + side * s * (w / 4 + 0.15)
        add(box(0.55, 0.55, 0.1, (wp[0], wp[1], wp[2]), yaw), "window")
    if chimney:
        cp = np.array([x, 0, z]) - side * w / 4
        add(box(0.45, h + 2.1, 0.45, (cp[0], 0, cp[2]), yaw), "wall2")

def clock_tower():
    add(cyl(5.4, 0.55, (0, 0, 0), seg=26), "plaza2")            # плинт
    for i in range(3):                                          # ступени на юг
        add(box(2.6 - i * 0.35, 0.22, 0.8, (0, i * 0.2, 3.4 - i * 0.72)), "stone")
    add(box(2.9, 7.2, 2.9, (0, 0.55, 0)), "wall")               # ствол
    add(ring(1.5, 1.85, 0.22, (0, 6.35, 0), seg=16), "wood")    # балкончик
    for sgn in (1, -1):                                         # циферблаты Ю/С
        m = cyl(1.05, 0.16, (0, 0, 0), seg=18)
        m.apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))
        m.apply_translation([0, 5.2, sgn * 1.42])
        add(m, "clock")
        add(box(0.09, 0.75, 0.06, (0, 5.2, sgn * 1.52)), "dark")           # стрелка ↑
        add(box(0.5, 0.09, 0.06, (0.22, 5.05, sgn * 1.52)), "dark")        # стрелка →
    add(pyramid(3.5, 2.9, 3.5, (0, 7.75, 0)), "roof_blue")
    add(ball(0.26, (0, 10.9, 0)), "lamp")
    add(box(0.9, 1.4, 0.12, (0, 0.55, 1.36)), "door")

def stall(x, z, top="roof_red", yaw=None):
    yaw = yaw_to_center(x, z) if yaw is None else yaw
    for sx in (-1, 1):
        for sz in (-1, 1):
            p = np.array([x, 0, z])
            off = np.array([sx * 0.85, 0, sz * 0.7])
            rot = np.array([off[0] * np.cos(yaw) + off[2] * np.sin(yaw), 0,
                            -off[0] * np.sin(yaw) + off[2] * np.cos(yaw)])
            q = p + rot
            add(box(0.12, 1.5, 0.12, (q[0], 0, q[2]), yaw), "wood")
    add(pyramid(2.3, 0.8, 1.9, (x, 1.5, z), yaw), top)
    add(box(1.7, 0.75, 1.1, (x, 0, z), yaw), "wood_dark")

def tree_round(x, z, s=1.0):
    add(cyl(0.16 * s, 0.9 * s, (x, 0, z), seg=7), "wood_dark")
    add(ball(0.85 * s, (x, 1.45 * s, z), squash=0.95), "leaf")
    add(ball(0.45 * s, (x - 0.5 * s, 1.1 * s, z + 0.2 * s)), "leaf_dark")

def tree_pine(x, z, s=1.0):
    add(cyl(0.14 * s, 0.7 * s, (x, 0, z), seg=7), "wood_dark")
    add(cone(0.75 * s, 1.1 * s, (x, 0.6 * s, z), seg=9), "pine")
    add(cone(0.55 * s, 0.95 * s, (x, 1.3 * s, z), seg=9), "pine")
    add(cone(0.34 * s, 0.8 * s, (x, 2.0 * s, z), seg=9), "pine")

def rock(x, z, s=1.0):
    m = ball(0.55 * s, (x, 0.18 * s, z), squash=0.6)
    add(m, "rock")

def lamp(x, z):
    add(cyl(0.07, 2.1, (x, 0, z), seg=7), "dark")
    add(ball(0.2, (x, 2.25, z)), "lamp")

def fence_run(pts, post_h=0.75):
    pts = [np.array(p, dtype=float) for p in pts]
    for a, b in zip(pts[:-1], pts[1:]):
        L = np.linalg.norm(b - a)
        n = max(2, int(L / 1.1) + 1)
        for i in range(n):
            p = a + (b - a) * (i / (n - 1))
            add(box(0.1, post_h, 0.1, (p[0], 0, p[2])), "fence")
        mid, yaw = (a + b) / 2, np.arctan2((b - a)[0], (b - a)[2])
        add(box(0.07, 0.09, L, (mid[0], post_h * 0.7, mid[2]), yaw), "fence")

def strip(pts, width, color, y=0.02, h=0.1):
    """Дорога/река: лента из сегментов по точкам + диски-стыки на изломах."""
    pts = [np.array([p[0], 0, p[1]], dtype=float) for p in pts]
    for a, b in zip(pts[:-1], pts[1:]):
        L = np.linalg.norm(b - a) + width * 0.35
        mid, yaw = (a + b) / 2, np.arctan2((b - a)[0], (b - a)[2])
        add(box(width, h, L, (mid[0], y, mid[2]), yaw), color)
    for p in pts[1:-1]:
        add(cyl(width * 0.5, h, (p[0], y, p[2]), seg=10), color)

def bridge(x, z, yaw):
    add(box(2.6, 0.22, 1.6, (x, 0.28, z), yaw), "wood")
    fwd = np.array([np.sin(yaw), 0, np.cos(yaw)])
    side = np.array([np.cos(yaw), 0, -np.sin(yaw)])
    for s in (-1, 1):
        r = np.array([x, 0, z]) + side * s * 0.75
        add(box(1.9, 0.12, 0.1, (r[0], 0.75, r[2]), yaw + np.pi / 2), "fence")
        for e in (-1, 1):
            q = r + fwd * e * 0.9
            add(box(0.1, 0.8, 0.1, (q[0], 0, q[2])), "fence")

def windmill(x, z):
    yaw = yaw_to_center(x, z)
    add(box(2.6, 4.6, 2.6, (x, 0, z), yaw), "wall")
    add(prism(3.0, 1.3, 3.0, (x, 4.6, z), yaw), "roof_red")
    fwd = np.array([np.sin(yaw), 0, np.cos(yaw)])
    hub = np.array([x, 4.3, z]) + fwd * 1.55
    add(ball(0.22, tuple(hub)), "wood_dark")
    for k in range(4):                                   # четыре лопасти ✕
        blade = box(0.3, 3.4, 0.08, (0, 0, 0))
        blade.apply_translation([0, 0.1, 0])
        blade.apply_transform(rotation_matrix(np.pi / 4 + k * np.pi / 2,
                                              [np.sin(yaw), 0, np.cos(yaw)]))
        blade.apply_translation(hub)
        add(blade, "wood")
    add(box(0.8, 1.3, 0.1, tuple(np.array([x, 0, z]) + fwd * 1.33), yaw), "door")

def watermill(x, z):
    yaw = yaw_to_center(x, z)
    house(x, z, roof="roof_teal", w=3.2, h=2.6, d=3.0, yaw=yaw)
    side = np.array([np.cos(yaw), 0, -np.sin(yaw)])
    wp = np.array([x, 0, z]) + side * 2.0
    wheel = ring(0.9, 1.35, 0.28, (0, 0, 0), seg=14)
    wheel.apply_transform(rotation_matrix(np.pi / 2, [0, 0, 1]))
    wheel.apply_transform(rotation_matrix(yaw, [0, 1, 0]))
    wheel.apply_translation([wp[0], 1.15, wp[2]])
    add(wheel, "wood")
    for k in range(4):
        sp = box(0.12, 2.5, 0.12, (0, -1.25, 0))
        sp.apply_transform(rotation_matrix(k * np.pi / 4, [1, 0, 0]))
        sp.apply_transform(rotation_matrix(yaw, [0, 1, 0]))
        sp.apply_translation([wp[0], 1.15, wp[2]])
        add(sp, "wood_dark")

def gazebo(x, z, y):
    add(cyl(2.5, 0.35, (x, y, z), seg=8), "stone")
    for k in range(6):
        a = k * np.pi / 3
        add(cyl(0.13, 2.1, (x + 1.85 * np.sin(a), y + 0.35, z + 1.85 * np.cos(a)),
                seg=7), "white")
    add(cone(2.6, 1.7, (x, y + 2.45, z), seg=8), "roof_blue")
    add(ball(0.18, (x, y + 4.35, z)), "lamp")

def gate(x, z):
    for s in (-1, 1):
        add(box(0.8, 3.1, 0.8, (x + s * 1.8, 0, z)), "wall")
    add(prism(5.4, 1.2, 1.4, (x, 3.1, z)), "roof_red")
    fence_run([(x - 6.5, 0, z), (x - 2.4, 0, z)])
    fence_run([(x + 2.4, 0, z), (x + 6.5, 0, z)])

# ================================================================= СБОРКА
R = 30.0                                                   # радиус острова

# --- остров: газон, тёмная кромка, обрыв
add(cyl(R, 0.55, (0, -0.55, 0), seg=34), "grass")
add(cyl(R + 0.7, 0.8, (0, -1.35, 0), seg=34), "grass_dark")
add(cyl(R - 1.2, 1.5, (0, -2.85, 0), seg=34), "cliff")

# --- северный холм с беседкой
hill = ball(8.2, (0, -1.3, -19.5), sub=2, squash=0.52)
add(hill, "grass_dark")
gazebo(0, -19.5, 2.55)
for i in range(9):                                          # тропа-серпантин
    t = i / 8
    px = 1.6 * np.sin(t * 4.4)
    pz = -12.2 - t * 5.6
    py = max(0.0, (t - 0.18) * 3.1)
    add(box(1.15, 0.14, 1.05, (px, py, pz), 0.35 * np.sin(t * 5)), "path")

# --- площадь и кольца
add(cyl(12.3, 0.14, (0, 0.03, 0), seg=30), "plaza")
add(ring(5.6, 6.4, 0.14, (0, 0.06, 0), seg=26), "plaza2")
add(ring(13.6, 16.0, 0.12, (0, 0.03, 0), seg=32), "path")   # кольцевая дорога
clock_tower()

# --- дороги
strip([(0, 12.0), (0, 24.6)], 2.3, "path", y=0.05)          # главная: площадь→ворота
strip([(0, -12.0), (0, -12.6)], 1.8, "path", y=0.05)        # север к тропе
strip([(-15.9, 3.2), (-20.0, 5.4), (-22.4, 8.0)], 1.3, "path", y=0.05)   # к мосту ЮЗ
strip([(15.8, 2.6), (20.2, 4.4)], 1.3, "path", y=0.05)      # к водяной мельнице
strip([(11.2, 11.2), (14.6, 13.8)], 1.3, "path", y=0.05)    # к мастерской
gate(0, 24.6)

# --- река на западе + мосты
river = [(-13.5, -23.5), (-16.5, -18), (-19.5, -12), (-21.5, -5),
         (-22.5, 2), (-23.0, 8.5), (-22.0, 15), (-19.5, 20.5), (-16.5, 24.5)]
strip(river, 1.9, "water", y=0.02, h=0.06)
bridge(-22.6, 8.2, np.deg2rad(80))
bridge(-20.6, -9.0, np.deg2rad(65))

# --- рынок-палатки вокруг площади (пропуская юг-дорогу и север-тропу)
angles = [22, 55, 88, 121, 154, 206, 239, 272, 305, 338]
tops = ["roof_red", "roof_teal"]
for i, adeg in enumerate(angles):
    a = np.deg2rad(adeg)
    x, z = 9.7 * np.sin(a), 9.7 * np.cos(a)
    stall(x, z, tops[i % 2])

# --- фонари на площади
for adeg in (36, 108, 180 - 14, 180 + 14, 252, 324):
    a = np.deg2rad(adeg)
    lamp(12.9 * np.sin(a), 12.9 * np.cos(a))

# --- дома девяти (двери смотрят на башню)
house(-12.6, 5.2, roof="roof_red", chimney=True)            # 1 пекарня Греты
house(9.3, 8.6, roof="roof_teal", w=3.8, d=3.2)             # 2 кафе Бруно
house(-5.2, -12.4, roof="roof_brown")                       # 3 дом смотрителя
house(14.8, -3.4, roof="roof_red", w=4.6, h=3.3, d=3.6,     # 4 ратуша Амины
      chimney=True)
house(-11.6, -7.4, roof="roof_red", w=2.3, h=1.9, d=2.0)    # 5 будка Пауля
house(9.8, -11.0, roof="roof_teal")                         # 6 почта Веры
house(16.2, 12.6, roof="roof_teal", chimney=True)           # 7 мастерская Мии
windmill(13.6, -13.8)                                       # мельница СВ
watermill(21.3, 5.4)                                        # водяная В

# --- 8 рынок под платаном + сад Тео (ЮЗ)
tree_round(-14.6, 13.4, s=1.9)                              # платан
stall(-12.4, 15.4, "roof_red")
stall(-16.9, 15.9, "roof_teal")
fence_run([(-19.5, 0, 11.5), (-19.5, 0, 17.5), (-13.0, 0, 18.6)])
for gx, gz in [(-18.3, 12.6), (-17.3, 14.2), (-18.6, 15.8), (-17.0, 16.9)]:
    add(ball(0.42, (gx, 0.32, gz)), "leaf_dark")            # грядки

# --- колодец-фонтан (ЮЗ ближе к площади)
add(cyl(1.05, 0.7, (-9.0, 0, 14.8), seg=12), "stone")
add(cyl(0.75, 0.78, (-9.0, 0, 14.8), seg=12), "water")

# --- заборчики у домов
fence_run([(6.6, 0, 11.6), (11.9, 0, 12.6)])                # у кафе
fence_run([(11.0, 0, -15.9), (16.2, 0, -16.6)])             # у мельницы

# --- деревья и камни по кромке (детерминированный рассев)
rng = np.random.default_rng(7)
riv = np.array(river)
for adeg in range(0, 360, 14):
    a = np.deg2rad(adeg + float(rng.uniform(-5, 5)))
    r = float(rng.uniform(24.5, 28.2))
    x, z = r * np.sin(a), r * np.cos(a)
    if abs(x) < 5.5 and z > 20:      continue               # ворота
    if np.min(np.hypot(riv[:, 0] - x, riv[:, 1] - z)) < 3.2: continue  # река
    if abs(x) < 7 and z < -13:       continue               # холм
    (tree_pine if rng.random() < 0.55 else tree_round)(x, z, s=float(rng.uniform(0.8, 1.3)))
extra = [(-6.5, 17.5, "r"), (5.8, 17.8, "p"), (18.5, -8.5, "p"), (-15.5, -11.5, "p"),
         (6.3, -14.8, "r"), (-8.9, 10.9, "p"), (19.8, 9.8, "r"), (-17.9, 6.9, "r")]
for x, z, kind in extra:
    (tree_round if kind == "r" else tree_pine)(x, z)
for x, z, s in [(4.2, -17.6, 1.4), (5.4, -16.5, 0.9), (-10.5, -14.7, 1.2),
                (17.5, -10.9, 1.0), (23.4, 12.4, 1.3), (-6.2, 21.5, 0.9),
                (12.5, 17.9, 1.1), (24.2, -2.5, 1.5), (-13.6, 21.0, 1.0)]:
    rock(x, z, s)

# --- ящики/бочки у рынка и мельницы
for x, z in [(-11.3, 16.9), (13.0, -15.9), (12.1, -15.2), (8.2, 12.9)]:
    add(box(0.7, 0.7, 0.7, (x, 0, z), 0.4), "wood")
for x, z in [(-10.6, 17.6), (13.9, -15.4)]:
    add(cyl(0.38, 0.72, (x, 0, z), seg=9), "wood_dark")

# ============================================================== ЭКСПОРТ
scene = trimesh.Scene()
total_tris = 0
for key, meshes in BUCKETS.items():
    merged = trimesh.util.concatenate(meshes)
    merged.unmerge_vertices()                                # flat shading
    rgb = col(key)
    material = trimesh.visual.material.PBRMaterial(
        baseColorFactor=[*(rgb / 255.0), 1.0],
        metallicFactor=0.0, roughnessFactor=0.95, name=key)
    merged.visual = trimesh.visual.TextureVisuals(material=material)
    scene.add_geometry(merged, geom_name=key, node_name=key)
    total_tris += len(merged.faces)

out = __file__.rsplit("/", 1)[0] + "/../kolokolets_town.glb"
scene.export(out)
print(f"OK: {out}")
print(f"материалов: {len(BUCKETS)}, треугольников: {total_tris}")
box_ = scene.bounds
print(f"габариты: X {box_[0][0]:.1f}..{box_[1][0]:.1f}  "
      f"Y {box_[0][1]:.1f}..{box_[1][1]:.1f}  Z {box_[0][2]:.1f}..{box_[1][2]:.1f}")
