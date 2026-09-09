# Project Type Detection

Classify the repository using evidence from Discovery. A repository can have a dominant type plus secondary traits (e.g. "CLI that is also a library"); pick the dominant reader-facing type to drive section priority, and mention secondary traits in About/Features.

Detection signals →Type:

| Signal | Likely type |
|---|---|
| `bin` field in package.json, argparse/click/commander/clap/cobra usage, no HTTP server | **CLI** |
| Published to npm/PyPI/crates.io/RubyGems with clear public exports, no UI, no server | **Library / SDK** |
| Express/Fastify/Flask/FastAPI/Django/Rails routes, OpenAPI spec, no frontend build | **API** |
| React/Vue/Svelte/Next.js/Angular app, `public/index.html`, frontend build pipeline | **Web application** |
| Electron/Tauri/Qt/.NET WPF project files | **Desktop application** |
| React Native / Flutter / Swift(iOS)/Kotlin(Android) project structure | **Mobile application** |
| Repo designed to be extended by others (plugin points, hooks, lifecycle docs) | **Framework** |
| Manifest targeting a host application (VS Code extension, browser extension, CMS plugin) | **Plugin / Extension** |
| Scheduled scripts, workflow runners, no user-facing interface | **Automation** |
| Agent loop, tool-calling, prompt/skill definitions, LLM orchestration | **AI agent** |
| `SKILL.md` + reference/asset structure like this one | **AI skill** |
| Terraform/Ansible/Helm/Kubernetes manifests as the primary content | **Infrastructure project** |
| Dockerfile/compose is the primary deliverable, minimal app code | **Docker project** |
| `packages/`, `apps/`, workspace config (lerna, nx, turborepo, pnpm workspaces) | **Monorepo** |
| "template" in name/description, designed to be cloned/forked as a starting point | **Template** |
| Course materials, tutorials, notebooks as primary content | **Educational repository** |
| Dotfiles, shared configs, no executable logic | **Configuration repository** |
| The repo *is* a docs site (Docusaurus, MkDocs, VuePress) | **Documentation project** |

If nothing matches cleanly, describe the closest fit and say so plainly rather than forcing a category.

## Section priorities by type

Use this to decide which SHOULD/CONDITIONAL sections (see `section-library.md`) get emphasis and ordering priority. MUST sections always apply regardless of type.

**CLI**
Priority: Installation → Commands/Options → Configuration → Examples → Update → Uninstallation.
Usage examples are terminal invocations with real flags from the actual argument parser.

**Library / SDK**
Priority: Installation → Imports → Basic usage → API examples → Compatibility → Versioning.
Show the real import statement and a minimal real call, not a hypothetical one.

**API**
Priority: Quick Start → Authentication → Example request → Example response → Endpoints overview → link to full API docs.
Use real route paths and real request/response shapes pulled from route handlers, OpenAPI spec, or existing docs — never invented endpoints.

**Web application**
Priority: Screenshot/demo → Local setup → Environment variables → Development → Architecture → Deployment.
A screenshot only if one exists in the repo or the user supplies one; never a fabricated placeholder pretending to be a live product shot.

**Desktop / Mobile application**
Priority: Screenshot(s) → Installation per platform → Requirements → Usage walkthrough (numbered UI steps) → Build/Development.

**Framework**
Priority: About/philosophy → Quick Start → Core concepts → Extension points → API → Architecture → Contributing.

**Plugin / Extension**
Priority: Host compatibility → Installation into host → Configuration → Usage → Development (for contributors extending it further).

**Automation**
Priority: What it automates → Triggers/Schedule → Configuration → Setup → Logs/Output → Limitations.

**AI agent / AI skill**
Priority: Purpose → When to use / triggers → Inputs → Workflow → Outputs → Examples → Integration instructions.

**Infrastructure / Docker project**
Priority: Requirements → Quick Start (up and running) → Configuration/variables → Architecture of the stack → Deployment → Security.

**Monorepo**
Priority: About (what the workspace contains) → Package/app index table → Development (workspace-wide commands) → Per-package pointers (link out, don't duplicate).

**Template**
Priority: What you get → How to use this template → What to customize first → Structure.

**Educational / Documentation / Configuration repository**
Priority: About/Purpose → Structure/Contents → How to use or follow along → Contributing (if community-maintained).
Many standard technical sections (Architecture, CI/CD, Deployment) may legitimately not apply — omit them rather than forcing them.
