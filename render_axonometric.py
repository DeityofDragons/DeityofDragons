#!/usr/bin/env python3
"""Render an axonometric (isometric) drawing of the wooden block structure."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# Occupied unit cubes (x right, y up, z depth). Front elevation z=0:
#
#   y=4: R R .
#   y=3: R W W
#   y=2: W P P
#   y=1: T W P
#   y=0: T T W
VOXELS: dict[tuple[int, int, int], str] = {
    # Red L-tromino
    (0, 4, 0): "R",
    (1, 4, 0): "R",
    (0, 3, 0): "R",
    # Purple L-tromino
    (1, 2, 0): "P",
    (2, 2, 0): "P",
    (2, 1, 0): "P",
    # Teal L-tromino
    (0, 0, 0): "T",
    (1, 0, 0): "T",
    (0, 1, 0): "T",
    # Natural wood monocubes
    (2, 0, 0): "W",
    (1, 1, 0): "W",
    (0, 2, 0): "W",
    (1, 3, 0): "W",
    (2, 3, 0): "W",
}

# Face shades: top / left (+z) / right (+x)
PALETTE = {
    "R": ("#F04545", "#D32F2F", "#A32020"),
    "P": ("#B57AE8", "#9B59D6", "#7340A8"),
    "T": ("#45C4B4", "#2FA899", "#227F74"),
    "W": ("#EDD3AD", "#D7B88A", "#B8925E"),
}

EDGE = "#1F1A17"


def iso_project(x: float, y: float, z: float, scale: float) -> tuple[float, float]:
    sx = (x - z) * math.cos(math.radians(30)) * scale
    sy = -y * scale + (x + z) * math.sin(math.radians(30)) * scale
    return sx, sy


def cube_faces(
    x: int, y: int, z: int, scale: float
) -> dict[str, list[tuple[float, float]]]:
    p = {
        "000": iso_project(x, y, z, scale),
        "100": iso_project(x + 1, y, z, scale),
        "010": iso_project(x, y + 1, z, scale),
        "110": iso_project(x + 1, y + 1, z, scale),
        "001": iso_project(x, y, z + 1, scale),
        "101": iso_project(x + 1, y, z + 1, scale),
        "011": iso_project(x, y + 1, z + 1, scale),
        "111": iso_project(x + 1, y + 1, z + 1, scale),
    }
    return {
        # +y
        "top": [p["010"], p["110"], p["111"], p["011"]],
        # +z appears on the left of the cube in this projection
        "left": [p["001"], p["011"], p["111"], p["101"]],
        # +x appears on the right of the cube
        "right": [p["100"], p["110"], p["111"], p["101"]],
    }


def occluded(x: int, y: int, z: int, face: str, occupied: set[tuple[int, int, int]]) -> bool:
    if face == "top" and (x, y + 1, z) in occupied:
        return True
    if face == "left" and (x, y, z + 1) in occupied:
        return True
    if face == "right" and (x + 1, y, z) in occupied:
        return True
    return False


def projected_bounds(scale: float) -> tuple[float, float, float, float]:
    pts: list[tuple[float, float]] = []
    for x, y, z in VOXELS:
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    pts.append(iso_project(x + dx, y + dy, z + dz, scale))
    return (
        min(p[0] for p in pts),
        min(p[1] for p in pts),
        max(p[0] for p in pts),
        max(p[1] for p in pts),
    )


def render_png(path: Path, size: int = 2000, scale: float = 150) -> None:
    occupied = set(VOXELS)
    ordered = sorted(VOXELS.keys(), key=lambda p: (p[0] + p[2], p[1], p[0]))

    min_x, min_y, max_x, max_y = projected_bounds(scale)
    ox = size / 2 - (min_x + max_x) / 2
    oy = size / 2 - (min_y + max_y) / 2 - size * 0.02

    def shift(poly: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [(px + ox, py + oy) for px, py in poly]

    # Soft contact shadow
    shadow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    footprint: list[tuple[float, float]] = []
    for (x, y, z) in VOXELS:
        if y != 0:
            continue
        for dx, dz in ((0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)):
            footprint.append(iso_project(x + dx, -0.05, z + dz, scale))
    if footprint:
        sp = shift(footprint)
        xs = [p[0] for p in sp]
        ys = [p[1] for p in sp]
        pad = scale * 0.35
        bbox = [min(xs) - pad, min(ys) - pad * 0.3, max(xs) + pad, max(ys) + pad * 0.55]
        shadow_draw.ellipse(bbox, fill=(40, 30, 20, 55))
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=scale * 0.12))

    img = Image.new("RGBA", (size, size), (252, 250, 247, 255))
    img = Image.alpha_composite(img, shadow_layer)
    draw = ImageDraw.Draw(img)

    face_order = ("left", "right", "top")
    color_map = {"left": 1, "right": 2, "top": 0}

    for x, y, z in ordered:
        colors = PALETTE[VOXELS[(x, y, z)]]
        faces = cube_faces(x, y, z, scale)
        for name in face_order:
            if occluded(x, y, z, name, occupied):
                continue
            sp = shift(faces[name])
            draw.polygon(sp, fill=colors[color_map[name]], outline=EDGE)
            draw.line(sp + [sp[0]], fill=EDGE, width=max(2, scale // 45))

    img_rgb = Image.new("RGB", (size, size), (252, 250, 247))
    img_rgb.paste(img, mask=img.split()[-1])
    path.parent.mkdir(parents=True, exist_ok=True)
    img_rgb.save(path, "PNG", optimize=True)
    print(f"Wrote {path}")


def render_svg(path: Path, scale: float = 110) -> None:
    occupied = set(VOXELS)
    ordered = sorted(VOXELS.keys(), key=lambda p: (p[0] + p[2], p[1], p[0]))
    min_x, min_y, max_x, max_y = projected_bounds(scale)
    pad = 64
    width = (max_x - min_x) + pad * 2
    height = (max_y - min_y) + pad * 2
    ox = pad - min_x
    oy = pad - min_y

    def poly_to_svg(poly: list[tuple[float, float]]) -> str:
        return " ".join(f"{px + ox:.2f},{py + oy:.2f}" for px, py in poly)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.2f} {height:.2f}">',
        '<rect width="100%" height="100%" fill="#FCFAF7"/>',
        "<title>Axonometric drawing of wooden block assembly</title>",
        f'<g stroke="{EDGE}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">',
    ]

    face_order = ("left", "right", "top")
    color_map = {"left": 1, "right": 2, "top": 0}

    for x, y, z in ordered:
        colors = PALETTE[VOXELS[(x, y, z)]]
        faces = cube_faces(x, y, z, scale)
        for name in face_order:
            if occluded(x, y, z, name, occupied):
                continue
            parts.append(
                f'<polygon points="{poly_to_svg(faces[name])}" fill="{colors[color_map[name]]}"/>'
            )

    parts += ["</g>", "</svg>", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {path}")


def main() -> None:
    root = Path(__file__).resolve().parent
    assets = root / "assets"
    output = root / "output"
    for dest in (assets, output):
        render_png(dest / "blocks_axonometric.png", size=2000, scale=155)
        render_svg(dest / "blocks_axonometric.svg", scale=120)


if __name__ == "__main__":
    main()
