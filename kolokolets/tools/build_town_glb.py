#!/usr/bin/env python3
"""
КОЛОКОЛЕЦ v2 — сборка города в один GLB из НАСТОЯЩЕГО Kenney Fantasy Town Kit
(папка `fantasy town/GLB format/` в корне репо, CC0) + примитивы для террейна,
воды, дорог и циферблата. Планировка — та же, что в planirovka_goroda.html.

Дома собираются из модулей кита (wall / wall-door / wall-window-*, roof-point),
мельницы — корпус из модулей + родные windmill.glb (крылья) и watermill.glb
(колесо), рынок — stall-red/green, зелень — tree*/rock*, фонтан — fountain-*.
Каждый уникальный ассет грузится один раз и ИНСТАНСИРУЕТСЯ нодами → файл лёгкий.

Запуск: python3 build_town_glb.py  →  ../kolokolets_town.glb
Y вверх; юг = +Z (ворота), север = −Z (холм с беседкой).
"""
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix

KIT = __file__.rsplit("/", 1)[0] + "/../../fantasy town/GLB format/"
OUT = __file__.rsplit("/", 1)[0] + "/../kolokolets_town.glb"

# ----------------------------------------------------------- трансформы
def T(tx=0.0, ty=0.0, tz=0.0, yaw=0.0, s=1.0, sy=None):
    m = np.eye(4)
    m[:3, :3] = np.diag([s, sy if sy is not None else s, s])
    if yaw:
        m = rotation_matrix(yaw, [0, 1, 0]) @ m
    m[:3, 3] += [tx, ty, tz]
    return m

def yaw_to_center(x, z):
    return np.arctan2(-x, -z)

INSTANCES = []                                    # (asset, world_matrix)
def place(asset, world):
    INSTANCES.append((asset, world))

# ------------------------------------------------------ примитивный слой
C = {"grass": "7CB158", "grass_dark": "6C9A4C", "cliff": "A98C5B",
     "path": "D9C08F", "plaza": "D6BD8E", "plaza2": "C9AC79",
     "water": "4FA3D8", "wood": "A97B4F", "dark": "4A4038",
     "clock": "F7F3E8", "lamp": "F2C14E"}
BUCKETS = {}
def prim(mesh, key):
    BUCKETS.setdefault(key, []).append(mesh)

def cyl(r, h, at=(0, 0, 0), seg=14):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=seg)
    m.apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))
    m.apply_translation([0, h / 2, 0]); m.apply_translation(at)
    return m

def pbox(w, h, d, at=(0, 0, 0), yaw=0.0):
    m = trimesh.creation.box(extents=[w, h, d])
    m.apply_translation([0, h / 2, 0])
    if yaw: m.apply_transform(rotation_matrix(yaw, [0, 1, 0]))
    m.apply_translation(at)
    return m

def ring(r_in, r_out, h, at=(0, 0, 0), seg=30):
    m = trimesh.creation.annulus(r_min=r_in, r_max=r_out, height=h, sections=seg)
    m.apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))
    m.apply_translation([0, h / 2, 0]); m.apply_translation(at)
    return m

def ball(r, at=(0, 0, 0), sub=1, squash=1.0):
    m = trimesh.creation.icosphere(subdivisions=sub, radius=r)
    m.apply_scale([1, squash, 1]); m.apply_translation(at)
    return m

def strip(pts, width, key, y=0.02, h=0.1):
    pts = [np.array([p[0], 0, p[1]], float) for p in pts]
    for a, b in zip(pts[:-1], pts[1:]):
        L = np.linalg.norm(b - a) + width * 0.35
        mid, yaw = (a + b) / 2, np.arctan2((b - a)[0], (b - a)[2])
        prim(pbox(width, h, L, (mid[0], y, mid[2]), yaw), key)
    for p in pts[1:-1]:
        prim(cyl(width / 2, h, (p[0], y, p[2]), seg=10), key)

# --------------------------------------------------------- дом из модулей
def house(x, z, w=3, d=2, rows=2, yaw=None, wood=False, chimney=False,
          banners=False, roof_h=1.6, roof="roof-point"):
    """Дом w×d тайлов, rows этажей-рядов, пирамидальная крыша из roof-point."""
    yaw = yaw_to_center(x, z) if yaw is None else yaw
    W = lambda lx, ly, lz, lyaw, a: place(a, T(x, 0, z, yaw) @ T(lx, ly, lz, lyaw))
    pref = "wall-wood-" if wood else "wall-"
    for row in range(rows):
        y = float(row)
        for i in range(w):                        # фронт (+Z) и тыл (−Z)
            lx = i + 0.5 - w / 2
            front = None
            if row == 0 and i == w // 2:
                front = pref + "door"
            elif row == 0:
                front = pref + "window-shutters"
            else:
                front = pref + "window-small" if i % 2 == 0 else pref[:-1]
            W(lx, y, d / 2, np.pi / 2, front)
            W(lx, y, -d / 2, -np.pi / 2, pref[:-1] if row else pref + "window-small")
        for j in range(d):                        # бока (±X)
            lz = j + 0.5 - d / 2
            W(w / 2, y, lz, 0.0, pref[:-1])
            W(-w / 2, y, lz, np.pi, pref[:-1] if row else pref + "window-small")
    place(roof, T(x, 0, z, yaw) @ T(0, rows, 0, 0, s=(w + 0.7) / 1.1,
                                    sy=roof_h / 0.5))
    if chimney:
        place("chimney", T(x, 0, z, yaw) @ T(-w / 4, rows + roof_h * 0.45, 0))
    if banners:
        for sx in (-1.1, 1.1):
            place("banner-red" if sx < 0 else "banner-green",
                  T(x, 0, z, yaw) @ T(sx, 0.9, d / 2 + 0.08, np.pi / 2))

def tower():
    prim(cyl(5.4, 0.55, (0, 0, 0), seg=26), "plaza2")            # плинт
    for bx in (-1.0, 0.0, 1.0):                                  # ствол 3×3×6
        for bz in (-1.0, 0.0, 1.0):
            for lvl in range(6):
                place("wall-block", T(bx, 0.55 + lvl, bz))
    place("stairs-wide-stone", T(0, 0, 2.55, np.pi, s=1.7, sy=0.55))
    prim(ring(1.95, 2.35, 0.2, (0, 6.35, 0), seg=18), "wood")    # балкончик
    for sgn in (1, -1):                                          # циферблаты Ю/С
        m = cyl(0.95, 0.14, (0, 0, 0), seg=18)
        m.apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))
        m.apply_translation([0, 5.35, sgn * 1.58]); prim(m, "clock")
        prim(pbox(0.09, 0.66, 0.05, (0, 5.35, sgn * 1.67)), "dark")
        prim(pbox(0.48, 0.09, 0.05, (0.19, 5.19, sgn * 1.67)), "dark")
    place("roof-point-blue", T(0, 6.55, 0, 0, s=3.9 / 1.1, sy=2.3 / 0.5))
    prim(ball(0.22, (0, 9.1, 0)), "lamp")
    for sx in (-1.55, 1.55):
        place("banner-red" if sx < 0 else "banner-green",
              T(sx, 3.4, 1.52, np.pi / 2))

def windmill_bld(x, z):
    yaw = yaw_to_center(x, z)
    house(x, z, w=2, d=2, rows=3, yaw=yaw, wood=True, roof_h=1.3,
          roof="roof-point-red")
    place("windmill", T(x, 0, z, yaw) @ T(0, 2.9, 1.35, np.pi / 2, s=0.85))

def watermill_bld(x, z):
    yaw = yaw_to_center(x, z)
    house(x, z, w=3, d=2, rows=2, yaw=yaw, wood=True, roof_h=1.4)
    place("watermill", T(x, 0, z, yaw) @ T(2.0, 0.95, 0, 0, s=1.35))

def gazebo(x, z, y):
    for k in range(4):
        place("planks", T(x, y, z) @ T([-0.5, 0.5][k % 2], 0.02, [-0.5, 0.5][k // 2]))
    for k in range(6):
        a = k * np.pi / 3
        place("pillar-wood", T(x + 1.35 * np.sin(a), y, z + 1.35 * np.cos(a),
                               0, s=1, sy=1.6))
    place("roof-point-blue", T(x, y + 1.6, z, np.pi / 6, s=3.4 / 1.1, sy=1.5 / 0.5))
    place("lantern", T(x, y + 0.04, z, 0, s=0.9))

def gate(x, z):
    for sx in (-1.5, 1.5):
        place("wall-block", T(x + sx, 0, z)); place("wall-block", T(x + sx, 1, z))
    place("planks", T(x - 0.5, 2.0, z, 0, s=1.0)); place("planks", T(x + 0.5, 2.0, z))
    place("roof-point-red", T(x, 2.06, z, 0, s=4.2 / 1.1, sy=1.0 / 0.5))
    place("banner-red", T(x - 1.5, 0.9, z + 0.55, np.pi / 2))
    place("banner-green", T(x + 1.5, 0.9, z + 0.55, np.pi / 2))
    for s in (-1, 1):
        for i in range(4):
            place("fence", T(x + s * (2.6 + i), 0, z, np.pi / 2))

def bridge(x, z, yaw):
    for o in (-0.5, 0.5):
        place("planks", T(x, 0.22, z, yaw) @ T(o, 0, 0, 0, s=1.0, sy=1.0))
    for s in (-1, 1):
        place("fence", T(x, 0.24, z, yaw) @ T(0, 0, s * 0.75, 0))

def stall(x, z, red=True, s=1.5):
    place("stall-red" if red else "stall-green",
          T(x, 0, z, yaw_to_center(x, z), s=s))

def tree(x, z, kind="tree", s=1.0):
    place(kind, T(x, 0, z, float((x * 7 + z) % 6.28), s=s))

# ================================================================ СБОРКА
R = 30.0
prim(cyl(R, 0.55, (0, -0.55, 0), seg=34), "grass")
prim(cyl(R + 0.7, 0.8, (0, -1.35, 0), seg=34), "grass_dark")
prim(cyl(R - 1.2, 1.5, (0, -2.85, 0), seg=34), "cliff")
prim(ball(8.2, (0, -1.3, -19.5), sub=2, squash=0.52), "grass_dark")   # холм

# площадь, кольца, дороги
prim(cyl(12.3, 0.14, (0, 0.03, 0), seg=30), "plaza")
prim(ring(5.6, 6.4, 0.14, (0, 0.06, 0), seg=26), "plaza2")
prim(ring(13.6, 16.0, 0.12, (0, 0.03, 0), seg=32), "path")
strip([(0, 12.0), (0, 24.6)], 2.3, "path", y=0.05)
strip([(0, -12.0), (0, -12.6)], 1.8, "path", y=0.05)
strip([(-15.9, 3.2), (-20.0, 5.4), (-22.4, 8.0)], 1.3, "path", y=0.05)
strip([(15.8, 2.6), (20.2, 4.4)], 1.3, "path", y=0.05)
strip([(11.2, 11.2), (14.6, 13.8)], 1.3, "path", y=0.05)
for i in range(9):                                          # серпантин на холм
    t = i / 8
    prim(pbox(1.15, 0.14, 1.05,
              (1.6 * np.sin(t * 4.4), max(0.0, (t - 0.18) * 3.1), -12.2 - t * 5.6),
              0.35 * np.sin(t * 5)), "path")

# река + мосты
river = [(-13.5, -23.5), (-16.5, -18), (-19.5, -12), (-21.5, -5),
         (-22.5, 2), (-23.0, 8.5), (-22.0, 15), (-19.5, 20.5), (-16.5, 24.5)]
strip(river, 1.9, "water", y=0.02, h=0.06)
bridge(-22.6, 8.2, np.deg2rad(80)); bridge(-20.6, -9.0, np.deg2rad(65))

tower()
gate(0, 24.6)
gazebo(0, -19.5, 2.9)

# рынок-кольцо вокруг площади
for i, adeg in enumerate([22, 55, 88, 121, 154, 206, 239, 272, 305, 338]):
    a = np.deg2rad(adeg)
    stall(9.7 * np.sin(a), 9.7 * np.cos(a), red=(i % 2 == 0))
for adeg in (36, 108, 166, 194, 252, 324):                  # фонари
    a = np.deg2rad(adeg)
    place("lantern", T(12.9 * np.sin(a), 0.03, 12.9 * np.cos(a), 0, s=1.5))

# дома девяти
house(-12.6, 5.2, w=3, d=2, chimney=True, roof="roof-point-red")   # 1 пекарня Греты
house(9.3, 8.6, w=3, d=2)                                          # 2 кафе Бруно
house(-5.2, -12.4, w=2, d=2, wood=True, roof="roof-point-red")     # 3 дом смотрителя
house(14.8, -3.4, w=4, d=3, rows=2, chimney=True,
      banners=True, roof_h=1.9, roof="roof-point-red")             # 4 ратуша Амины
house(-11.6, -7.4, w=2, d=2, rows=1, roof_h=1.1,
      roof="roof-point-red")                                       # 5 будка Пауля
house(9.8, -11.0, w=3, d=2)                                        # 6 почта Веры
house(16.2, 12.6, w=3, d=2, wood=True, chimney=True)               # 7 мастерская Мии
windmill_bld(13.6, -13.8)
watermill_bld(21.3, 5.4)

# 8 рынок под платаном + сад Тео (ЮЗ)
tree(-14.6, 13.4, "tree", s=2.6)                            # платан
stall(-12.4, 15.4, True); stall(-16.9, 15.9, False)
place("cart", T(-11.2, 0, 17.2, 0.6))
for i, (fx, fz, fy) in enumerate([(-19.5, 12.0, 0), (-19.5, 13.0, 0), (-19.5, 14.0, 0),
                                  (-19.5, 15.0, 0), (-19.0, 16.4, .5), (-17.6, 17.6, 1.0),
                                  (-16.4, 18.2, 1.2), (-15.2, 18.4, 1.4)]):
    place("fence", T(fx, 0, fz, fy))
place("fence-gate", T(-14.1, 0, 18.5, 1.45))
for gx, gz in [(-18.3, 12.6), (-17.3, 14.2), (-18.6, 15.8), (-17.0, 16.9)]:
    place("hedge", T(gx, 0, gz, 0.5, s=0.9))

# фонтан (вместо колодца)
place("fountain-round-detail", T(-9.0, 0.03, 14.8))
place("fountain-center", T(-9.0, 0.1, 14.8))
prim(cyl(0.62, 0.16, (-9.0, 0.12, 14.8), seg=12), "water")

# заборчики и изгороди у домов
for i in range(5):
    place("fence", T(6.6 + i * 1.05, 0, 11.9, np.pi / 2 + 0.12))
for i in range(5):
    place("fence", T(11.0 + i * 1.05, 0, -15.9, np.pi / 2 - 0.1))
for i in range(3):
    place("hedge", T(12.2, 0, -5.6 + i, 0))

# деревья и камни по кромке
rng = np.random.default_rng(7)
riv = np.array(river)
KINDS = ["tree", "tree-high", "tree-crooked", "tree-high-crooked"]
for adeg in range(0, 360, 13):
    a = np.deg2rad(adeg + float(rng.uniform(-5, 5)))
    r = float(rng.uniform(24.5, 28.2))
    x, z = r * np.sin(a), r * np.cos(a)
    if abs(x) < 5.5 and z > 20: continue
    if np.min(np.hypot(riv[:, 0] - x, riv[:, 1] - z)) < 3.2: continue
    if abs(x) < 7 and z < -13: continue
    tree(x, z, KINDS[int(rng.integers(0, 4))], s=float(rng.uniform(1.0, 1.5)))
for x, z, k in [(-6.5, 17.5, "tree"), (5.8, 17.8, "tree-high"), (18.5, -8.5, "tree"),
                (-15.5, -11.5, "tree-high"), (6.3, -14.8, "tree"), (-8.9, 10.9, "tree"),
                (19.8, 9.8, "tree-crooked"), (-17.9, 6.9, "tree")]:
    tree(x, z, k, s=1.15)
for x, z, s, k in [(4.2, -17.6, 1.3, "rock-large"), (5.4, -16.5, 0.9, "rock-small"),
                   (-10.5, -14.7, 1.1, "rock-wide"), (17.5, -10.9, 1.0, "rock-small"),
                   (23.4, 12.4, 1.2, "rock-large"), (-6.2, 21.5, 0.9, "rock-small"),
                   (12.5, 17.9, 1.0, "rock-wide"), (24.2, -2.5, 1.4, "rock-large"),
                   (-13.6, 21.0, 1.0, "rock-small")]:
    place(k, T(x, 0, z, float((x * 3) % 6), s=s))

# ============================================================== ЭКСПОРТ
RECOLOR = {"roof-point-red":  ("roof-point", np.array([201, 79, 67])),
           "roof-point-blue": ("roof-point", np.array([63, 107, 181]))}

def load_asset(name):
    if name in RECOLOR:
        src_name, target = RECOLOR[name]
        m = trimesh.load(KIT + src_name + ".glb", force="mesh").copy()
        vc = np.asarray(m.visual.to_color().vertex_colors, float)[:, :3]
        lum = vc.mean(axis=1, keepdims=True) / max(vc.mean(), 1e-6)   # светотень
        teal = (vc[:, 1] > vc[:, 0] * 1.15)                            # бирюза кита
        out = vc.copy()
        out[teal] = np.clip(target[None, :] * lum[teal], 0, 255)
        rgba = np.hstack([out, np.full((len(out), 1), 255.0)])
        m.visual = trimesh.visual.ColorVisuals(mesh=m, vertex_colors=rgba.astype(np.uint8))
        return m
    return trimesh.load(KIT + name + ".glb", force="mesh")

scene = trimesh.Scene()
cache = {}
counts = {}
for asset, world in INSTANCES:
    if asset not in cache:
        cache[asset] = load_asset(asset)
    counts[asset] = counts.get(asset, 0) + 1
    scene.add_geometry(cache[asset], geom_name=asset,
                       node_name=f"{asset}_{counts[asset]:03d}", transform=world)

tris = sum(len(cache[a].faces) * n for a, n in counts.items())
for key, meshes in BUCKETS.items():
    merged = trimesh.util.concatenate(meshes)
    merged.unmerge_vertices()
    rgb = np.array([int(C[key][i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
    merged.visual = trimesh.visual.TextureVisuals(
        material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=[*rgb, 1.0], metallicFactor=0.0,
            roughnessFactor=0.95, name=key))
    scene.add_geometry(merged, geom_name="prim_" + key, node_name="prim_" + key)
    tris += len(merged.faces)

scene.export(OUT)
print(f"OK: {OUT}")
print(f"кит-ассетов: {len(cache)} уникальных, {sum(counts.values())} инстансов; "
      f"треугольников всего: ~{tris}")
b = scene.bounds
print(f"габариты: X {b[0][0]:.1f}..{b[1][0]:.1f}  Y {b[0][1]:.1f}..{b[1][1]:.1f}  "
      f"Z {b[0][2]:.1f}..{b[1][2]:.1f}")
