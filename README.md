# Watermarks Remover Web — Vercel

Web wrapper around `guillaumemeyer/watermarks-remover`.

## Deploy
1. Push this folder to a GitHub repository.
2. In Vercel, choose **Add New → Project** and import the repository.
3. Select **Framework Preset: Container** if it is not auto-detected.
4. Vercel should detect `Dockerfile.vercel`.
5. Deploy.

The app listens on the `PORT` environment variable and defaults to port 80.

## Usage / compliance
Use only on content you own or have permission to process.
No claim is made that outputs are "undetectable" or that official vendor detectors will fail.
See `UPSTREAM_LICENSE.txt`, `README_DEPLOY.md`, and `COMPLIANCE.json`.
