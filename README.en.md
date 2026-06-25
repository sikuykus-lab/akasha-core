AKASHA Core (`akasha-core`)
===========================

This is the Python implementation of the AKASHA core (`akash-core v1`) as specified
in `AKASHA-TZ v1.8`.

- Single brain repository (private GitHub or a directory on your server) with a fixed layout.
- CLI tool `akash` and library `akash_core` for `adopt`, `pull`, `prepare`, `remember`, `sync` and more.
- Backends `github` and `server` as described in §2.5 of the spec.

The spec is the single source of truth:

- `AKASHA-TZ v1.8` (a copy lives in the user’s working repository, e.g. `Google Sheets/akash/AKASHA-TZ.md`).

## Legal / SaaS status

`akasha-core` is **not** open source. It is a proprietary AKASHA core.
All rights belong to `sikuykus-lab`.

Use of the code is allowed only for:

- integration with your private AKASHA brain repository (GitHub or server);
- AKASHA‑compatible SaaS solutions explicitly approved by the owner.

License texts:

- `LICENSE.md` — main license (Russian, binding);
- `LICENSE.en.md` — English translation;
- `LICENSE.es.md` — Spanish translation;
- `LICENSE.zh.md` — Chinese translation.

## Installation (from source)

```bash
cd akasha-core
pip install -e .
```

## Quick start

```bash
# bootstrap against a GitHub brain repo
akash adopt https://github.com/user/akash-brain --agent cursor

# check status
akash status

# start session
akash pull

# sync at end of session
akash sync
```

See §11 of `AKASHA-TZ v1.8` and the docs in `docs/AKASHA-INSTRUCTIONS.*.md`
for the full command list and lifecycle.

