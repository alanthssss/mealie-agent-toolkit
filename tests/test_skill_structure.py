import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "mealie-quality-operator"


class SkillStructureTests(unittest.TestCase):
    def test_frontmatter_and_references(self):
        skill_path = SKILL_DIR / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match, "SKILL.md must start with YAML frontmatter")
        metadata = yaml.safe_load(match.group(1))
        self.assertEqual(metadata["name"], SKILL_DIR.name)
        self.assertRegex(metadata["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertTrue(1 <= len(metadata["description"]) <= 1024)
        self.assertNotIn("TO" + "DO", text)
        self.assertLessEqual(len(text.splitlines()), 500)
        for relative in re.findall(r"\]\((references/[^)]+)\)", text):
            self.assertTrue((SKILL_DIR / relative).is_file(), f"missing reference: {relative}")

    def test_openai_interface_mentions_skill(self):
        config = yaml.safe_load((SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8"))
        self.assertIn("$mealie-quality-operator", config["interface"]["default_prompt"])


if __name__ == "__main__":
    unittest.main()
