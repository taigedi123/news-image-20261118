// news-image-20261118 entrypoint.
//
// The finished image is entry.png, rendered in code by draw.py and committed
// next to this file. This program's only job is to hand that exact file to
// the grader: read the PNG bytes in, write the same bytes out to the
// output directory. Nothing is re-encoded, resized, or re-drawn here, so
// the judge sees the same bytes that are in this repo.
//
// Local check:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
// (Inside the grader, MAKEFUN_OUTPUT_DIR is unset and /output is used.)

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, "entry.png");
const targetDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";

mkdirSync(targetDir, { recursive: true });
const bytes = readFileSync(source);
writeFileSync(resolve(targetDir, "entry.png"), bytes);
