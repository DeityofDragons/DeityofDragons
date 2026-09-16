# Axonometric Block Drawing

Isometric (axonometric) reconstruction of the photographed wooden-block assembly.

## Output

- [`assets/blocks_axonometric.png`](assets/blocks_axonometric.png) — precise isometric rendering
- [`assets/blocks_axonometric.svg`](assets/blocks_axonometric.svg) — vector isometric drawing
- [`assets/blocks_axonometric_illustrated.png`](assets/blocks_axonometric_illustrated.png) — illustrated axonometric view

## Geometry

Unit cubes on a 3×5×1 grid (x right, y up, z depth):

```
y=4:  R  R  .
y=3:  R  W  W
y=2:  W  P  P
y=1:  T  W  P
y=0:  T  T  W
```

- **R** red L-tromino · **P** purple L-tromino · **T** teal L-tromino · **W** wood monocubes

## Regenerate

```bash
python3 render_axonometric.py
```
