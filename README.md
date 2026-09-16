# Axonometric Block Drawing

Isometric (axonometric) reconstruction of the photographed wooden-block assembly.

## Output

- [`assets/blocks_axonometric.png`](assets/blocks_axonometric.png) — precise isometric rendering
- [`assets/blocks_axonometric.svg`](assets/blocks_axonometric.svg) — vector isometric drawing
- [`assets/blocks_axonometric_illustrated.png`](assets/blocks_axonometric_illustrated.png) — illustrated axonometric view

## Geometry

Unit cubes on a 3×5×2 grid. Axes are **x** to the right, **y** up, **z** away from the
viewer; the assembly stands on the table on its `y=0` face.

It is not a flat wall. The bottom three courses are two cubes deep, and the top two
courses are a single-cube slab that sits in the **rear** plane, so the top of the
composition steps back over the front of the base.

Front layer, `z=0` (bottom three courses only):

```
y=2:  W  P  P
y=1:  T  W  P
y=0:  T  T  W
```

Rear layer, `z=1` (full height, minus the top-right corner):

```
y=4:  R  R  .
y=3:  R  W  W
y=2:  W  W  W
y=1:  W  W  W
y=0:  W  W  W
```

- **R** red L-tromino · **P** purple L-tromino · **T** teal L-tromino · **W** natural wood

Seen straight on, the nearest cube in each cell gives the front elevation
`R R . / R W W / W P P / T W P / T T W`; from behind, the rear slab reads as wood with
the red L mirrored into the top-right corner. `render_axonometric.py` prints all four
elevations so the model can be checked against the reference photographs.

## Regenerate

```bash
python3 render_axonometric.py
```
