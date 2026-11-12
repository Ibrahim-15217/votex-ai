# Fresh-Clone Verification

**Run:** 12 November 2026
**Commit verified:** [`f67cd47`](https://github.com/Ibrahim-15217/votex-ai/commit/f67cd47)
**Repository:** https://github.com/Ibrahim-15217/votex-ai (public)
**Result:** **PASS** — the repository is self-contained.

This records a clean-machine run of the public repository, with no files copied
from the development working copy.

---

## 1. Environment

| Item | Value |
| --- | --- |
| Host | Windows 11 |
| Clone | `git clone --depth 1 https://github.com/Ibrahim-15217/votex-ai.git` |
| Python | 3.12.5 (fresh `venv`) |
| Node | 24.7.0 |
| npm | 11.5.1 |
| Database | SQLite fallback, created and seeded automatically on first start |
| Data | Synthetic demo tenants only |

---

## 2. Commands and results

### Frontend

```bash
cd frontend
npm ci --no-audit --no-fund
npm run build
```

`npm ci` installed **184 packages** from the committed lockfile.

`npm run build` runs `tsc --noEmit && vite build`:

| Output | Size | Gzip |
| --- | --- | --- |
| `dist/index.html` | 0.83 kB | 0.50 kB |
| `dist/assets/index-*.css` | 39.70 kB | 7.96 kB |
| `dist/assets/index-*.js` | 377.90 kB | 109.88 kB |
| `dist/favicon.svg` | 0.67 kB | — |

66 modules transformed. No TypeScript errors. Bundle sizes match the
development build exactly.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -q
```

- Dependency install: exit code 0; `fastapi`, `sklearn`, `jwt` and `argon2`
  import cleanly.
- Test suite: **40 passed, 1 warning in 51.54 s**.
  The warning is Starlette's upstream `anyio.abc.BlockingPortal` deprecation in
  its own `testclient.py`; it is not raised by Votex code.

### Runtime

```bash
cd backend  && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev
```

The API created the SQLite database, applied the schema and seeded the demo
tenants on startup. No manual migration or seed step was needed.

---

## 3. API acceptance checks

Run against the clean checkout with the demo accounts
(password `VotexDemo!23`).

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| `GET /api/v1/health` | `ok` | `ok`, version `0.1.0`, env `development` | **PASS** |
| Admin incident stats | 10 incidents, 3 critical | total 10, critical 3 | **PASS** |
| Admin incident queue | 10 visible | 10 visible | **PASS** |
| Cross-tenant read (INEC analyst reading a Votex incident) | denied | `404` | **PASS** |
| Audit chain verification | valid | `valid=true`, 105 entries checked | **PASS** |
| National dashboard | 13 incidents, 2 organisations, suppression active | total 13, organisations 2, `suppressed_cells=39`, `k=5` | **PASS** |
| Correlated indicators | 10 | total 10 | **PASS** |

The audit entry count rises between runs (89 → 105) because sign-ins and
verification calls are themselves audited. That is expected behaviour.

---

## 4. Browser acceptance checks

Headless Chrome 1440×900, analyst session, six authenticated routes. Console
captured through CDP (`Runtime`, `Log` and `Network` domains).

| Route | Loaded | Console errors | Horizontal overflow |
| --- | --- | --- | --- |
| `/` (overview) | yes | 0 | 0 px |
| `/incidents` | yes | 0 | 0 px |
| `/report` | yes | 0 | 0 px |
| `/intelligence` | yes | 0 | 0 px |
| `/dashboards` | yes | 0 | 0 px |
| `/audit` | yes | 0 | 0 px |

Screenshots from this clean checkout are in
[`evidence/fresh-clone/`](./evidence/fresh-clone/).

---

## 5. Issue found and fixed

The first run reported one console error on the overview:

```
Failed to load resource: the server responded with a status of 404 (Not Found)
```

The cause was a missing favicon: `index.html` declared no icon, so the browser
requested `/favicon.ico` and received 404. This was a real first-run defect that
a judge would have seen in DevTools.

Fixed in `f67cd47`:

- added `frontend/public/favicon.svg` (shield and check mark in the brand
  palette), and
- linked it from `frontend/index.html` with
  `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />`.

Re-verified after the fix: **0 console errors on all six routes**, with no
change to the JS or CSS bundle sizes.

---

## 6. Not covered by this run

These remain open and are tracked in
[SUBMISSION_CHECKLIST.md](./SUBMISSION_CHECKLIST.md):

- Docker Compose startup (the SQLite path above was verified instead).
- axe-core automated accessibility audit.
- Native-speaker review of the Hausa, Yoruba and Igbo translations.
- The 13-scenario demonstration run and the three-minute demo video.

---

## 7. Reproduce

```bash
git clone https://github.com/Ibrahim-15217/votex-ai.git
cd votex-ai/frontend
npm ci && npm run build

cd ../backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m pytest -q

.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# second terminal
cd ../frontend && npm run dev
```

Sign in at http://localhost:5173 with `analyst@votex.demo` / `VotexDemo!23`.
