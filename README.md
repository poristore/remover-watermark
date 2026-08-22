# Watermarks Remover Web — Vercel fixed build

Web wrapper around `guillaumemeyer/watermarks-remover`.

## Vercel fixes in this build

- Gradio pinned to `6.3.0`.
- Gradio event queue disabled (`queue=False`) for interactive actions.
- Global `.queue()` removed.
- `show_error=True` enabled so remaining backend errors are visible.
- Upstream `watermarks-remover` pinned to release `v0.3.2` instead of mutable `main`.
- Container listens on Vercel `PORT`, default port 80.

## Deploy/update an existing GitHub + Vercel project

Replace these files in your GitHub repository:
- `app.py`
- `requirements.txt`
- `Dockerfile`
- `Dockerfile.vercel`

Commit the changes. If Vercel is connected to GitHub, a new deployment should start automatically.

## Usage / compliance

Use only on content you own or have permission to process.
No claim is made that outputs are “undetectable” or that official vendor detectors will fail.

See `UPSTREAM_LICENSE.txt`, `README_DEPLOY.md`, and `COMPLIANCE.json`.
