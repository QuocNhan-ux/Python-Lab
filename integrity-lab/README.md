# Python + Cybersecurity: File Integrity Lab

**Time:** 45–60 minutes. **Prerequisites:** C/C++ knowledge, Python 3.10 or later.
No packages, accounts, administrator permissions, or network access needed.

Build an offline tool that records SHA-256 hashes of files, then detects added,
removed, and modified files. This is a small version of a technique used to
monitor configuration files and investigate unexpected changes.

The included implementation works immediately. Learn by running it, reading its
four small functions, and completing the exercises below.

## 1. Run the experiment (10 minutes)

Open a terminal in this project folder. On systems where Python is named
`python` or `py`, substitute that for `python3` below.

```sh
python3 --version
python3 integrity.py init sample_files
python3 integrity.py check sample_files
```

The first command creates `baseline.json`; the check prints
`No content changes detected.`

Now use your text editor to:

1. Change `role = reader` to `role = admin` in `sample_files/settings.ini`.
2. Create `sample_files/new.txt` with any text.
3. Delete `sample_files/notes.txt` (it is only sample data).

```sh
python3 integrity.py check sample_files
```

Expected output:

```text
ADDED    "new.txt"
REMOVED  "notes.txt"
MODIFIED "settings.ini"
```

Exit codes: `0` = success/no changes, `1` = changes detected, `2` = error.
An existing baseline cannot be overwritten by `init`. To repeat the lab, restore
the sample files and explicitly delete your generated `baseline.json` first.
You can keep separate baselines with `--baseline another-baseline.json`.

## 2. Read the code like a C++ developer (10 minutes)

Read in this order: `hash_file`, `scan`, `compare`, `main`.

| Python feature | Connection to C/C++ |
| --- | --- |
| `dict[str, str]` | Similar purpose to `std::unordered_map<string, string>`; this is a type hint, not runtime enforcement. |
| `with path.open(...)` | Deterministic cleanup like an RAII file wrapper, even if an exception occurs. |
| `bytes` vs `str` | Raw bytes vs Unicode text. Hash bytes so encoding/newline conversion does not alter the input. |
| `for chunk in iter(..., b"")` | Repeatedly read until an empty byte string signals EOF. The lambda supplies the read operation. |
| `before.keys() & after.keys()` | Set intersection; find filenames present in both snapshots. |
| List comprehensions | A compact loop that constructs a list. |
| `Path` and `/` | Portable path handling; `/` joins paths through operator overloading. |
| `raise` / `except` | Exceptions; the CLI turns expected failures into an error message and exit status. |
| `if __name__ == "__main__"` | Runs the CLI only when executed directly, so tests can import functions. |

Questions to answer before editing:

1. Why hash in 64 KiB chunks instead of reading the entire file?
2. Why store relative names, but bind the baseline to an absolute root?
3. What happens when a file is renamed without changing its contents?
4. Why exclude the baseline itself from scanning?

Answers: bounded memory; portable names within a specific directory;
a removal plus an addition; otherwise updating the baseline would change a
monitored file and invalidate its own hash.

## 3. Extend it yourself (20–30 minutes)

Complete these in order. The shipped code is your reference implementation.

### Exercise A — Friendly summary

After the per-file output, print counts such as
`1 added, 1 removed, 1 modified`. Use `len()` and an f-string.
Verify both an unchanged directory and the three-change experiment above.

### Exercise B — Ignore temporary files

Add a repeatable `--ignore` option using `argparse`'s `action="append"` and
`fnmatch.fnmatchcase()`. Match patterns against each relative POSIX filename.
For example, `--ignore '*.tmp'` should skip temporary files. Apply the same
patterns during baseline creation and checking. Save the patterns in the
baseline and reject a check with different patterns; otherwise a changed
configuration could hide files that were previously monitored.

Acceptance check: ignore `scratch.tmp`, then change both that file and
`settings.ini`. Only `settings.ini` should be reported.

### Exercise C — Machine-readable reports

Add a `--json` flag for checks. Output the `changes` dictionary using
`json.dumps()`, preserve the existing exit codes, and avoid mixing human-readable
status lines into the JSON output. Practice parsing that report from another
Python program using `json.loads()`.

## 4. Verify the implementation

```sh
python3 -m unittest -v
```

The included tests check a known SHA-256 result, all three change categories,
and exclusion of the baseline. Add behavior-focused tests for your exercises.
Tests use temporary directories, so they do not modify the sample files.

## Security lessons and limits

- A hash detects changed bytes. It does not explain intent or prove malware.
- The baseline must come from a trusted starting state. An attacker who can
  rewrite both the files and baseline can hide changes. Keep a protected copy;
  a hash alone provides no authentication.
- This lab compares file contents and names. It does not monitor permissions,
  ownership, timestamps, or changes that happen and are reverted between scans.
- It skips symbolic links and does not follow directory links. It is intended
  for a quiet local practice directory, not hostile filesystems: concurrent
  changes can race with scanning, and the scan is not an atomic snapshot.
- Scanning can read private files, and the baseline records filenames and hashes.
  Start with the supplied sample directory and keep baselines private.

Next step: learn HMAC and add authenticated baselines, considering separately
where to store the secret key. That makes a useful second project.
