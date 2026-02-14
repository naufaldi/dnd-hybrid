#!/usr/bin/env python3
"""Scene validation script to check all scene files for errors.

Run with: python scripts/validate_scenes.py
Exit code: 0 if all valid, 1 if errors found
"""

import sys
import yaml
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """Represents a validation issue."""

    file: str
    issue_type: str  # 'error', 'warning', 'info'
    message: str
    line: int = 0


@dataclass
class ValidationReport:
    """Report of all validation issues."""

    issues: List[ValidationIssue] = field(default_factory=list)
    files_checked: int = 0
    scenes_found: int = 0

    def add_error(self, file: str, message: str, line: int = 0):
        self.issues.append(ValidationIssue(file, "error", message, line))

    def add_warning(self, file: str, message: str, line: int = 0):
        self.issues.append(ValidationIssue(file, "warning", message, line))

    def add_info(self, file: str, message: str, line: int = 0):
        self.issues.append(ValidationIssue(file, "info", message, line))

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.issue_type == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.issue_type == "warning"]

    def print_report(self):
        """Print formatted report."""
        print("=" * 80)
        print("SCENE VALIDATION REPORT")
        print("=" * 80)
        print(f"\nFiles checked: {self.files_checked}")
        print(f"Scenes found: {self.scenes_found}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n" + "=" * 80)
            print("ERRORS (must fix)")
            print("=" * 80)
            for issue in self.errors:
                print(f"\n❌ {issue.file}")
                print(f"   Line {issue.line}: {issue.message}")

        if self.warnings:
            print("\n" + "=" * 80)
            print("WARNINGS (should fix)")
            print("=" * 80)
            for issue in self.warnings:
                print(f"\n⚠️  {issue.file}")
                print(f"   {issue.message}")

        if not self.errors and not self.warnings:
            print("\n✅ All scenes valid!")

        print("\n" + "=" * 80)


class SceneValidator:
    """Validates scene YAML files."""

    # Invalid Rich markup patterns
    INVALID_MARKUP = [
        "[size=",
        "[/size]",
        "[font=",
        "[color=",  # Should use [red], [blue], etc.
    ]

    # Required scene fields
    REQUIRED_SCENE_FIELDS = ["id", "title", "description", "choices"]

    # Valid choice fields
    VALID_CHOICE_FIELDS = [
        "id",
        "text",
        "shortcut",
        "next_scene",
        "consequences",
        "skill_check",
        "required_flags",
        "set_flags",
        "required_mechanics",
        "combat_encounter",
        "victory_next_scene",
        "defeat_scene",
    ]

    def __init__(self, scenes_dir: Path):
        self.scenes_dir = scenes_dir
        self.report = ValidationReport()
        self.all_scene_ids: set = set()
        self.all_references: List[Tuple[str, str]] = []  # (source_scene, target_scene)

    def validate_all(self) -> ValidationReport:
        """Validate all scene files."""
        scene_files = list(self.scenes_dir.rglob("*.yaml"))
        self.report.files_checked = len(scene_files)

        # First pass: collect all scene IDs
        for scene_file in scene_files:
            scene_id = self._extract_scene_id(scene_file)
            if scene_id:
                self.all_scene_ids.add(scene_id)

        # Second pass: validate each scene
        for scene_file in scene_files:
            self._validate_scene_file(scene_file)

        # Third pass: check references
        self._validate_references()

        return self.report

    def _extract_scene_id(self, scene_file: Path) -> str:
        """Extract scene ID from file without full validation."""
        try:
            with open(scene_file, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                return content.get("id", "") if content else ""
        except Exception:
            return ""

    def _validate_scene_file(self, scene_file: Path):
        """Validate a single scene file."""
        try:
            with open(scene_file, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.report.add_error(
                str(scene_file),
                f"YAML parsing error: {e}",
                getattr(e, "problem_mark", None) and e.problem_mark.line or 0,
            )
            return
        except Exception as e:
            self.report.add_error(str(scene_file), f"Failed to read file: {e}")
            return

        if not content:
            self.report.add_error(str(scene_file), "Empty scene file")
            return

        self.report.scenes_found += 1

        # Check required fields
        for field in self.REQUIRED_SCENE_FIELDS:
            if field not in content:
                self.report.add_error(str(scene_file), f"Missing required field: '{field}'")

        # Validate scene ID matches filename (optional but good practice)
        scene_id = content.get("id", "")
        expected_id = scene_file.stem
        if scene_id and scene_id != expected_id:
            self.report.add_warning(
                str(scene_file), f"Scene ID '{scene_id}' doesn't match filename '{expected_id}'"
            )

        # Validate description for invalid markup
        description = content.get("description", "")
        self._validate_markup(str(scene_file), description)

        # Validate choices
        choices = content.get("choices", [])
        if not isinstance(choices, list):
            self.report.add_error(str(scene_file), "'choices' must be a list")
            return

        for i, choice in enumerate(choices):
            if not isinstance(choice, dict):
                self.report.add_error(str(scene_file), f"Choice {i} is not a valid object")
                continue

            self._validate_choice(str(scene_file), choice, i)

    def _validate_markup(self, file_path: str, text: str):
        """Check text for invalid markup."""
        if not isinstance(text, str):
            return

        for pattern in self.INVALID_MARKUP:
            if pattern in text:
                self.report.add_error(file_path, f"Invalid Rich markup pattern found: '{pattern}'")

    def _validate_choice(self, file_path: str, choice: dict, index: int):
        """Validate a single choice."""
        # Check required choice fields
        if "id" not in choice:
            self.report.add_error(file_path, f"Choice {index} missing required field: 'id'")

        if "text" not in choice:
            self.report.add_error(file_path, f"Choice {index} missing required field: 'text'")

        # Check for invalid fields
        for field in choice.keys():
            if field not in self.VALID_CHOICE_FIELDS:
                self.report.add_error(file_path, f"Choice {index} has invalid field: '{field}'")

        # Collect references to other scenes
        next_scene = choice.get("next_scene")
        if next_scene:
            self.all_references.append((file_path, next_scene))

        # Check skill check references
        skill_check = choice.get("skill_check", {})
        if skill_check:
            success = skill_check.get("success_next_scene")
            failure = skill_check.get("failure_next_scene")
            if success:
                self.all_references.append((file_path, success))
            if failure:
                self.all_references.append((file_path, failure))

        # Check combat navigation
        victory = choice.get("victory_next_scene")
        defeat = choice.get("defeat_scene")
        if victory:
            self.all_references.append((file_path, victory))
        if defeat:
            self.all_references.append((file_path, defeat))

    def _validate_references(self):
        """Check that all scene references point to existing scenes."""
        for source, target in self.all_references:
            if target not in self.all_scene_ids:
                self.report.add_error(source, f"References non-existent scene: '{target}'")


def main():
    """Main entry point."""
    # Find scenes directory
    script_dir = Path(__file__).parent.parent
    scenes_dir = script_dir / "src" / "story" / "scenes"

    if not scenes_dir.exists():
        print(f"Error: Scenes directory not found: {scenes_dir}")
        sys.exit(1)

    # Run validation
    validator = SceneValidator(scenes_dir)
    report = validator.validate_all()
    report.print_report()

    # Exit with appropriate code
    sys.exit(1 if report.errors else 0)


if __name__ == "__main__":
    main()
