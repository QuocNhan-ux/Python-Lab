import tempfile
import unittest
from pathlib import Path

from integrity import compare, hash_file, scan


class IntegrityTests(unittest.TestCase):
    def test_known_sha256(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "hello"
            path.write_bytes(b"abc")
            self.assertEqual(hash_file(path),
                             "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_detects_changes_and_excludes_baseline(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            baseline = root / "baseline.json"
            baseline.write_text("{}")
            (root / "edit.txt").write_text("before")
            (root / "remove.txt").write_text("goodbye")
            before = scan(root, baseline)
            self.assertNotIn("baseline.json", before)
            (root / "edit.txt").write_text("after")
            (root / "remove.txt").unlink()
            (root / "new.txt").write_text("hello")
            self.assertEqual(compare(before, scan(root, baseline)), {
                "added": ["new.txt"], "removed": ["remove.txt"],
                "modified": ["edit.txt"],
            })


if __name__ == "__main__":
    unittest.main()
