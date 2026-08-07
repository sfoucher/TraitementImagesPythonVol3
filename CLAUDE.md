# CLAUDE.md

Quarto book: *Traitement de la donnée géospatiale avec Python - applications thématiques* (French), volume 3 of the series. Chapters are `NN-*.qmd`; site output → `docs/`.

This repo was seeded as a copy of volume 1 (*Traitement d'images satellites avec Python*) and then stripped: all volume 1 chapters, their notebook/marimo exports, quiz YAMLs and revealjs decks were removed. Volume 1 lives at `../TraitementImagesPythonVol1` and is still the place to look for shared machinery that was deleted here (slides sub-project, quiz YAMLs, per-chapter data files).

Volume 3 is organized by **thematic application** rather than by processing technique — each chapter takes one domain end to end, from data access to interpretation.

Current chapters (`_quarto.yml`): `index.qmd`, `00-auteurs.qmd`, part "Partie 1. Hydrologie spatiale" → `00-SWOT.qmd`, `references.qmd`.

Authors: Samuel Foucher, Mélanie Trudel, Victoria Litalien.

## Build toolchain

- **Quarto runs in docker, not on host.** Image: `mlsysbook-linux:quarto-1.9.38` (the tag encodes the Quarto version; built from `docker/linux/Dockerfile` with `--build-arg QUARTO_VERSION`). Host quarto (`/opt/quarto`) is a different env — use the container for reproducible builds.
- Run pattern (from repo root): `docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/workspace mlsysbook-linux:quarto-1.9.38 quarto <args>` (repo mounts at `/workspace`). Add `--network=host -p 3508:3508` for `quarto preview`. Full form: `q quarto preview --port N --host 0.0.0.0 --no-browser`. Stopping it leaves a `.quarto/preview` lock + a lingering container → next preview fails "Terminating existing preview server" (exit 1); clear with `rm -rf .quarto/preview` and `docker stop` the orphan (`docker ps --filter ancestor=mlsysbook-linux:quarto-1.9.38`).
- `--user "$(id -u):$(id -g)" -e HOME=/tmp` makes generated files (`docs/`, `pdf/`) host-owned, so host-side ops on them (e.g. `cp -f pdf/*.pdf docs/`) work normally. `HOME=/tmp` is required alongside it — the image `HOME` is `/root`, unwritable for a non-root uid, and quarto/jupyter/matplotlib need a writable config dir. Without `--user` the outputs come back root-owned and host-side steps hit EACCES.
- `process.sh` — full build+export script (HTML + PDF + typst, chapter→ipynb/marimo export). Set `-euo pipefail`; all quarto/marimo calls wrapped in a `q()` docker helper.
- Piping a script into the container needs `-i`: `docker run --rm -i … python3 - <<'PY'`. Without `-i`, stdin isn't forwarded → `python3 -` runs an empty script and exits 0 silently.

## Rendering

- **HTML:** `quarto render --to html --output-dir ./docs`
- **PDF:** needs the production profile — `quarto render --profile production --to pdf --output-dir ./pdf`. The `pdf` format is defined only in `_quarto-production.yml` (a Quarto profile), not in `_quarto.yml`.
- `_quarto-production.yml` pulls in `lua/callout_custom_pdf.lua` and five `tex-hacks/*.tex` includes. **Both dirs are build-critical source and are now tracked** — `.gitignore` used to exclude them (inherited from volume 1), which made the PDF build fail on any fresh clone with `cannot open lua/callout_custom_pdf.lua`. Don't re-add those ignore rules.
- The PDF filename is **derived from the book title**, so it changes whenever the title does (accents and punctuation included — `:` becomes `---`; current name is `Traitement-de-la-donnée-géospatiale-avec-Python---applications-thématiques.pdf`). Don't hardcode it; process.sh globs `ls -t ./pdf/*.pdf | head -1`. The `output:` field in `_quarto-production.yml` is dead for book projects and cannot override it.
- Execution is cached (`.jupyter_cache/`, `execute: cache: true`) — re-renders reuse cached notebook output.
- **Typst books work on Quarto ≥1.9** (image is 1.9.38). Render: `quarto render --profile typst --to orange-book-typst --output-dir ./typst-out` (profile `_quarto-typst.yml` sets `format: orange-book-typst` — the bundled textbook layout: colored title band, part banners, boxed chapter headers; palette follows the Quarto brand, blue here). Output is `typst-out/` (gitignored). `keep-typ: true` also emits the book source `index.typ` at repo root (gitignored) — compile it standalone from repo root with `quarto typst compile index.typ out.pdf` (set `TYPST_PACKAGE_CACHE_PATH=.quarto/typst/packages` for offline; needs the `images/` + `*_files/` assets present). `make-typst-zip.sh` bundles `index.typ` + its referenced assets into `typst-out/book-typst-src.zip` for upload to typst.app (`SKIP_RENDER=1` reuses an existing `index.typ`). Caveats: typst's native `.bib` parser is stricter than biblatex — **no duplicate keys**, and `url` must be a real URL (not a bare DOI like `10.xxx`); the LaTeX-only `tex-hacks/` + `callout_custom_pdf.lua` don't apply, so `bloc_*` callouts render as plain blocks. **LaTeX PDF (`--profile production`) stays canonical** — typst is experimental/optional.
- `clean_notebooks.py` (stdlib, tested via `python3 -m unittest tests.test_clean_notebooks -v`) cleans quarto-exported notebooks: strips the YAML header, HTML comments, `#|` directives, `bloc_*` callout regions (removed outright, not converted — except `bloc_exercice`, whose inner markdown is kept, fences stripped), standalone image lines (`![…](…){…}`), and trailing heading-anchor attributes (`## Titre {#sec-…}` → `## Titre`). Stdlib-only, no `docs/` dependency. Runs in process.sh via `q python3 clean_notebooks.py "$ch.ipynb"` after `quarto convert`.
- Build emits a pre-existing non-fatal SCSS parse error dumping `_quarto_internal_scss_error.scss`. Don't chase unless fixing it directly. (Dangling `@sec-*` crossrefs were cleaned up in the volume 3 conversion — the build is currently crossref-clean, so a new `?@sec-` in the output means you just broke something.)
- xarray `.plot()` (pcolormesh) on a full-res raster makes a huge **vector** `figure-pdf/*.pdf` (a 1188×1599 SAR image = 40MB, and it bloats the book PDF too). Use `.plot.imshow()` (raster, ~100KB) or `artist.set_rasterized(True)`. `#| fig-format: png` is **ignored per-cell** by the jupyter engine. Same reasoning applies to dense scatter plots (`PIXC` point clouds are millions of points) — pass `rasterized=True`.
- process.sh renders PDF with `--no-clean`, so renamed/removed figures linger as orphans in `*_files/figure-pdf/`. When a cell's figure outputs change, clear the chapter's `*_files/` and `docs/*_files/` before rebuilding.
- Quarto converts apostrophes in prose/headings to curly `'` in HTML — `grep` with a straight `'` misses them; verify with apostrophe-free fragments. Same for non-breaking spaces before `:` in `index.qmd` (U+00A0), which defeat naive string matching — match on a fragment that avoids the punctuation.
- Quarto copies assets referenced in HTML (`<script src=…>`) but does **not** follow JS `import` chains — imported JS (e.g. `assets/ia-companion/lib.js`, imported by `widget.js`) must be declared under `project: resources:` in `_quarto.yml` or it 404s on the published site (`docs/` gets the script but not its import).
- **pdflatex chokes on some Unicode in prose** (e.g. `≤` U+2264, `≥`) → `LaTeX Error: Unicode character …`, the LaTeX PDF fails, and `docs/*.pdf` gets dropped (a following `git add -A` then commits its deletion). Use words ("au plus"/"au moins"), math mode (`$1\sigma$`, `$\mu\text{rad}$` — safe), or add a mapping to `tex-hacks/fix-unicode-chars.tex`. `×` (U+00D7), `—`, `œ` and accented Latin are fine; typst/HTML handle all of these. After a build, verify `docs/….pdf` still exists before committing.
- **A bare `quarto render --to html --output-dir ./docs` deletes `docs/*.pdf`** — even when it succeeds. Quarto's clean pass prunes anything in the output dir that the HTML render didn't produce, and the PDF comes from a *separate* render (`--profile production`, output `pdf/`, copied in afterwards). This is not the pdflatex failure above: the HTML build reports success and drops the PDF silently, so a following `git add -A` commits its deletion. process.sh is safe (PDF step runs after HTML and re-copies), but any standalone HTML render is not. Restore with `cp -f pdf/*.pdf docs/` and check `ls docs/*.pdf` before committing.

## Publishing

GitHub Pages serves the book from **branch `main`, path `/docs`** at <https://sfoucher.github.io/TraitementImagesPythonVol3/>. `docs/` is committed, so publishing is just build → commit → push; there is no `gh-pages` branch and no publish workflow. (The `gh-pages` branch inherited from volume 1 was stale and has been deleted.)

`_quarto.yml` `site-url` must match that host — it feeds `sitemap.xml` and `robots.txt`. Volume 1's `serie-python-tele.github.io` value is kept as a comment in case the book later moves to the organization. Don't let `site-url` end in `/index.html`: Quarto concatenates it, yielding a malformed `…/index.html/sitemap.xml`.

## Deps

- Python: `docker/dependencies/requirements.txt` (the source of truth for the image). R: `docker/dependencies/install_packages.R`. TeX: `docker/dependencies/tl_packages`. Changing these needs an image rebuild: `docker build --build-arg QUARTO_VERSION=1.9.38 -t mlsysbook-linux:quarto-1.9.38 -f docker/linux/Dockerfile .`
- Root `requirements.txt` is the **reader-facing** list (referenced by `jupyter_env.yaml`), not the image's. `requirements.yaml` is a separate conda env (`atelier`) and still carries volume 1 packages — unused by the build.
- Quarto version is a build arg (`ARG QUARTO_VERSION`, default 1.7.31). process.sh derives `IMAGE` from `QUARTO_VERSION` (default 1.9.38, env-overridable: `QUARTO_VERSION=1.10.x ./process.sh`).
- **The image tag is shared with volume 1.** Both repos have their own `docker/dependencies/requirements.txt` but both resolve to `mlsysbook-linux:quarto-1.9.38`. Rebuilding from volume 3 with volume 1 deps pruned silently breaks volume 1 builds on the same machine. `IMAGE` is env-overridable — use a distinct tag (`IMAGE=vol3-book:quarto-1.9.38`) when volume 3 diverges for real.
- Fast dep-add without full ~20min rebuild: layer-patch — `docker build -t mlsysbook-linux:quarto-1.9.38 - <<EOF` / `FROM mlsysbook-linux:quarto-1.9.38` / `RUN pip install <pkg>` / `EOF`. Caveat: image then diverges from Dockerfile until a clean rebuild.
- The image still carries volume 1 deps that no volume 3 chapter uses (`torch`, `supertree`, `spyndex`, `geemap`, `xrscipy`, `numba`, `opencv`, `seaborn`, `gdown`). Pruning shrinks the image but costs a clean rebuild.
- `torch` must be CPU wheel: `pip install torch==2.4.0+cpu --index-url https://download.pytorch.org/whl/cpu` (avoids ~2GB CUDA wheel).
- `marimo` is in the image; chapter→marimo `.py` export active in process.sh.

## Chapter conventions

- `bloc_*` callouts (objectif/package/exercice/aller_loin/attention/astuce/notes) are custom divs styled in `css/r4ds.scss` (per-type color + `images/Bloc*.png` icon). **Fence nesting is 6/4/3**: `:::::: bloc_X` → `:::: bloc_X-header` → `::: bloc_X-icon`, with an optional `::: bloc_X-body`, closing `::::::`. Quarto renders a 5-colon outer fence just fine, so a wrong count looks correct in the browser — but `make_exercices.py` matches the literal `:::::: bloc_exercice` and silently extracts nothing. Follow 6/4/3.
- `make_exercices.py` (stdlib, tested via `python3 -m unittest tests.test_make_exercices -v`) aggregates each chapter's `bloc_exercice` div (+ any following `<details>` solutions) into a consolidated `08-Exercices.qmd`. Its `CHAPTERS` list at the top is **hardcoded** — add each new chapter there. Currently dormant: `08-Exercices.qmd` is not in `_quarto.yml` and the call is commented out in process.sh, but `tests.test_make_exercices` builds against the real repo, so a stale `CHAPTERS` entry fails the suite.
- Run both suites after touching chapter structure: `python3 -m unittest tests.test_clean_notebooks tests.test_make_exercices` (40 tests, stdlib only, runs on the host).
- `00-SWOT.qmd` is `eval: false` at the header level — `earthaccess.login()` needs interactive Earthdata credentials the container can't supply, so cells are shown but never executed. The packages are in the image regardless. If a future chapter needs real execution, the credential question is the blocker, not the deps.
- Chapter quizzes: an HTML-only cell `render_quizz(Quiz("quiz/ChapNN.yml", "ChapNN"))` from `code_complementaire/quizz_functions.py`, guarded by `.content-visible when-format="html"` with a `when-profile="production"` PDF fallback. Quiz YAML = list of questions: `type` uc/mc/stat, `response` a **1-based** index (or list for mc), `answers` list, optional `help`. **The `quiz/` dir was deleted with the volume 1 chapters** — recreate it (and a `quiz/ChapNN.yml` per chapter) before adding a quiz cell. `code_complementaire/quizz_functions.py` is still present.
- `assets/ia-companion/` — "Assistant IA" chat widget (`widget.js` + `lib.js`), injected via `_quarto.yml` `include-after-body` (`data-worker-url=…workers.dev`). LLM logic (`max_tokens`, system prompt, beginner/expert `level`) lives in a **separate Cloudflare worker, NOT this repo** — answer-truncation / level bugs are worker-side. Widget runs in a shadow DOM: key events need `stopPropagation` at the shadow root, else Quarto's search hotkeys (`f`/`s`/`/`) hijack keystrokes (its handler reads `document.activeElement`, which is the shadow host, not the textarea).

## Note

Docker infra copied from Harvard `cs249r_book` (MLSysBook); `docker/**/README.md` still references upstream repo/registry — not yet adapted.

DOCX render is commented out in process.sh. Quarto prunes non-target format subdirs from `<chapter>_files/` on each render, so `figure-docx/` PNGs get deleted — they're gitignored (`**/figure-docx/`); don't re-commit them.

`docs/….pdf` is committed in full each build (currently ~1.9MB). If it approaches GitHub's 50MB soft limit, hunt oversized `*_files/figure-pdf/*.pdf` (see the pcolormesh note) or use Git LFS.

The revealjs slides sub-project (`slides/`) was volume 1 material and has been removed; restore it from git history (commit `5f80688`) when volume 3 decks are written, and re-add the two render steps to process.sh.
