// The Catalogue Photo of an Impossible Gadget — CHRONO-TOAST T-3000.
//
// The catalogue photograph itself is generated at build time by draw.py
// (PIL) and committed as entry.png. At grade time this program only copies
// that committed image to $MAKEFUN_OUTPUT_DIR/entry.png using the Node
// standard library: no network, no shelling out, no Pillow or fonts needed
// in the grading sandbox.
//
// The picture: a chrome studio toaster that toasts TIME — its two slices
// of toast pop up as clock faces (10:08 and 4:40) — with exactly one
// accessory, a small red twin-bell alarm clock standing beside it.
import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "output";
mkdirSync(outDir, { recursive: true });

if (!existsSync(src)) {
  throw new Error(`entry.png not found next to main.ts (looked in ${here})`);
}
const dest = join(outDir, "entry.png");
copyFileSync(src, dest);

const bytes = statSync(dest).size;
if (bytes > 1_048_576) {
  throw new Error(`entry.png is ${bytes} bytes, over the 1 MiB cap`);
}
console.log(`wrote ${dest} (${bytes} bytes)`);
