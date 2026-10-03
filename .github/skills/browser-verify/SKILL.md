---
name: browser-verify
description: How to check a website change in a real browser - build the static export, serve it under the production base path, then inspect pages, console, network and accessibility with Playwright. Use after any change under website/ or to data the site renders, before calling it done.
---

# Check the website in a browser

A successful build only shows the site compiles. Done means the page renders the right thing:
look at it.

## 1. Build what production serves

From the repository root:

```bash
(cd website && npm ci && npm run build)
```

This writes the static export to `website/out/`. It uses the production base path
`/quantum-grand-challenges`, so asset URLs only resolve when the site is served under that path.
The build first runs `publish-viz`, which copies visualisation assets into `website/public/viz/`
(gitignored). On Windows it can also rewrite the line endings of `website/data/vizManifest.json`;
if `git diff --stat` shows no content change, restore that file with `git checkout`.

## 2. Serve it under the base path

```bash
mkdir -p /tmp/site && ln -sfn "$PWD/website/out" /tmp/site/quantum-grand-challenges
python -m http.server 8000 --directory /tmp/site
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force $env:TEMP\site | Out-Null
New-Item -ItemType Junction -Path $env:TEMP\site\quantum-grand-challenges -Target (Resolve-Path website\out)
python -m http.server 8000 --directory $env:TEMP\site
```

Open `http://localhost:8000/quantum-grand-challenges/`. Remove the link afterwards.

For quick iteration only, `npm run dev` serves at `http://localhost:3000` without the base path;
it is not what production serves, so finish on the static export.

## 3. Look at it

The cloud agent has a Playwright browser restricted to localhost; in VS Code use the Playwright
tools if they are configured.

- Each page you changed renders the right values. Read them off the page and compare them with
  the source data in `website/data/`.
- The browser console shows no errors, and no network request returns 404, especially for
  `/_next/` assets and images.
- Accessibility basics: one `h1`, headings in order, alternative text on images and charts,
  everything reachable by keyboard, colour not the only signal.
- Take a screenshot of each changed page for the pull request.

## 4. Source-level guards

`python -m pytest tooling/test_website_claims.py -q`,
`python tooling/reporting/validate_website_data_schema.py` and
`python tooling/reporting/check_homepage_stats.py` check the data and claims the site renders.
Run them too; they are not a substitute for looking.
