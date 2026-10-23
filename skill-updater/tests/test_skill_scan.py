from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import skill_scan  # noqa: E402


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_skill(root: Path, name: str = "demo-skill", description: str = "Faz algo útil. Use quando…") -> Path:
    skill = root / name
    write_text(skill / "SKILL.md", f"---\nname: {name}\ndescription: >-\n  {description}\n---\n\n# Demo\n\nVeja [ref](references/a.md).\n")
    write_text(skill / "references" / "a.md", "# A\n")
    return skill


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / "skill_scan.py"), *args],
                          capture_output=True, text=True, encoding="utf-8")


class FrontmatterTests(unittest.TestCase):
    def test_folded_block_and_scalars(self):
        meta, error = skill_scan.parse_frontmatter("---\nname: x\ndescription: >-\n  linha um\n  linha dois\n---\nbody")
        self.assertIsNone(error)
        self.assertEqual(meta, {"name": "x", "description": "linha um linha dois"})

    def test_missing_frontmatter(self):
        _, error = skill_scan.parse_frontmatter("# sem frontmatter")
        self.assertIn("frontmatter", error)


class InventoryTests(unittest.TestCase):
    def test_collects_dependencies(self):
        with tempfile.TemporaryDirectory() as raw:
            skill = make_skill(Path(raw))
            write_text(skill / "references" / "b.md", "\n".join([
                "Instale com `pip install requests==2.31.0 rich`.",
                "Modelo: whisper large-v3, em 21/10/2026.",
                "Ferramenta fixada no commit `0670e4fdf95a`.",
                "Repo: https://github.com/owner/tool e https://huggingface.co/org/model-x.",
                "Docs: https://huggingface.co/docs/hub e https://github.com/apps/claude.",
            ]))
            write_text(skill / "scripts" / "run.py", "import json\nimport numpy\nimport helper\n")
            write_text(skill / "scripts" / "helper.py", "X = 1\n")
            inv = skill_scan.inventory_skill(skill)

        self.assertEqual(inv["github_repos"], ["owner/tool"])
        self.assertEqual(inv["hf_repos"], ["models:org/model-x"])
        self.assertIn({"name": "requests", "op": "==", "version": "2.31.0", "at": "references/b.md:1"}, inv["pins"])
        self.assertEqual([c["sha"] for c in inv["commits"]], ["0670e4fdf95a"])
        self.assertEqual(inv["newest_date_mentioned"], "2026-10-21")
        self.assertIn("whisper large-v3", [m["model"] for m in inv["model_mentions"]])
        imports = [p for p in inv["packages"] if p["tool"] == "python-import"]
        self.assertEqual(imports[0]["packages"], ["numpy"])  # stdlib and local modules left out

    def test_ignores_words_that_only_start_like_models(self):
        with tempfile.TemporaryDirectory() as raw:
            skill = make_skill(Path(raw))
            write_text(skill / "references" / "b.md", "Follow the same four-layer layout; o qwen else 150.\n")
            inv = skill_scan.inventory_skill(skill)
        self.assertEqual(inv["model_mentions"], [])

    def test_ip_addresses_are_not_pins(self):
        with tempfile.TemporaryDirectory() as raw:
            skill = make_skill(Path(raw))
            write_text(skill / "references" / "b.md", "dig @8.8.8.8 exemplo.com\nif n>=25 and k==0:\n")
            inv = skill_scan.inventory_skill(skill)
        self.assertEqual(inv["pins"], [])


class LatestHelpersTests(unittest.TestCase):
    def test_package_names(self):
        self.assertEqual(skill_scan._pkg_name("diffusers==0.32.2"), "diffusers")
        self.assertEqual(skill_scan._pkg_name('"rembg[cpu]"'), "rembg")
        self.assertEqual(skill_scan._pkg_name("@scope/pkg@1.2.0"), "@scope/pkg")
        self.assertEqual(skill_scan._pkg_name("cv2"), "opencv-python")
        self.assertIsNone(skill_scan._pkg_name("2"))
        self.assertIsNone(skill_scan._pkg_name("https://download.pytorch.org/whl/cpu"))

    def test_package_versions(self):
        self.assertEqual(skill_scan._pkg_version("diffusers==0.32.2"), "0.32.2")
        self.assertEqual(skill_scan._pkg_version("react@^18.2.0"), "18.2.0")
        self.assertEqual(skill_scan._pkg_version("@scope/pkg@1.2.0"), "1.2.0")
        self.assertIsNone(skill_scan._pkg_version("rich"))

    def test_compare(self):
        self.assertEqual(skill_scan.compare("4.48.0", "5.20.2"), "atrás (major)")
        self.assertEqual(skill_scan.compare("0.32.2", "0.42.0"), "atrás (minor)")
        self.assertEqual(skill_scan.compare("1.2.0", "1.2.3"), "atrás (patch)")
        self.assertEqual(skill_scan.compare("0.6", "0.6"), "em dia")
        self.assertEqual(skill_scan.compare(None, "1.0"), "")

    def test_norm_name(self):
        self.assertEqual(skill_scan.norm_name("faster_whisper"), skill_scan.norm_name("Faster-Whisper"))


class LinksTests(unittest.TestCase):
    def test_placeholders(self):
        for url in ("http://localhost:PORTA", "http://IP_DA_VPS", "https://dominio.com",
                    "https://$host$request_uri", "https://github.com/usuario/repo.git"):
            self.assertTrue(skill_scan.is_placeholder(url), url)
        self.assertFalse(skill_scan.is_placeholder("https://pypi.org/project/rich/"))

    def test_clean_url(self):
        self.assertEqual(skill_scan.clean_url("https://x.org/a)."), "https://x.org/a")
        self.assertEqual(skill_scan.clean_url("https://en.wikipedia.org/wiki/A_(b)"), "https://en.wikipedia.org/wiki/A_(b)")


class ValidateTests(unittest.TestCase):
    def test_valid_skill(self):
        with tempfile.TemporaryDirectory() as raw:
            result = skill_scan.validate_skill(make_skill(Path(raw)))
        self.assertTrue(result["ok"], result)

    def test_errors(self):
        with tempfile.TemporaryDirectory() as raw:
            skill = make_skill(Path(raw), name="Bad_Name", description="x" * 1100)
            write_text(skill / "references" / "a.md", "[quebrado](nao-existe.md) e `[exemplo](./LICENSE)`\n")
            write_text(skill / "scripts" / "x.py", "def (:\n")
            write_text(skill / "assets" / "y.json", "{nope}")
            result = skill_scan.validate_skill(skill)
        text = "\n".join(result["errors"])
        self.assertFalse(result["ok"])
        self.assertIn("fora do padrão", text)
        self.assertIn("1100 caracteres", text)
        self.assertIn("nao-existe.md", text)
        self.assertNotIn("LICENSE", text)  # inline code is an example, not a link
        self.assertIn("SyntaxError", text)
        self.assertIn("JSON inválido", text)


class CliTests(unittest.TestCase):
    def test_inventory_and_validate_json(self):
        with tempfile.TemporaryDirectory() as raw:
            make_skill(Path(raw), "a-skill")
            make_skill(Path(raw), "b-skill")
            inventory = run_cli("inventory", raw, "--json")
            validate = run_cli("validate", raw, "--json")
        self.assertEqual(inventory.returncode, 0, inventory.stderr)
        self.assertEqual(sorted(r["skill"] for r in json.loads(inventory.stdout)), ["a-skill", "b-skill"])
        self.assertEqual(validate.returncode, 0, validate.stderr)

    def test_validate_exit_code(self):
        with tempfile.TemporaryDirectory() as raw:
            skill = make_skill(Path(raw))
            write_text(skill / "SKILL.md", "sem frontmatter\n")
            result = run_cli("validate", str(skill))
        self.assertEqual(result.returncode, 1)

    def test_no_skill_found(self):
        with tempfile.TemporaryDirectory() as raw:
            result = run_cli("inventory", raw)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
