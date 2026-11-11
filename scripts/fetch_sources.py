"""Copy the pinned source files from the Paper 1 checklist repository into data/raw/.

The commit is pinned in config/sources.json so every build uses the same checklist.
Change the commit there when the checklist is updated, then rerun this script.
"""
import json, pathlib, subprocess, shutil, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT / "config/sources.json").read_text())
raw = ROOT / "data/raw"
raw.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(["git", "init", "-q", tmp], check=True)
    subprocess.run(["git", "-C", tmp, "fetch", "-q", "--depth", "1", cfg["checklist_repo"], cfg["checklist_commit"]], check=True)
    subprocess.run(["git", "-C", tmp, "checkout", "-q", "FETCH_HEAD"], check=True)
    for key, rel in cfg["files"].items():
        shutil.copy(pathlib.Path(tmp) / rel, raw / pathlib.Path(rel).name)
        print("copied", rel)
(raw / "SOURCE_COMMIT.txt").write_text(cfg["checklist_commit"] + "\n")
