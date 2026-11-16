#!/usr/bin/env python3
"""Verify the Moth code-switching dataset without third-party dependencies.

Checks, in order:

* manifest counts and the per-set/per-speaker breakdown;
* unique ``uid`` and ``audio`` values;
* every referenced WAV exists, is 48 kHz mono 16-bit, matches its duration
  (within 100 ms) and its SHA-256;
* no unreferenced WAV is left under ``audio/``;
* no normalised text overlap between the train and test sets;
* every anchor sentence also appears in the test set;
* ``en_spans`` are valid word index ranges.

Exit code 0 means the dataset is internally consistent.
"""

from __future__ import annotations

import hashlib
import json
import sys
import wave
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    "train": {"clips": 1413, "speakers": {"S1": 741, "S2": 672}},
    "test": {"clips": 600, "speakers": {"S1": 200, "S2": 200, "S3": 200}},
    "anchor": {"clips": 180, "speakers": {"S1": 60, "S2": 60, "S3": 60}},
}
TOTAL = 2193
DURATION_TOLERANCE = 0.1

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load(name: str) -> list[dict]:
    path = ROOT / "manifests" / name
    rows = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                fail(f"{name}:{number}: invalid JSON: {exc}")
    return rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_rows(split: str, rows: list[dict]) -> None:
    expected = EXPECTED[split]
    if len(rows) != expected["clips"]:
        fail(f"{split}: expected {expected['clips']} rows, found {len(rows)}")
    speakers = Counter(row.get("speaker") for row in rows)
    for speaker, count in expected["speakers"].items():
        if speakers.get(speaker) != count:
            fail(f"{split}: expected {count} rows for {speaker}, found {speakers.get(speaker, 0)}")
    unexpected = set(speakers) - set(expected["speakers"])
    if unexpected:
        fail(f"{split}: unexpected speakers {sorted(unexpected)}")
    if any(row.get("split") != split for row in rows):
        fail(f"{split}: rows with a different split value")


def main() -> int:
    train = load("train.jsonl")
    test = load("test.jsonl")
    anchor = load("anchor.jsonl")
    all_rows = load("all.jsonl")
    excluded = load("excluded.jsonl")

    for split, rows in (("train", train), ("test", test), ("anchor", anchor)):
        check_rows(split, rows)

    if len(all_rows) != TOTAL:
        fail(f"all.jsonl: expected {TOTAL} rows, found {len(all_rows)}")
    if len(all_rows) != len(train) + len(test) + len(anchor):
        fail("all.jsonl does not equal train + test + anchor")

    seen_uid = Counter(row.get("uid") for row in all_rows)
    seen_audio = Counter(row.get("audio") for row in all_rows)
    for field, counter in (("uid", seen_uid), ("audio", seen_audio)):
        duplicates = sorted(value for value, count in counter.items() if count > 1)
        if duplicates:
            fail(f"duplicate {field}: {duplicates[:5]}")

    referenced = set()
    for row in all_rows:
        uid = row.get("uid", "?")
        relative = row.get("audio")
        if not relative:
            fail(f"{uid}: missing audio path")
            continue
        referenced.add(relative)
        path = ROOT / relative
        if not path.is_file():
            fail(f"{uid}: missing file {relative}")
            continue
        if path.stat().st_size != row.get("bytes", path.stat().st_size):
            fail(f"{uid}: byte size differs from the manifest")
        if row.get("audio_sha256") != sha256(path):
            fail(f"{uid}: SHA-256 mismatch")
        try:
            with wave.open(str(path), "rb") as handle:
                rate = handle.getframerate()
                channels = handle.getnchannels()
                width = handle.getsampwidth()
                duration = handle.getnframes() / rate
        except wave.Error as exc:
            fail(f"{uid}: not a readable WAV: {exc}")
            continue
        if rate != 48000 or channels != 1 or width != 2:
            fail(f"{uid}: expected 48 kHz mono 16-bit, found {rate} Hz/{channels} ch/{width * 8} bit")
        if abs(duration - float(row.get("duration", 0))) > DURATION_TOLERANCE:
            fail(f"{uid}: duration {duration:.3f}s vs manifest {row.get('duration')}s")
        if int(row.get("sample_rate", 0)) != rate:
            fail(f"{uid}: sample_rate field mismatch")
        if int(row.get("channels", 0)) != channels:
            fail(f"{uid}: channels field mismatch")
        if int(row.get("bits_per_sample", 0)) != width * 8:
            fail(f"{uid}: bits_per_sample field mismatch")
        words = row.get("text", "").split()
        for span in row.get("en_spans", []):
            if (
                not isinstance(span, list)
                or len(span) != 2
                or not all(isinstance(index, int) for index in span)
                or not (0 <= span[0] < span[1] <= len(words))
            ):
                fail(f"{uid}: invalid en_span {span!r} for {len(words)} words")

    on_disk = {
        str(path.relative_to(ROOT)) for path in (ROOT / "audio").rglob("*.wav")
    }
    unreferenced = sorted(on_disk - referenced)
    if unreferenced:
        fail(f"{len(unreferenced)} unreferenced WAV files, first: {unreferenced[:5]}")

    train_norm = {row["norm"] for row in train}
    test_norm = {row["norm"] for row in test}
    if train_norm & test_norm:
        fail(f"train/test text overlap: {sorted(train_norm & test_norm)[:5]}")
    if len(train_norm) != len(train):
        fail("duplicate normalised text inside train")
    if len(test_norm) != len(test):
        fail("duplicate normalised text inside test")
    missing_anchor = sorted({row["norm"] for row in anchor} - test_norm)
    if missing_anchor:
        fail(f"anchor sentences missing from test: {missing_anchor[:5]}")

    for split, rows in (("train", train), ("test", test), ("anchor", anchor)):
        seconds = sum(float(row["duration"]) for row in rows)
        print(f"{split:6} {len(rows):5d} clips  {seconds / 60:7.1f} min")
    print(f"excluded {len(excluded):4d} files (documented in manifests/excluded.jsonl)")
    print(f"total    {len(all_rows):5d} clips  {sum(float(r['duration']) for r in all_rows) / 60:7.1f} min")

    if errors:
        print(f"\nFAILED with {len(errors)} error(s):", file=sys.stderr)
        for message in errors[:40]:
            print(f"  - {message}", file=sys.stderr)
        return 1
    print("\nOK: manifests, audio, hashes, durations and splits are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
