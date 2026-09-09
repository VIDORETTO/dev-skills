# Anti-Hallucination Rules & Quality Gate

## Never invent

```text
installation commands       API endpoints              deployment procedures
package names                environment variables      support channels
repository URLs               configuration fields       security guarantees
versions                      file paths / directories   roadmap items
runtime compatibility         architecture components    maintainers / contributors
badges                        license information
download counts / coverage %  benchmarks
```

Every factual statement must trace to: repository files, project documentation, package metadata, configuration, source code, CI workflows, or a verified official external source (e.g. an actual published npm/PyPI page you have evidence for). If you cannot point to the evidence, the claim does not go in the README.

## When information can't be verified

1. Omit it — this is the default and usually correct choice.
2. If omission would leave a MUST section genuinely broken (e.g. no license found at all), state that plainly ("No license file was found in this repository") rather than silently guessing.
3. Ask the user only when the gap blocks a MUST section and no reasonable adaptation exists (e.g. you truly cannot determine the project's name or purpose from anything in the repo).

Never silently guess. Never pad a section with vague filler to avoid admitting a gap.

## Claims policy

Forbidden unless objectively supported by repo evidence: "blazing fast", "production ready", "enterprise ready", "100% secure", "zero configuration", "best in class", "highly scalable", "lightning fast", "battle tested." Replace with specific, measurable capabilities pulled from real features/tests/benchmarks.

## Secrets and sensitive data

Never reproduce real credentials, tokens, private keys, secrets, or internal-only endpoints — even if they appear committed in the repository. If you notice real secrets in tracked files, flag this to the user as a security concern separately from the README content; do not echo the secret value anywhere, including in a "Security" section.

## README Quality Gate

Run this checklist before delivering any README. Fix every failure — do not deliver with known gate failures.

```text
[ ] Correct project name
[ ] Correct description
[ ] Logo or visual identity handled correctly (existing asset preferred; generated placeholder clearly labeled if used)
[ ] Local/relative assets preferred over external links
[ ] Image alt text present and descriptive
[ ] Hero is visually organized (centered, name, tagline, badges, nav)
[ ] Exactly one H1 in the whole document
[ ] Tagline clearly explains the project in one sentence, no marketing fluff
[ ] Badges are verified against repo evidence
[ ] Badge count is 3–7, not excessive
[ ] Relative links used for repo files/images where appropriate
[ ] Installation commands verified against manifest/registry evidence
[ ] Installation includes a verification step when possible
[ ] Configuration values/env vars verified, secrets use placeholders
[ ] Usage is explained before any internals
[ ] Quick Start produces a real, achievable result
[ ] Examples reflect the actual project API/CLI/behavior
[ ] Update instructions verified (or omitted if no real mechanism)
[ ] Uninstallation instructions verified (or omitted if not applicable)
[ ] End-user and technical sections are clearly separated by the divider
[ ] Tech stack / Technical Overview matches repository files exactly
[ ] Architecture reflects actual implementation, no invented components
[ ] Project Structure tree contains only real files/directories
[ ] Development commands are real (exist in manifest/Makefile)
[ ] Testing commands are real; no fabricated coverage percentages
[ ] CI/CD description reflects actual workflow files, not assumed from a badge
[ ] Deployment instructions verified; no secrets exposed
[ ] Security claims are reasonable, not absolute/unsupported
[ ] Limitations listed are real, not invented, not omitted out of politeness
[ ] Roadmap (if present) is sourced from real repo evidence, not fabricated
[ ] Maintainers/contributors listed are verifiable, not scraped commit-history guesses
[ ] License section matches the actual LICENSE file, or states none was found
[ ] No empty sections
[ ] No unsupported/marketing claims remain
[ ] README stays scannable; long detail delegated to /docs where appropriate
[ ] (UPGRADE mode) No valuable project-specific content was deleted without reason
```

If any box can't be checked, either fix the underlying section or remove/adapt it — never ship a README with an unresolved gate failure.
