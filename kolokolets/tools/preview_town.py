#!/usr/bin/env python3
"""Превью kolokolets_town.glb: софт-рендер matplotlib (изометрия, как референс).
Painter's algorithm послойно: террейн → плоские накладки → объекты (по глубине)."""
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

src = __file__.rsplit("/", 1)[0] + "/../kolokolets_town.glb"
scene = trimesh.load(src)
light = np.array([0.45, 0.8, 0.35]); light /= np.linalg.norm(light)

LAYER = {"grass": 0, "grass_dark": 0, "cliff": 0,
         "plaza": 1, "plaza2": 1, "path": 1, "water": 1}

ELEV, AZIM = 35, -66
el, az = np.deg2rad(ELEV), np.deg2rad(AZIM)
view = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])

packs = {0: [], 1: [], 2: []}
for name, geom in scene.geometry.items():
    base = np.array(geom.visual.material.baseColorFactor[:3], dtype=float)
    if base.max() > 1.0:
        base = base / 255.0
    tv = geom.vertices[geom.faces]                        # (n,3,3) Y-up
    shade = 0.6 + 0.4 * np.clip(geom.face_normals @ light, 0, 1)
    pv = np.stack([tv[:, :, 0], -tv[:, :, 2], tv[:, :, 1]], axis=-1)  # север вверх
    cols = np.clip(base[None, :] * shade[:, None], 0, 1)
    packs[LAYER.get(name, 2)].append((pv, cols))

fig = plt.figure(figsize=(13, 10), dpi=110)
ax = fig.add_subplot(111, projection="3d", proj_type="ortho")
for layer in (0, 1, 2):
    if not packs[layer]:
        continue
    pv = np.concatenate([p for p, _ in packs[layer]])
    cols = np.concatenate([c for _, c in packs[layer]])
    depth = pv.mean(axis=1) @ view
    order = np.argsort(depth)                              # дальние первыми
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
