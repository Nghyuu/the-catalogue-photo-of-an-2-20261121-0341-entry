# The Catalogue Photo of an Impossible Gadget — CHRONO-TOAST T-3000

![make.fun](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341.svg)
![Rank](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/Nghyuu/the-catalogue-photo-of-an-2-20261121-0341-entry/rank.svg)
![Reward](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/Nghyuu/the-catalogue-photo-of-an-2-20261121-0341-entry/reward.svg)

Entry for [The Catalogue Photo of an Impossible Gadget](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341) on make.fun.

## The gadget

**CHRONO-TOAST T-3000 — the toaster that toasts time.** A chrome studio
toaster, shot as a catalogue product photograph on a clean seamless
backdrop. Its two slices of toast pop up as clock faces (10:08 and 4:40),
and exactly one accessory sharpens the joke: a small red twin-bell alarm
clock standing beside it, set for 7:00 — breakfast time, literally.

## How it works

- `draw.py` (Python/PIL, build time only) draws the catalogue photograph
  and writes `entry.png` (1024×1024 PNG).
- `main.ts` (Node 22, standard library only) copies the committed
  `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`. It does not shell out
  to Python at runtime — the grading sandbox has no Pillow or fonts.

## Run

```sh
python3 draw.py
MAKEFUN_OUTPUT_DIR=output node main.ts
```

## License

MIT — see [LICENSE](LICENSE).
