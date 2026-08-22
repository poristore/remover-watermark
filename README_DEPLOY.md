# Watermarks Remover Web — Free deployment

Web wrapper for `guillaumemeyer/watermarks-remover`.

## Recommended free host (verified Aug 22, 2026): Render Free Web Service

Render currently supports free web services for hobby/testing use. Free services:
- receive a public `onrender.com` URL;
- can run Docker/Python;
- spin down after 15 minutes of inactivity;
- receive 750 free instance-hours per workspace per month;
- use ephemeral local storage, which suits this app because uploads should not persist.

### Deploy

1. Put this folder in your own GitHub repository.
2. In Render: **New → Web Service**.
3. Connect your GitHub repository.
4. Runtime: Docker.
5. Instance type: **Free**.
6. Create the service.

`render.yaml` is included for Blueprint-style configuration.

## Compliance decisions

The upstream project explicitly separates deterministic cleaning, best-effort rewrite,
metadata/C2PA stripping, optional external scorers/backends, and out-of-scope pixel
watermark removal.

This public wrapper therefore:
- requires user confirmation that they own/have rights to process the content;
- prohibits academic fraud and false “human-written” claims in the UI;
- does not claim “undetectable” output;
- exposes residual-risk limitations;
- enables core Layer A and file cleaners;
- leaves Layer B remote/model rewrite disabled by default;
- does not bundle reverse-SynthID;
- does not bundle CtrlRegen/noai-watermark;
- retains the upstream MIT license notice.

## Privacy / storage

Each operation uses temporary files. The application does not intentionally create
a persistent user-content database. Render Free local storage is ephemeral.
Hosting-provider logs and infrastructure are still governed by Render's own policies.

## Resource limits

This wrapper applies a conservative 64 MiB public input limit.
The upstream project itself has broader configurable resource caps.

PDF cleanup benefits from `exiftool`, which is installed.
`c2patool` is optional upstream and is not included in this minimal free image.

## Security

- Treat uploads as untrusted.
- Never shell-interpolate user filenames.
- Do not expose rewrite API keys in command-line arguments.
- Do not enable arbitrary remote rewrite endpoints.
- Track upstream `main` or deliberately pin a reviewed release/commit and update it.

## License

Upstream core is MIT. See `UPSTREAM_LICENSE.txt`.
Optional external projects may have separate licenses and are intentionally not bundled.
