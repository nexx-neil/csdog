"""Verify the current project and preserved archive, independent of retired migrations."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
R = Path(__file__).resolve().parents[3]
E = R / "reorganization/20261026"

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()

def verify():
    manifest = json.loads((E / "manifest.json").read_text())
    changes = {x["path"]: x for x in json.loads((E / "changes.json").read_text())}
    failures = []
    task_evidence = R / "dogfight_rl/runs/locomotion/csdog_ppo_20261026/protection/task_manifest.json"
    amendments = {}
    new_files = {}
    if task_evidence.is_file():
        task = json.loads(task_evidence.read_text())
        amendments = {row["path"]: row for row in task["changes"]}
        new_files = {row["path"]: row for row in task["new_files"]}
        for row in amendments.values():
            backup = R / row["backup"]
            if not backup.is_file() or sha(backup) != row["before"]:
                failures.append("new-task original protection invalid: " + row["path"])
        for row in new_files.values():
            path = R / row["path"]
            if not path.is_file() or sha(path) != row["sha256"]:
                failures.append("new-task file hash mismatch: " + row["path"])
    def current_expected(path, baseline):
        edit = amendments.get(path)
        if edit:
            if edit["before"] != baseline:
                failures.append("new-task amendment breaks historical seal: " + path)
            return edit["after"]
        return baseline
    for row in manifest["files"]:
        path = R / row["new"]
        change = changes.get(row["new"])
        expected = row["sha256"]
        if change:
            backup = R / change["backup"]
            if change["before"] != expected or not backup.is_file() or sha(backup) != expected:
                failures.append("invalid original backup chain: " + row["new"])
            expected = change["after"]
        expected = current_expected(row["new"], expected)
        if not path.is_file() or sha(path) != expected:
            failures.append("missing or hash mismatch: " + row["new"])
    seal = E / "current_files.json"
    if not seal.is_file():
        failures.append("current source seal not created yet")
    else:
        for row in json.loads(seal.read_text()):
            path = R / row["path"]
            expected = current_expected(row["path"], row["sha256"])
            if not path.is_file() or sha(path) != expected:
                failures.append("current file hash mismatch: " + row["path"])
    for change in changes.values():
        if not (R / change["backup"]).is_file() or sha(R / change["backup"]) != change["before"]:
            failures.append("original edit backup corrupt: " + change["path"])
    if seal.is_file():
        sealed_paths = {row["path"] for row in json.loads(seal.read_text())} | set(new_files)
        for p in (R / "dogfight_rl").rglob("*"):
            rel = p.relative_to(R / "dogfight_rl")
            if p.is_file() and not any(part in (".git", "__pycache__", ".pytest_cache", "runs") for part in rel.parts):
                if str(p.relative_to(R)) not in sealed_paths:
                    failures.append("unsealed current project file: " + str(rel))
    hardlinks = [str(p.relative_to(R)) for base in [R / "dogfight_rl/src", R / "dogfight_rl/scripts"]
                 for p in base.rglob("*") if p.is_file() and p.stat().st_nlink > 1]
    if hardlinks:
        failures.append("hard-linked maintained source: " + repr(hardlinks))
    links = [str(p.relative_to(R)) for p in R.rglob("*") if p.is_symlink()]
    if links:
        failures.append("unexpected symbolic links: " + repr(links))
    mesh_references = 0
    for path in (R / "model").glob("*.urdf"):
        for mesh in ET.parse(path).getroot().iter("mesh"):
            uri = mesh.attrib["filename"]
            target = R / "model" / uri.removeprefix("package://csdog_urdf/") if uri.startswith("package://") else path.parent / uri
            mesh_references += 1
            if not target.is_file():
                failures.append("mesh missing: " + str(target))
    return dict(status="FAIL" if failures else "PASS", baseline_files=len(manifest["files"]),
        documented_edits=len(changes), new_task_amendments=len(amendments), new_task_files=len(new_files), model_mesh_references=mesh_references, symbolic_links=len(links), hardlinked_current_sources=len(hardlinks),
        historical_migration_validation="RETIRED: path_migration/20261025 was intentionally removed; not required by current check",
        failures=failures)
if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(result["status"] != "PASS")
