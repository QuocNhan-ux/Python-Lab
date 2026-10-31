#!/usr/bin/env python3
"""An offline file-integrity lab. Python 3.10+, standard library only."""

import argparse
import hashlib
import json
from pathlib import Path


def hash_file(path: Path) -> str:
    """Hash in chunks so memory use does not grow with file size."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan(root: Path, baseline: Path) -> dict[str, str]:
    """Map relative filenames to hashes; skip symlinks and the baseline."""
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    results = {}
    # Path.rglob does not recurse into directory symlinks by default.
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or path.resolve() == baseline:
            continue
        if path.is_file():
            results[path.relative_to(root).as_posix()] = hash_file(path)
    return results


def compare(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    """Dictionary keys behave like sets when comparing filenames."""
    return {
        "added": sorted(after.keys() - before.keys()),
        "removed": sorted(before.keys() - after.keys()),
        "modified": sorted(
            name for name in before.keys() & after.keys()
            if before[name] != after[name]
        ),
    }


def load_baseline(path: Path, root: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("Unsupported baseline format")
    if data.get("root") != str(root):
        raise ValueError("Baseline belongs to a different directory")
    files = data.get("files")
    if not isinstance(files, dict) or not all(
        isinstance(k, str) and isinstance(v, str)
        and len(v) == 64 and all(c in "0123456789abcdef" for c in v)
        for k, v in files.items()
    ):
        raise ValueError("Invalid baseline hashes")
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "check"])
    parser.add_argument("directory", type=Path)
    parser.add_argument("--baseline", type=Path, default=Path("baseline.json"))
    args = parser.parse_args()
    root = args.directory.resolve()
    baseline = args.baseline.resolve()
    try:
        if args.command == "init":
            data = {"version": 1, "root": str(root), "files": scan(root, baseline)}
            # Exclusive creation prevents accidentally replacing a trusted baseline.
            with baseline.open("x", encoding="utf-8") as stream:
                json.dump(data, stream, indent=2, sort_keys=True)
                stream.write("\n")
            print(f"Saved {len(data['files'])} file hashes to {baseline}")
            return 0
        before = load_baseline(baseline, root)
        changes = compare(before, scan(root, baseline))
        for category, names in changes.items():
            for name in names:
                # JSON quoting keeps unusual filenames from injecting terminal escapes.
                print(f"{category.upper():8} {json.dumps(name)}")
        if any(changes.values()):
            return 1
        print("No content changes detected.")
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
