# Forgejo workflow stubs

These are the Forgejo half of the CI migration. **During Phase 2 they are inert
on both forges** and exist so the shape can be reviewed before it is load-bearing:

* **GitHub ignores this directory entirely** — it reads only `.github/workflows/`.
* **The forge copy of this repo is a read-only pull mirror with the `actions`
  unit disabled**, so nothing here can be triggered there either.

All the real logic lives once in `lenore/lenore-ci`, pinned at `@v1` (a moving
major tag, actions convention). These files stay ~6 lines each — that is the
point.

## 🔴 At the Phase 3 cutover, `.github/workflows/` must be DELETED in the same change

Forgejo reads **both** `.github/workflows/` and `.forgejo/workflows/`. The moment
Actions is enabled on the forge copy, leaving both in place means every workflow
runs twice — and two `semantic-release` instances on one push is exactly the
double-changelog / double-bump anomaly this migration exists to prevent.

Enabling Actions and deleting `.github/workflows/` are one atomic step, not two.
