#!/usr/bin/env python3
"""Превью kolokolets_town.glb: софт-рендер matplotlib (изометрия, как референс).
Поддерживает инстансы (ноды с трансформами) и текстурные материалы кита."""
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

src = __file__.rsplit("/", 1)[0] + "/../kolokolets_town.glb"
scene = trimesh.load(src)
light = np.array([0.45, 0.8, 0.35]); light /= np.linalg.norm(light)

LAYER0 = ("prim_grass", "prim_grass_dark", "prim_cliff")
LAYER1 = ("prim_plaza", "prim_plaza2", "prim_path", "prim_water")

def face_colors(geom):
    """Средний цвет граней: vertex colors / текстура кита / baseColorFactor."""
    vis = geom.visual
    if isinstance(vis, trimesh.visual.ColorVisuals):
        vc = np.asarray(vis.vertex_colors, dtype=float)[:, :3] / 255.0
        return vc[geom.faces].mean(axis=1)
    try:
        cv = vis.to_color()
        vc = np.asarray(cv.vertex_colors, dtype=float)[:, :3] / 255.0
        return vc[geom.faces].mean(axis=1)
    except Exception:
        base = np.array(vis.material.baseColorFactor[:3], dtype=float)
        if base.max() > 1.0:
            base = base / 255.0
        return np.tile(base, (len(geom.faces), 1))

ELEV, AZIM = 35, -66
el, az = np.deg2rad(ELEV), np.deg2rad(AZIM)
view = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])

# кэш цветов по имени геометрии (инстансы делят геометрию)
color_cache = {name: face_colors(g) for name, g in scene.geometry.items()}

packs = {0: [], 1: [], 2: []}
for node in scene.graph.nodes_geometry:
    world, gname = scene.graph[node]
    geom = scene.geometry[gname]
    tv = trimesh.transformations.transform_points(
        geom.vertices, world)[geom.faces]                  # (n,3,3) Y-up мир
    n = np.cross(tv[:, 1] - tv[:, 0], tv[:, 2] - tv[:, 0])
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
    shade = 0.62 + 0.38 * np.clip(n @ light, 0, 1)
    pv = np.stack([tv[:, :, 0], -tv[:, :, 2], tv[:, :, 1]], axis=-1)
    cols = np.clip(color_cache[gname] * shade[:, None], 0, 1)
    layer = 0 if gname in LAYER0 else 1 if gname in LAYER1 else 2
    packs[layer].append((pv, cols))

fig = plt.figure(figsize=(13, 10), dpi=110)
ax = fig.add_subplot(111, projection="3d", proj_type="ortho")
for layer in (0, 1, 2):
    if not packs[layer]:
        continue
    pv = np.concatenate([p for p, _ in packs[layer]])
    cols = np.concatenate([c for _, c in packs[layer]])
    order = np.argsort(pv.mean(axis=1) @ view)
    coll = Poly3DCollection(pv[order], facecolors=cols[order], edgecolors="none")
    coll.set_zsort("average")
    ax.add_collection3d(coll)

ax.set_xlim(-31, 31); ax.set_ylim(-31, 31); ax.set_zlim(-8, 26)
ax.set_box_aspect((1, 1, 0.55))
ax.computed_zorder = False
ax.view_init(elev=ELEV, azim=AZIM)
ax.set_axis_off(); fig.patch.set_facecolor("#f4efe4")
plt.tight_layout(pad=0)
out = __file__.rsplit("/", 1)[0] + "/../town_preview.png"
plt.savefig(out, bbox_inches="tight", facecolor=fig.get_facecolor())
print("OK:", out)
