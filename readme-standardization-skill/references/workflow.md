# Workflow: Discovery, Project Model, Generation, Modes

## Discovery

Never start writing before this phase is complete. Inspect everything available in the repository — do not sample a few files and extrapolate.

### Files to check for existence and read in full

```text
README.md
LICENSE / LICENSE.md / LICENSE.txt
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
SUPPORT.md
CODE_OF_CONDUCT.md

package.json, package-lock.json, pnpm-lock.yaml, yarn.lock
pyproject.toml, requirements.txt, Pipfile, poetry.lock
Cargo.toml, go.mod, Gemfile, composer.json

Dockerfile, docker-compose.yml, compose.yml
.env.example, .env.template
Makefile, Taskfile.yml

.github/ (issue templates, PR templates, FUNDING.yml)
.github/workflows/*.yml
```

### Directories to walk (not dump — walk to understand structure)

```text
src/, lib/, app/, packages/, apps/
tests/, test/
docs/
examples/
scripts/
public/, assets/, static/, images/
```

### Signals to extract while reading

- **Entry points**: `main`, `bin`, `exports` in package.json; `[project.scripts]` in pyproject.toml; `main.go`; Dockerfile `ENTRYPOINT`/`CMD`.
- **Commands / scripts**: `scripts` block in package.json, `Makefile` targets, `Taskfile.yml` tasks, CLI argument parser definitions (argparse, click, commander, clap, cobra, yargs).
- **Build & test config**: test runner config (jest.config, vitest.config, pytest.ini, tox.ini), build tool config (vite, webpack, tsconfig, setup.py, Cargo build targets).
- **CI/CD**: every workflow file in `.github/workflows/` — read the actual jobs/steps, don't infer from the filename alone.
- **Deployment config**: Dockerfile stages, docker-compose services, Vercel/Netlify config, Kubernetes manifests, Terraform, fly.toml, Procfile.
- **Environment variables**: `.env.example`/`.env.template` keys, `process.env.X` / `os.environ["X"]` / `os.getenv` references in source, config-loading modules.
- **Public interfaces**: exported symbols (`__all__`, `export`, `pub fn`), route definitions (Express/Fastify/Flask/FastAPI routers), OpenAPI/Swagger specs, CLI `--help` output structure, published package name on npm/PyPI/crates.io if declared in manifest.
- **Existing visual assets**: search `assets/`, `docs/assets/`, `public/`, `static/`, `images/`, `.github/` for logo/banner/screenshot/gif files; note exact relative paths.
- **Version & runtime constraints**: `engines` in package.json, `python_requires` in pyproject.toml, `go 1.x` in go.mod, Dockerfile `FROM` base image tag, CI matrix versions.
- **License**: presence and exact type of `LICENSE` file — read enough to identify MIT/Apache-2.0/GPL/BSD/proprietary/none. Never assume from repo visibility.
- **Maintainers/contributors**: `CODEOWNERS`, package manifest `author`/`maintainers` fields, explicit "Maintainers" sections in existing docs. Do not scrape from git history/commit authors as if that were an authoritative maintainer list.
- **Roadmap signals**: an actual `ROADMAP.md`, a "Roadmap" section in an existing README, pinned GitHub Project boards or milestones described in repo docs. Do not infer roadmap from open issues alone.

### Discovery output

Before moving on, be able to answer, with evidence, for every item in the Internal Project Model below. If you cannot answer an item with evidence, its value is `unknown` — not a guess.

## Internal Project Model

Build this structured model (mentally or as scratch notes) before drafting anything:

```yaml
project:
  name:                 # from manifest name / repo name / H1 of existing README
  tagline:               # one sentence, inferred from description fields + code, not marketing copy
  description:
  project_type:          # see references/project-types.md
  target_users:

  languages:
  frameworks:
  runtime:               # verified version constraints only
  package_manager:

  entry_points:
  commands:
  scripts:                # verified, copy-pasted from actual manifest/Makefile

  installation:           # verified command(s) only
  configuration:
  environment_variables:  # name, required?, default, description — only if evidenced
  update_method:          # only if a real update mechanism exists
  uninstall_method:       # only if verifiable

  public_interfaces:
  api:
  cli:
  library_usage:

  architecture:           # only components you can point to in the code
  important_modules:
  important_directories:
  data_flow:

  tests:                  # real test command + framework
  build:                  # real build command + output
  ci:                     # real workflow steps, from .github/workflows
  deployment:             # real deployment mechanism, if any

  assets:                 # real paths to logo/screenshot/banner if present
  documentation:          # links to CONTRIBUTING.md, docs/, etc. if present

  license:                # exact license or "none found"
  maintainers:            # only if verifiable
  releases:               # CHANGELOG.md / GitHub Releases presence
```

Any field with no evidence stays empty/`unknown`. Do not fill gaps with plausible-sounding defaults.

## Generation Workflow

```text
1.  Inspect repository (Discovery, above)
2.  Identify project type (references/project-types.md)
3.  Extract verified project facts into the Internal Project Model
4.  Detect available assets (logo, screenshots, diagrams)
5.  Detect installation / configuration / usage
6.  Detect technical architecture
7.  Detect tests / build / CI / deployment
8.  Detect license / community files
9.  Finalize the Internal Project Model
10. Select MUST / SHOULD / CONDITIONAL sections (references/section-library.md)
11. Build the README outline (canonical order, adapted to the project)
12. Generate Hero (Layer 1)
13. Generate End-User Documentation (Layer 2)
14. Generate Technical Documentation (Layer 3)
15. Generate Project/Community sections (Layer 4)
16. Validate every link, command, and claim against the Internal Project Model
17. Run the Quality Gate (references/anti-hallucination.md)
18. Produce the final README.md
```

Do not skip steps 1–11 "because the project is simple." A simple project still gets the full discovery pass — it just ends up with a shorter, leaner README because fewer sections have evidence, not because the process was shortened.

## Modes

### CREATE mode

Trigger: no README exists, or the existing one is empty / a stub / clearly not meaningful (e.g. just a title).

Process: run the full Generation Workflow above from a blank slate, using only repository evidence.

### UPGRADE mode

Trigger: a substantive README already exists.

Process:

1. Read the existing README in full before touching anything else.
2. Run Discovery and build the Internal Project Model exactly as in CREATE mode — the existing README's claims are not a substitute for verifying against real files.
3. Diff the existing README's claims against the Internal Project Model:
   - Correct and evidenced → preserve, and preserve any intentional project-specific voice/branding/terminology in these parts.
   - Outdated or contradicted by the repo → correct it, note the correction in your summary to the user.
   - Unverifiable (badges, claims, numbers with no matching evidence) → remove or flag; never carry forward a badge/claim just because it was already there.
   - Missing MUST sections → add them, generated the same way as CREATE mode.
   - Present but disorganized → reorganize into the canonical four-layer order without discarding the underlying content.
4. Do not delete project-specific identity (mascots, distinctive tone, an unusual but intentional section) merely because it isn't part of the default template — the goal is standardization of *structure and rigor*, not homogenization of *voice*.
5. Present a short changelog-style summary to the user: what was added, what was corrected, what was removed and why, what still needs the user's input.
