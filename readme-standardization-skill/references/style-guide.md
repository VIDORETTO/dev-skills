# Style Guide

## Markdown rules

- GitHub Flavored Markdown throughout.
- Heading hierarchy: `H1` → project name only (exactly one H1 in the whole document); `H2` → main sections; `H3` → subsections.
- Centered hero section, useful whitespace, concise paragraphs, descriptive headings, syntax-highlighted code blocks, relative repository links, tables where they help scanning, meaningful alt text on every image, Mermaid for diagrams that earn their place, consistent emoji-per-section, scannable structure throughout.
- Avoid excessive HTML. Use HTML only where Markdown can't do the job: centered hero, `<picture>` for dark/light logo variants, precise image sizing.

## Hero section markup

```html
<div align="center">

[LOGO]

# Project Name

**Short tagline explaining exactly what the project does.**

[BADGES]

[Quick navigation links]

</div>
```
Optionally followed by a screenshot / demo GIF / banner / product preview. The hero's job: identity, purpose, status, main technology, navigation, visual preview — in that order of importance.

## Logo rules

1. Search the repo first: `assets/`, `docs/assets/`, `public/`, `static/`, `images/`, `.github/`.
2. Prefer a repository-local asset over any external image. Never link a random external logo.
3. If no logo exists and the environment/task explicitly allows creating one, a simple neutral placeholder logo may be generated — but it must be clearly labeled to the user as a **newly created placeholder**, never presented as if it were a pre-existing official asset.
4. Recommended filenames: `assets/logo.svg`, `assets/logo-light.svg`, `assets/logo-dark.svg`.
5. For dark/light mode support, prefer GitHub-compatible markup:
```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/logo-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/logo-light.svg">
  <img alt="Project logo" src="./assets/logo-light.svg">
</picture>
```

## Asset standard

```text
assets/
├── logo.svg
├── logo-light.svg
├── logo-dark.svg
├── banner.png
├── screenshot.png
├── demo.gif
└── architecture.svg
```
For larger repos:
```text
docs/
└── assets/
    ├── branding/
    ├── screenshots/
    ├── diagrams/
    └── demos/
```
Always use relative paths. Every meaningful image needs descriptive alt text:
- Bad: `![](./assets/demo.png)`
- Good: `![Dashboard showing the project's main interface](./assets/demo.png)`

## Badge policy

- Target 3–6 badges, hard cap 7.
- Only badges backed by real evidence: CI status (from an actual workflow), package version (from the manifest), license (from `LICENSE`), coverage (from real coverage config/CI), runtime/language version (from manifest constraints), registry/downloads (only if actually published), platform support (only if actually tested/declared).
- If a dynamic badge isn't feasible, a descriptive static badge is fine *as long as the underlying fact is verified* (e.g. "Python 3.13", "CLI", "Docker", "Open Source" when a license is genuinely present).
- Never badge: nonexistent CI, nonexistent coverage, unsupported runtimes, fake download counts, fake versions, a license not present in the repo, or "production ready" style status claims.

## Tagline rules

One sentence: what it does, ideally for whom. No vague marketing language.
- Good: "A CLI for converting and optimizing images directly from the terminal."
- Bad: "The next-generation revolutionary solution for modern workflows."

## Quick navigation / TOC

For medium/large READMEs, add a nav line near the top: `Documentation · Installation · Usage · Development · Contributing`. For very large READMEs, add a real table of contents. Skip both for short READMEs — an unnecessary TOC is itself an anti-pattern.

## Emoji policy

One emoji per semantic section, used consistently:

```text
📖 About              🏗️ Technical Overview   🔐 Security
✨ Features            🏛️ Architecture         ⚠️ Limitations
🧠 How It Works        📁 Project Structure    🗺️ Roadmap
📋 Requirements        🔄 Internal Flow        🤝 Contributing
📦 Installation        🗄️ Data Model           💬 Support
⚙️ Configuration       🔌 API                  📜 Releases
🚀 Quick Start         🧑‍🔧 Development          👥 Maintainers
🧑‍💻 Usage              🧪 Testing               🙏 Acknowledgements
⬆️ Updating            🔁 CI/CD                📄 License
🗑️ Uninstallation
🛠️ Troubleshooting
❓ FAQ
```
Do not vary the emoji for the same semantic section across repositories unless there's a clear reason.

## Writing style

**End-user documentation**: plain language, short paragraphs, direct instructions, numbered procedures, copyable commands, complete examples, expected results. Explain unfamiliar concepts before relying on them. A user should be able to install and use the project without reading source code.

**Technical documentation**: precise terminology, real module/directory/script/config names, architecture diagrams, tables where useful, concise but not oversimplified to the point of inaccuracy.

**Progressive disclosure**: simple → practical → operational → technical → architectural → contributor-focused, top to bottom. Never start with internals.

## Claims policy

Avoid unsupported marketing language unless objectively backed by evidence in-repo: "blazing fast", "production ready", "enterprise ready", "100% secure", "zero configuration", "best in class", "highly scalable", "lightning fast", "battle tested." Replace with measurable, specific capabilities.

## Links

Prefer relative links for repo files: `[Contributing](./CONTRIBUTING.md)`. Prefer relative image paths: `![Screenshot](./assets/screenshot.png)`. Avoid fragile external asset URLs for images that belong to the repo.

## Code examples

Every code block: correct language identifier, realistic code matching the actual project API, minimal but complete enough to run when presented as executable, placeholders clearly marked as placeholders.
- Good: a real `npm install` / `npm run dev` pair.
- Bad: `do some setup here`.

## Tables

Use for environment variables, commands, tech stack, compatibility matrices, configuration options. Don't force every section into a table.

## Diagrams

Use Mermaid (`flowchart`, sequence, class, state, ER) when it genuinely clarifies architecture or process flow. Keep diagrams readable and grounded in real components — never decorative, never fabricated.

## README size management

If a section grows too large, move detail to `/docs` (e.g. `docs/installation.md`, `docs/architecture.md`, `docs/api.md`, `docs/deployment.md`, `docs/troubleshooting.md`) and leave a concise summary + link in the README. The README stays the entry point, not the entire manual.

## Anti-patterns to actively avoid

Excessive badges; giant logos; meaningless slogans; fake metrics; fake compatibility claims; unverified commands; unexplained code blocks; explaining internals before usage; dumping the entire repo tree; huge API docs inside the README; screenshots with no context; broken external image URLs; empty sections; invented roadmap items; assumed licenses; nonexistent CI badges; inconsistent headings; unnecessary duplication; giant walls of text; excessive callouts; excessive emoji usage.
