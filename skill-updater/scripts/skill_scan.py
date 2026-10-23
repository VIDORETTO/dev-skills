#!/usr/bin/env python3
"""Deterministic helpers for the skill-updater skill.

The skill decides *what* is outdated and *what* to change.  This script only
collects facts that do not need a model:

  inventory  what a skill depends on (links, versions, packages, repos,
             models, dates, pinned commits) and how old it is in git
  latest     current version/date of those packages, repos and models
             (PyPI, npm, GitHub, Hugging Face)
  links      HTTP status of every external link
  validate   frontmatter, relative links, scripts and JSON after an edit

Standard library only, so it runs anywhere the skill is copied.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".sh", ".ps1", ".js", ".mjs", ".ts", ".json",
    ".yaml", ".yml", ".toml", ".cfg", ".ini",
}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
USER_AGENT = "skill-updater/1.0 (+https://github.com/VIDORETTO/dev-skills)"

URL_RE = re.compile(r"https?://[^\s<>\"'`)\]}|]+")
ISO_DATE_RE = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b")
BR_DATE_RE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d\d)\b")
VERSION_RE = re.compile(
    r"(?<![\w.])(?:v\d+(?:\.\d+){1,3}|\d+\.\d+\.\d+(?:[-.]?(?:rc|beta|alpha|b|a)\d*)?)(?![\w.])"
)
PIN_RE = re.compile(r"\b([A-Za-z][\w-]*)\s*(==|>=|~=|@)\s*v?(\d+(?:\.\d+){1,2})(?![.\d])")
COMMIT_CONTEXT_RE = re.compile(r"commit|checkout|sha|hash|pinned|fixad", re.I)
COMMIT_RE = re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")
MODEL_RE = re.compile(
    r"\b(?:claude|gpt|o[134]|gemini|gemma|llama|qwen|mistral|mixtral|deepseek|phi|"
    r"grok|kimi|glm|minimax|flux|sdxl|sd3|stable-diffusion|wan|hunyuan|ltx|veo|sora|"
    r"kling|whisper|sam|nano-banana|imagen|midjourney|seedance|seedream)(?![a-z])"
    r"(?:[-_.]?[\w.]+|\s(?=\S*\d)[\w.]+){0,3}",
    re.I,
)
INSTALL_RE = re.compile(
    r"\b(pip3?|uv pip|uv|pipx|poetry|npm|pnpm|yarn|bun|apt(?:-get)?|brew|cargo|go)\s+"
    r"(?:install|add|i|get)\s+([^\n`#;&|>]+)"
)
GITHUB_RE = re.compile(r"https?://github\.com/([\w.-]+)/([\w.-]+)")
HF_RE = re.compile(r"https?://huggingface\.co/(?:(spaces|datasets)/)?([\w.-]+)/([\w.-]+)")
HF_RESERVED = {"api", "docs", "blog", "papers", "learn", "models", "posts", "settings", "join", "login", "pricing", "collections", "organizations"}
GITHUB_RESERVED = {"apps", "orgs", "settings", "features", "topics", "marketplace", "sponsors", "login", "about"}
IMPORT_TO_PYPI = {
    "cv2": "opencv-python", "PIL": "pillow", "sklearn": "scikit-learn", "skimage": "scikit-image",
    "yaml": "pyyaml", "bs4": "beautifulsoup4", "dotenv": "python-dotenv", "fitz": "pymupdf",
    "docx": "python-docx", "pptx": "python-pptx", "attr": "attrs", "dateutil": "python-dateutil",
}
PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net", "dominio.com", "seudominio.com", "yourdomain.com", "localhost"}
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
LOCAL_REF_RE = re.compile(r"`((?:references|scripts|assets|templates|agents|shared)/[\w./-]+)`")


# --------------------------------------------------------------------------- helpers


def find_skills(paths: Iterable[str]) -> list[Path]:
    """Every directory that holds a SKILL.md under the given paths."""
    found: list[Path] = []
    for raw in paths:
        p = Path(raw).resolve()
        if p.is_file() and p.name == "SKILL.md":
            p = p.parent
        if (p / "SKILL.md").is_file():
            found.append(p)
            continue
        for skill_md in sorted(p.rglob("SKILL.md")):
            if not SKIP_DIRS.intersection(skill_md.parts):
                found.append(skill_md.parent)
    unique = sorted(set(found))
    if not unique:
        sys.exit(f"nenhum SKILL.md encontrado em: {', '.join(paths)}")
    return unique


def iter_text_files(skill_dir: Path) -> Iterable[Path]:
    for path in sorted(skill_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not SKIP_DIRS.intersection(path.parts):
            yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    """Tiny YAML subset: scalar keys and folded/literal blocks (>, >-, |, |-)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "SKILL.md não começa com frontmatter '---'"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, "frontmatter sem '---' de fechamento"
    data: dict[str, str] = {}
    i = 1
    while i < end:
        line = lines[i]
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, value = m.group(1), m.group(2).strip()
        if value in {">", ">-", "|", "|-", ">+", "|+"}:
            block: list[str] = []
            i += 1
            while i < end and (not lines[i].strip() or lines[i].startswith((" ", "\t"))):
                block.append(lines[i].strip())
                i += 1
            sep = "\n" if value.startswith("|") else " "
            data[key] = sep.join(b for b in block if b).strip()
            continue
        data[key] = value.strip().strip("\"'")
        i += 1
    return data, None


def git_last_change(path: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=path if path.is_dir() else path.parent,
            capture_output=True, text=True, timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = out.stdout.strip()
    return value or None


def days_since(iso: str | None) -> int | None:
    if not iso:
        return None
    try:
        return (date.today() - date.fromisoformat(iso[:10])).days
    except ValueError:
        return None


def clean_url(url: str) -> str:
    url = url.rstrip(".,;:!?*_")
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1]
    return url


def ssl_context() -> ssl.SSLContext:
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    return ssl.create_default_context(cafile=cafile) if cafile and Path(cafile).is_file() else ssl.create_default_context()


def http(url: str, method: str = "GET", headers: dict[str, str] | None = None, timeout: float = 15.0,
         read_body: bool = True) -> tuple[int, str, bytes]:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
            body = resp.read() if method == "GET" and read_body else b""
            return resp.status, resp.geturl(), body
    except urllib.error.HTTPError as exc:
        return exc.code, url, b""


def get_json(url: str, headers: dict[str, str] | None = None) -> Any:
    status, _, body = http(url, headers=headers)
    if status != 200:
        raise RuntimeError(f"HTTP {status}")
    return json.loads(body)


def emit(payload: Any, as_json: bool, render) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render(payload))


# --------------------------------------------------------------------------- inventory


def inventory_skill(skill_dir: Path) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    meta, fm_error = parse_frontmatter(read_text(skill_md))
    files, urls, dates, versions, pins, commits, models, installs = [], {}, [], [], [], [], {}, []
    github, hf = set(), set()

    for path in iter_text_files(skill_dir):
        rel = path.relative_to(skill_dir).as_posix()
        text = read_text(path)
        lines = text.splitlines()
        files.append({"path": rel, "lines": len(lines), "git_last_change": None})
        for n, line in enumerate(lines, 1):
            where = f"{rel}:{n}"
            for raw in URL_RE.findall(line):
                url = clean_url(raw)
                urls.setdefault(url, where)
                if gm := GITHUB_RE.match(url):
                    owner, repo = gm.group(1), gm.group(2).removesuffix(".git")
                    if owner.lower() not in GITHUB_RESERVED:
                        github.add(f"{owner}/{repo}")
                if hm := HF_RE.match(url):
                    kind, owner, name = hm.group(1) or "models", hm.group(2), hm.group(3)
                    if owner.lower() not in HF_RESERVED:
                        hf.add(f"{kind}:{owner}/{name}")
            for y, m, d in ISO_DATE_RE.findall(line):
                dates.append({"date": f"{y}-{m}-{d}", "at": where})
            for d, m, y in BR_DATE_RE.findall(line):
                if 1 <= int(m) <= 12 and 1 <= int(d) <= 31:
                    dates.append({"date": f"{y}-{int(m):02d}-{int(d):02d}", "at": where})
            line_wo_urls = URL_RE.sub(" ", line)
            for v in VERSION_RE.findall(line_wo_urls):
                versions.append({"version": v, "at": where, "context": line.strip()[:160]})
            for name, op, v in PIN_RE.findall(line_wo_urls):
                pins.append({"name": name, "op": op, "version": v, "at": where})
            if COMMIT_CONTEXT_RE.search(line):
                for sha in COMMIT_RE.findall(line_wo_urls):
                    commits.append({"sha": sha, "at": where, "context": line.strip()[:160]})
            for mm in MODEL_RE.finditer(line_wo_urls):
                token = mm.group(0).strip(" .-_")
                if len(token) > 3 and any(c.isdigit() or c == "-" for c in token):
                    models.setdefault(token.lower(), where)
            for tool, args in INSTALL_RE.findall(line):
                pkgs = [a for a in re.split(r"\s+", args.strip()) if a and not a.startswith(("-", "<", "$", "\\"))]
                if pkgs:
                    installs.append({"tool": tool, "packages": pkgs, "at": where})

        if rel.endswith("package.json"):
            try:
                pj = json.loads(text)
                for section in ("dependencies", "devDependencies", "peerDependencies"):
                    for name, spec in (pj.get(section) or {}).items():
                        installs.append({"tool": "npm", "packages": [f"{name}@{spec}"], "at": rel})
            except json.JSONDecodeError:
                pass
        if re.search(r"requirements[^/]*\.txt$", rel):
            pkgs = [ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith(("#", "-"))]
            if pkgs:
                installs.append({"tool": "pip", "packages": pkgs, "at": rel})
        if path.suffix == ".py":
            stdlib = getattr(sys, "stdlib_module_names", set())
            imports = set()
            for m in re.finditer(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", text, re.M):
                mod = m.group(1)
                if mod not in stdlib and mod != "__future__" and not (skill_dir / "scripts" / f"{mod}.py").exists():
                    imports.add(mod)
            if imports:
                installs.append({"tool": "python-import", "packages": sorted(imports), "at": rel})

    last_change = git_last_change(skill_dir)
    for f in files:
        f["git_last_change"] = git_last_change(skill_dir / f["path"])
    newest_mentioned = max((d["date"] for d in dates), default=None)
    return {
        "skill": meta.get("name") or skill_dir.name,
        "dir": str(skill_dir),
        "frontmatter_error": fm_error,
        "description": meta.get("description", ""),
        "git_last_change": last_change,
        "days_since_change": days_since(last_change),
        "newest_date_mentioned": newest_mentioned,
        "days_since_newest_date": days_since(newest_mentioned),
        "files": files,
        "urls": [{"url": u, "at": w} for u, w in urls.items()],
        "github_repos": sorted(github),
        "hf_repos": sorted(hf),
        "packages": installs,
        "pins": pins,
        "versions": versions,
        "commits": commits,
        "model_mentions": [{"model": m, "at": w} for m, w in sorted(models.items())],
        "dates": dates,
    }


def render_inventory(report: list[dict[str, Any]]) -> str:
    out = []
    if len(report) > 1:
        out.append("| Skill | Última mudança (git) | Dias | Data mais recente citada | Links | Pacotes | Repos GH | Repos HF | Versões |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for r in report:
            out.append(
                f"| {r['skill']} | {r['git_last_change'] or '—'} | {r['days_since_change'] if r['days_since_change'] is not None else '—'} "
                f"| {r['newest_date_mentioned'] or '—'} | {len(r['urls'])} | {sum(len(p['packages']) for p in r['packages'])} "
                f"| {len(r['github_repos'])} | {len(r['hf_repos'])} | {len(r['versions'])} |"
            )
        out.append("")
    for r in report:
        out.append(f"## {r['skill']}  ({r['dir']})")
        if r["frontmatter_error"]:
            out.append(f"- ⚠️ frontmatter: {r['frontmatter_error']}")
        out.append(f"- Última mudança no git: {r['git_last_change'] or 'sem histórico'}"
                   + (f" ({r['days_since_change']} dias)" if r["days_since_change"] is not None else ""))
        out.append(f"- Data mais recente citada no texto: {r['newest_date_mentioned'] or 'nenhuma'}")
        out.append(f"- Arquivos: {len(r['files'])} · linhas: {sum(f['lines'] for f in r['files'])}")
        if r["github_repos"]:
            out.append(f"- Repos GitHub: {', '.join(r['github_repos'])}")
        if r["hf_repos"]:
            out.append(f"- Repos Hugging Face: {', '.join(r['hf_repos'])}")
        if r["packages"]:
            out.append("- Pacotes / instalações:")
            for p in r["packages"]:
                out.append(f"  - {p['tool']}: {' '.join(p['packages'])}  ({p['at']})")
        if r["pins"]:
            out.append("- Versões fixadas: " + ", ".join(f"{p['name']}{p['op']}{p['version']} ({p['at']})" for p in r["pins"]))
        if r["commits"]:
            out.append("- Commits fixados: " + ", ".join(f"{c['sha']} ({c['at']})" for c in r["commits"]))
        if r["model_mentions"]:
            out.append("- Modelos/ferramentas citados (candidatos): " + ", ".join(m["model"] for m in r["model_mentions"]))
        if r["versions"]:
            out.append(f"- Números de versão no texto: {len(r['versions'])} (use --json para ver cada um com contexto)")
        out.append(f"- Links externos: {len(r['urls'])}")
        out.append("")
    return "\n".join(out)


def cmd_inventory(args: argparse.Namespace) -> None:
    report = [inventory_skill(d) for d in find_skills(args.paths)]
    report.sort(key=lambda r: -(r["days_since_change"] or 0))
    emit(report, args.json, render_inventory)


# --------------------------------------------------------------------------- latest


def _pkg_name(spec: str) -> str | None:
    spec = spec.strip().strip("'\"")
    if not spec or spec.startswith((".", "/", "git+", "http")) or "/" in spec.lstrip("@").split("@")[0] and not spec.startswith("@"):
        return None
    if spec.startswith("@"):  # scoped npm
        parts = spec.split("@")
        return "@" + parts[1]
    name = re.split(r"[=<>~!\[@;]", spec, maxsplit=1)[0]
    if not re.match(r"^[A-Za-z][\w.-]*$", name):
        return None
    return IMPORT_TO_PYPI.get(name, name)


def latest_pypi(name: str) -> dict[str, Any]:
    data = get_json(f"https://pypi.org/pypi/{name}/json")
    info = data["info"]
    files = data.get("urls") or []
    return {"latest": info.get("version"), "released": (files[0].get("upload_time_iso_8601") or "")[:10] if files else None,
            "yanked": info.get("yanked", False), "url": f"https://pypi.org/project/{name}/"}


def latest_npm(name: str) -> dict[str, Any]:
    data = get_json(f"https://registry.npmjs.org/{name.replace('/', '%2F')}",
                    headers={"Accept": "application/vnd.npm.install-v1+json"})
    latest = (data.get("dist-tags") or {}).get("latest")
    return {"latest": latest, "modified": (data.get("modified") or "")[:10], "url": f"https://www.npmjs.com/package/{name}"}


def latest_github(repo: str) -> dict[str, Any]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    meta = get_json(f"https://api.github.com/repos/{repo}", headers=headers)
    result = {"pushed": (meta.get("pushed_at") or "")[:10], "archived": meta.get("archived"),
              "stars": meta.get("stargazers_count"), "default_branch": meta.get("default_branch"),
              "url": meta.get("html_url"), "renamed_to": meta.get("full_name") if meta.get("full_name", "").lower() != repo.lower() else None}
    try:
        rel = get_json(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
        result.update({"latest": rel.get("tag_name"), "released": (rel.get("published_at") or "")[:10]})
    except RuntimeError:
        result["latest"] = None
    return result


def latest_hf(ref: str) -> dict[str, Any]:
    kind, repo = ref.split(":", 1)
    data = get_json(f"https://huggingface.co/api/{kind}/{repo}")
    return {"modified": (data.get("lastModified") or "")[:10], "downloads": data.get("downloads"),
            "likes": data.get("likes"), "gated": data.get("gated"),
            "url": f"https://huggingface.co/{'' if kind == 'models' else kind + '/'}{repo}"}


def cmd_latest(args: argparse.Namespace) -> None:
    jobs: list[tuple[str, str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add(kind: str, name: str, fn) -> None:
        if (kind, name) not in seen and len(jobs) < args.max:
            seen.add((kind, name))
            jobs.append((kind, name, fn))

    for inv in (inventory_skill(d) for d in find_skills(args.paths)):
        for p in inv["packages"]:
            tool = p["tool"]
            for spec in p["packages"]:
                name = _pkg_name(spec)
                if not name:
                    continue
                if tool in {"pip", "pip3", "uv", "uv pip", "pipx", "poetry", "python-import"}:
                    add("pypi", name, latest_pypi)
                elif tool in {"npm", "pnpm", "yarn", "bun"}:
                    add("npm", name, latest_npm)
        for repo in inv["github_repos"]:
            add("github", repo, latest_github)
        for ref in inv["hf_repos"]:
            add("huggingface", ref, latest_hf)

    def run(job: tuple[str, str, Any]) -> dict[str, Any]:
        kind, name, fn = job
        try:
            return {"source": kind, "name": name, **fn(name)}
        except Exception as exc:  # network, 404, rate limit: report, never crash
            return {"source": kind, "name": name, "error": str(exc)[:200]}

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(run, jobs))

    def render(rows: list[dict[str, Any]]) -> str:
        out = ["| Fonte | Nome | Mais recente | Data | Observação |", "|---|---|---|---|---|"]
        for r in rows:
            note = r.get("error") or ", ".join(
                f"{k}={r[k]}" for k in ("archived", "renamed_to", "stars", "downloads", "gated", "yanked") if r.get(k) not in (None, False, "")
            )
            out.append(f"| {r['source']} | {r['name']} | {r.get('latest') or '—'} | {r.get('released') or r.get('modified') or r.get('pushed') or '—'} | {note} |")
        if os.environ.get("GITHUB_TOKEN") is None and any(r["source"] == "github" for r in rows):
            out.append("\nSem GITHUB_TOKEN a API do GitHub limita a 60 chamadas/hora; erros 403 aqui são limite, não repo inexistente.")
        out.append("\n'python-import' pode trazer nomes de módulo que diferem do pacote no PyPI (cv2 → opencv-python); confira os 404.")
        return "\n".join(out)

    emit(results, args.json, render)


# --------------------------------------------------------------------------- links


def is_placeholder(url: str) -> bool:
    host = urllib.parse.urlsplit(url).hostname or ""
    return (
        any(ch in url for ch in "$<>{}")
        or "." not in host
        or host in PLACEHOLDER_HOSTS
        or host.startswith("127.")
        or re.search(r"[A-Z]{3,}_?[A-Z]*", urllib.parse.urlsplit(url).netloc) is not None
        or re.search(r"github\.com/(usuario|user|owner|seu-usuario)/", url, re.I) is not None
    )


def check_url(url: str) -> dict[str, Any]:
    for method in ("HEAD", "GET"):
        try:
            status, final, _ = http(url, method=method, timeout=12, read_body=False)
        except Exception as exc:
            status, final, err = None, url, str(exc)[:160]
        else:
            err = None
        if status and status < 400:
            return {"url": url, "status": status, "final": final if final != url else None}
        if status not in (403, 405, 429, None) and method == "HEAD":
            continue
    return {"url": url, "status": status, "final": None, "error": err}


def cmd_links(args: argparse.Namespace) -> None:
    where: dict[str, list[str]] = {}
    for d in find_skills(args.paths):
        inv = inventory_skill(d)
        for u in inv["urls"]:
            where.setdefault(u["url"], []).append(f"{inv['skill']}:{u['at']}")
    skipped = sorted(u for u in where if is_placeholder(u))
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(check_url, sorted(set(where) - set(skipped))))
    for r in results:
        r["at"] = where[r["url"]]

    def render(rows: list[dict[str, Any]]) -> str:
        bad = [r for r in rows if not r["status"] or r["status"] >= 400]
        moved = [r for r in rows if r.get("final")]
        out = [f"{len(rows)} links verificados · {len(bad)} com problema · {len(moved)} redirecionados"
               f" · {len(skipped)} ignorados por serem exemplo/placeholder", ""]
        if any("Tunnel connection failed" in str(r.get("error")) for r in bad):
            out += ["'Tunnel connection failed' = o proxy/rede do ambiente bloqueou o host; não prova que o link morreu.", ""]
        if bad:
            out += ["### Com problema (403/429 costuma ser bloqueio anti-bot, não link morto: confira no navegador)",
                    "| Status | URL | Onde |", "|---|---|---|"]
            out += [f"| {r['status'] or r.get('error')} | {r['url']} | {', '.join(r['at'][:3])} |" for r in bad]
            out.append("")
        if moved:
            out += ["### Redirecionados", "| De | Para |", "|---|---|"]
            out += [f"| {r['url']} | {r['final']} |" for r in moved]
        return "\n".join(out)

    emit(results, args.json, render)
    if any(r["status"] == 404 for r in results):
        sys.exit(1)


# --------------------------------------------------------------------------- validate

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_skill(skill_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    text = read_text(skill_md)
    meta, fm_error = parse_frontmatter(text)
    if fm_error:
        errors.append(fm_error)
    name, desc = meta.get("name", ""), meta.get("description", "")
    if not name:
        errors.append("frontmatter sem 'name'")
    elif not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"name '{name}' fora do padrão (minúsculas, números e hífens; até 64)")
    elif name != skill_dir.name:
        warnings.append(f"name '{name}' difere da pasta '{skill_dir.name}'")
    if not desc:
        errors.append("frontmatter sem 'description'")
    elif len(desc) > 1024:
        errors.append(f"description com {len(desc)} caracteres (limite 1024)")
    n_lines = len(text.splitlines())
    if n_lines > 500:
        warnings.append(f"SKILL.md com {n_lines} linhas (recomendado < 500; mova detalhes para references/)")

    for path in iter_text_files(skill_dir):
        rel = path.relative_to(skill_dir).as_posix()
        body = read_text(path)
        if path.suffix == ".md":
            in_fence = False
            for n, line in enumerate(body.splitlines(), 1):
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                if in_fence:
                    continue
                # Links inside inline code or quotes are examples, not navigation.
                prose = re.sub(r'`[^`]*`|"[^"]*"', " ", line)
                for target in MD_LINK_RE.findall(prose):
                    if re.match(r"^(https?:|mailto:|#|<)", target):
                        continue
                    local = target.split("#", 1)[0]
                    if local and not (path.parent / local).exists():
                        errors.append(f"{rel}:{n}: link relativo quebrado → {target}")
                for ref in LOCAL_REF_RE.findall(line):
                    ref = ref.rstrip(".,")
                    if "*" in ref or "<" in ref:
                        continue
                    if not ((skill_dir / ref).exists() or (path.parent / ref).exists()):
                        warnings.append(f"{rel}:{n}: `{ref}` citado mas não existe")
        elif path.suffix == ".py":
            try:
                compile(body, str(path), "exec")
            except SyntaxError as exc:
                errors.append(f"{rel}:{exc.lineno}: SyntaxError {exc.msg}")
        elif path.suffix == ".json":
            try:
                json.loads(body)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}:{exc.lineno}: JSON inválido ({exc.msg})")
    return {"skill": name or skill_dir.name, "dir": str(skill_dir), "ok": not errors, "errors": errors, "warnings": warnings}


def cmd_validate(args: argparse.Namespace) -> None:
    results = [validate_skill(d) for d in find_skills(args.paths)]

    def render(rows: list[dict[str, Any]]) -> str:
        out = []
        for r in rows:
            out.append(f"{'✅' if r['ok'] else '❌'} {r['skill']}  ({r['dir']})")
            out += [f"   erro: {e}" for e in r["errors"]]
            out += [f"   aviso: {w}" for w in r["warnings"]]
        return "\n".join(out)

    emit(results, args.json, render)
    if not all(r["ok"] for r in results):
        sys.exit(1)


# --------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    specs = {
        "inventory": (cmd_inventory, "o que a skill cita e quão velha ela está"),
        "latest": (cmd_latest, "versão/data atual de pacotes, repos GitHub e Hugging Face citados"),
        "links": (cmd_links, "status HTTP de cada link externo (sai com 1 se houver 404)"),
        "validate": (cmd_validate, "valida frontmatter, links relativos, .py e .json (sai com 1 se houver erro)"),
    }
    for name, (fn, help_text) in specs.items():
        p = sub.add_parser(name, help=help_text)
        p.add_argument("paths", nargs="+", help="pasta da skill, SKILL.md ou pasta com várias skills")
        p.add_argument("--json", action="store_true", help="saída em JSON")
        if name == "latest":
            p.add_argument("--max", type=int, default=60, help="máximo de consultas (padrão 60)")
        p.set_defaults(func=fn)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
