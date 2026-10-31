"""Load a scenario folder and its scenario.json (PFR1)."""
import json
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "scenarios"
RESULTS = ROOT / "results"

# Folders inside a scenario that are not part of the code under study.
EXCLUDED = {"tests", "solution", "__pycache__", ".pytest_cache"}


@dataclass(frozen=True)
class Scenario:
    path: Path
    title: str
    entry: str
    argv: tuple[str, ...]
    defect_file: str
    defect_line: int
    expected_calls: tuple[tuple[str, str], ...]
    origin: str

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def id(self) -> str:
        return self.name.split("_", 1)[0]

    @property
    def is_stand_in(self) -> bool:
        return self.origin == "stand-in"

    def source_files(self) -> list[Path]:
        """The scenario's own .py files, excluding tests and the solution."""
        return sorted(
            p for p in self.path.rglob("*.py")
            if not EXCLUDED & set(p.relative_to(self.path).parts[:-1])
        )

    def module_name(self, path: Path) -> str:
        return ".".join(path.resolve().relative_to(self.path.resolve()).with_suffix("").parts)

    @contextmanager
    def workspace(self, fixed: bool = False):
        """Yield a copy of this scenario in a temporary folder, optionally with the solution applied."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            copy = self.copy_to(Path(tmp), fixed)
            yield copy

    def copy_to(self, target: Path, fixed: bool = False) -> "Scenario":
        shutil.copytree(self.path, target, ignore=shutil.ignore_patterns(*EXCLUDED - {"tests"}),
                        dirs_exist_ok=True)
        if fixed:
            shutil.copytree(self.path / "solution", target, dirs_exist_ok=True)
        return replace(self, path=target)


def load(key: str) -> Scenario:
    """Load a scenario by folder name (a_intent_conflict) or id (a)."""
    matches = [p for p in SCENARIOS.iterdir() if p.is_dir() and key in (p.name, p.name.split("_", 1)[0])]
    if not matches:
        raise SystemExit(f"No scenario called '{key}'. Available: {', '.join(s.id for s in all_scenarios())}")
    path = matches[0]
    config = json.loads((path / "scenario.json").read_text(encoding="utf-8"))
    return Scenario(
        path=path,
        title=config["title"],
        entry=config["entry"],
        argv=tuple(config.get("argv", [])),
        defect_file=config["defect"]["file"],
        defect_line=config["defect"]["line"],
        expected_calls=tuple(tuple(c) for c in config["expected_calls"]),
        origin=config["origin"],
    )


def all_scenarios() -> list[Scenario]:
    return [load(p.name) for p in sorted(SCENARIOS.iterdir()) if (p / "scenario.json").exists()]
