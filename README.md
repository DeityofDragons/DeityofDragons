# Axonometric Block Drawing

Isometric (axonometric) reconstruction of the photographed wooden-block assembly.

## Output

- [`assets/blocks_axonometric.png`](assets/blocks_axonometric.png) — precise isometric rendering
- [`assets/blocks_axonometric.svg`](assets/blocks_axonometric.svg) — vector isometric drawing
- [`assets/blocks_axonometric_illustrated.png`](assets/blocks_axonometric_illustrated.png) — illustrated axonometric view

## Geometry

Unit cubes on a 3×5×2 grid. Axes are **x** to the right, **y** up, **z** away from the
viewer; the assembly stands on the table on its `y=0` face.

It is not a flat wall. It is a one-cube-thick backing slab standing in the **rear**
plane, with two L-trominoes applied one cube **proud** of it:

Applied pieces, `z=0` — purple and teal only:

```
y=2:  .  P  P
y=1:  T  .  P
y=0:  T  T  .
```

Backing slab, `z=1` — a full 3×5 minus the top-right corner:

```
y=4:  R  R  .
y=3:  R  W  W
y=2:  W  W  W
y=1:  W  W  W
y=0:  W  W  W
```

- **R** red L-tromino · **P** purple L-tromino · **T** teal L-tromino · **W** natural wood

Twenty cubes in total. Every natural-wood cell that reads in the front elevation is a
hole in the applied layer showing the recessed slab behind, so head-on the nearest cube
per cell gives `R R . / R W W / W P P / T W P / T T W`. From behind, the slab reads as
wood with the red L mirrored into the top-right corner, which is why red is the only
colour visible from both sides. `render_axonometric.py` prints all four elevations so
the model can be checked against the reference photographs.

## Regenerate

```bash
python3 render_axonometric.py
```
