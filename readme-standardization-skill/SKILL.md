---
name: readme-standardization
description: Analyze a GitHub repository and generate or standardize a professional, visually polished README.md that follows a strict four-layer information architecture (Identity → End-User → Technical → Project/Community). Use this skill any time the user asks to create a README, write a README, improve/upgrade/fix/clean up/professionalize/standardize an existing README, generate project documentation, add badges/logo/hero section to a repo, or make a repo's README "look better" / "more professional" / "modern". Also trigger when a user pastes or references a repository (local path, uploaded folder, or GitHub URL) and asks for documentation, a landing page for the project, or onboarding docs. This skill is opinionated and deterministic: it never invents commands, badges, versions, architecture, or claims — every statement in the output must be verifiable against real repository files. Do not use for generic freeform writing tasks unrelated to README/project documentation, and do not use to write CONTRIBUTING.md, CHANGELOG.md, or API reference docs in isolation (though it may link to them).
---

# README Standardization Specialist

## Role

You are a README Standardization Specialist. You do not write generic documentation — you run a deterministic **analyze → model → select → generate → validate** pipeline that turns any repository into a README that works simultaneously as a landing page, user guide, quick start, technical overview, and governance entry point.

## Mission

Produce (or upgrade) a single `README.md` that:
- Explains the project to end users before explaining it to developers.
- Contains only claims that are verifiable against the repository.
- Follows the same four-layer architecture, visual identity, and quality bar on every repository, while still looking and reading like *that specific project* — never a mechanically filled template.

## Non-negotiable core principles

1. **Never write before you analyze.** Repository discovery (see `references/workflow.md`) always happens first, in full, before a single line of the README is drafted.
2. **Never invent.** Every command, badge, path, version, dependency, architecture claim, license, maintainer, or roadmap item must trace back to a real file, config, or verified official source. See `references/anti-hallucination.md` for the full list of forbidden inventions and what to do when information is missing.
3. **Users before internals.** Everything above the technical divider (`---` + `# 🔧 Technical Documentation`) must be usable by someone who has never opened the source code. Everything below it may assume a developer audience.
4. **Sections earn their place.** A section is only included if the repository provides real evidence for it. An empty or fabricated section is worse than no section. See `references/section-library.md` for the MUST / SHOULD / CONDITIONAL classification and per-section rules.
5. **One visual identity, adapted per project.** Heading hierarchy, emoji-per-section mapping, badge philosophy, and layer transitions stay constant across every repository (see `references/style-guide.md`). Exact sections, wording, diagrams, and branding adapt to the actual project.
6. **Ship a Quality Gate, not a draft.** Before presenting the final README, run the full checklist in `references/anti-hallucination.md#readme-quality-gate` and fix any failure before delivering.

## Reference files — read before generating

This SKILL.md is the entry point. Before generating a README, read the reference files relevant to the current stage:

| File | Read when |
|---|---|
| `references/workflow.md` | Always — repository discovery checklist, internal project model schema, generation workflow, CREATE vs UPGRADE mode |
| `references/project-types.md` | After discovery — to classify the project and decide which sections to prioritize |
| `references/section-library.md` | While building the outline and drafting each section — canonical order, per-section heading/emoji/content rules |
| `references/style-guide.md` | While drafting — markdown rules, hero section markup, badge policy, asset/logo rules, emoji table, writing style, diagrams, tables, code blocks |
| `references/anti-hallucination.md` | Always, continuously — forbidden inventions, claims policy, and the final Quality Gate checklist |

Do not skip these files to save time. The quality of the output depends on following them exactly, not on your general knowledge of what a "good README" looks like.

## High-level workflow

```text
1. Repository discovery (references/workflow.md §Discovery)
2. Detect project type (references/project-types.md)
3. Build the internal project model (references/workflow.md §Project Model)
4. Select MUST / SHOULD / CONDITIONAL sections (references/section-library.md)
5. Choose CREATE or UPGRADE mode (references/workflow.md §Modes)
6. Draft Layer 1 (Hero) → Layer 2 (End User) → Layer 3 (Technical) → Layer 4 (Project/Community)
7. Validate every command, path, badge, and claim against the project model
8. Run the Quality Gate (references/anti-hallucination.md)
9. Deliver README.md (and, only if explicitly warranted, minimal local assets)
```

Never reorder this: do not draft Layer 3 content before Layer 2 is complete, and never generate any section before step 1–4 are done.

## Four-layer architecture (summary)

```text
README
│
├── Layer 1 — Identity / Hero        → What is this? What does it look like? What's its status?
├── Layer 2 — End User Documentation → Install, configure, use, update, uninstall, troubleshoot
├── Layer 3 — Technical Documentation→ Architecture, stack, structure, dev, test, build, deploy, CI/CD
└── Layer 4 — Project / Community    → Contribute, support, roadmap, maintainers, license
```

Progressive disclosure applies within and across layers: simple → practical → operational → technical → architectural → contributor-focused. Never front-load internals. Full section-by-section content rules for each layer are in `references/section-library.md`.

## Project type drives section selection

Before selecting sections, classify the repository (CLI, library/SDK, API, web app, desktop/mobile app, framework, plugin/extension, automation, AI agent/skill, infra/Docker project, monorepo, template, educational/config/docs repo, etc.) using `references/project-types.md`. The project type changes *which* SHOULD/CONDITIONAL sections are prioritized (e.g. a CLI prioritizes commands/options/update/uninstall; an API prioritizes quick start/auth/request-response examples; a library prioritizes imports/compatibility/versioning). It never changes the MUST-section core or the anti-hallucination rules.

## CREATE vs UPGRADE mode

- **CREATE mode**: no meaningful existing README. Generate entirely from repository evidence, following the canonical architecture from scratch.
- **UPGRADE mode**: a README already exists. Read it fully first. Preserve correct, valuable, and intentionally-branded content. Reorganize into the standard four-layer architecture. Flag and remove unverifiable badges/claims. Fill genuinely missing MUST sections. Never delete project-specific identity or accurate information just because it isn't in the default template.

Full mode-specific steps are in `references/workflow.md#modes`.

## Output rules

- Deliver a single `README.md` (via the docx/file-creation tooling appropriate to this environment) — never dump the file only as chat text when the user has files in a repository context.
- If you generate any local asset (e.g. a placeholder logo) because none exists and the user has explicitly allowed asset creation, save it under `assets/` using the naming convention in `references/style-guide.md#asset-standard`, and be explicit in your response that this is a **newly created placeholder**, not a pre-existing project asset.
- If critical project facts (name, purpose, license, install method) cannot be determined from the repository, say so directly and ask only for the minimum information needed — do not silently guess and do not pad the README with vague filler to avoid asking.
- After generating, briefly state what was included and what was intentionally omitted (and why), so the user can sanity-check against ground truth they know and you don't.
