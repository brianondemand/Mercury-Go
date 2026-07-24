# 🪽 Mercury Go

Automates `git fetch → pull → add → commit → push` with a styled CLI.

![Mercury screenshot](/banner.png)

## What it does

Running `mercury go` performs, in order:

1. **Locate the repo** — defaults to your current working directory (override with `--repo`).
2. **Verify the remote** *(optional)* — if you pass `--remote-url`, it checks `origin` matches exactly and aborts if it doesn't, so you never accidentally push to the wrong repo.
3. **Fetch & sync** — `git fetch`, then auto-`git pull` if your branch is behind.
4. **Show status** — prints `git status` so you can see what's about to be staged.
5. **Stage everything** — `git add .`
6. **Commit** — `git commit -m "<message>"` (default: `Updates Via Mercury`).
7. **Push** — `git push`.

## Requirements

- Python 3.7+
- `git` on your `PATH`
- `pip install rich`

## Setup (Windows)

1. Put `mercury.py` and `mercury.bat` in one folder, e.g. `C:\Tools\mercury\`.
2. Add that folder to your `PATH`:
   - Win → search "Environment Variables" → *Edit the system environment variables* → **Environment Variables** → select `Path` under *User variables* → **Edit** → **New** → paste the folder path → OK.
   - Or PowerShell: `setx PATH "$env:PATH;C:\Tools\mercury"`
3. Restart your terminal.

## Usage

Run from inside any git repo:

```bash
mercury
# or
mercury go
```

### Options

| Flag | Description | Default |
|---|---|---|
| `--repo PATH` | Repository to operate on | current working directory |
| `--remote-url URL` | Expected `origin` URL; aborts if it doesn't match | *(skipped if omitted)* |
| `--commit-message "MSG"` | Commit message | `Updates Via Mercury` |
| `--no-wait` | Skip the final "Press Enter" prompt | off |

### Examples

```bash
mercury go --repo ~/projects/my-repo --remote-url git@github.com:yourname/my-repo.git
mercury go --commit-message "Automated backup" --no-wait
```

## Notes

- Runs `git add .` — stages everything in the working tree. Check your `.gitignore` before running.
- If there's nothing to commit, Mercury logs a warning and still attempts to push.
- The remote-URL check is opt-in (via `--remote-url`), not hardcoded — the same install works across different repos.

## License

Feel free to use, modify, and share.
