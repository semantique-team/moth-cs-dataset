#!/usr/bin/env python3
"""Build the canonical manifests for the Moth code-switching dataset.

The legacy manifests in ``moth-stt/recordings/manifests`` encode ``audio`` as
``<speaker>/<file>.wav`` without the set root.  The same string therefore means
``audio/T/S1/S1_0001.wav`` in ``T.jsonl`` and ``audio/anchor/S1/S1_0001.wav`` in
``A-S1.jsonl``.  This script rewrites every row with an unambiguous path,
adds a stable ``uid`` and the audio metadata (SHA-256, sample rate, channels,
bit depth, measured duration) and writes one canonical file per split.

It is a one-off migration tool: it reads the legacy manifests from a checkout of
``moth-stt`` and the canonical audio tree of this repository.  Running it again
must produce byte-identical output.

Usage::

    python scripts/build_canonical.py --source-root ../moth-stt
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import wave
from collections import Counter, defaultdict
from pathlib import Path

SETS = {
    # name: (manifest files, source audio root, canonical audio prefix, split)
    "T": (("T.jsonl",), "recordings/audio", "T", "test"),
    "R-S1": (("R-S1.jsonl",), "recordings/audio/R-S1", "R-S1", "train"),
    "R-S2": (("R-S2.jsonl",), "recordings/audio/R-S2", "R-S2", "train"),
    "A": (
        ("A-S1.jsonl", "A-S2.jsonl", "A-S3.jsonl"),
        "recordings/audio/anchor",
        "anchor",
        "anchor",
    ),
}

EXPECTED = {"T": 600, "R-S1": 741, "R-S2": 672, "A": 180}

EXCLUDED = {
    "recordings/audio/S1_alt_2026-10-19T1724": (
        "superseded S1 retake session; the canonical T takes are under audio/T/S1"
    ),
    "recordings/audio/R-S2/S2/S2_0001.wav": (
        "unlabelled take; rejected at import and absent from R-S2.jsonl"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wave_info(path: Path) -> tuple[float, int, int, int]:
    with wave.open(str(path), "rb") as handle:
        frames = handle.getnframes()
        rate = handle.getframerate()
        channels = handle.getnchannels()
        width = handle.getsampwidth()
    return frames / rate, rate, channels, width * 8


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def canonical_row(source: dict, set_name: str, prefix: str, split: str, root: Path) -> dict:
    relative = f"audio/{prefix}/{source['audio']}"
    audio = root / relative
    if not audio.is_file():
        raise SystemExit(f"missing audio: {audio} (from {source['id']})")
    duration, rate, channels, bits = wave_info(audio)
    expected = float(source.get("duration") or 0.0)
    if expected and abs(duration - expected) > 0.1:
        raise SystemExit(
            f"duration mismatch for {source['id']}: manifest {expected:.3f}s, "
            f"wave {duration:.3f}s"
        )
    speaker = source.get("speaker")
    return {
        "uid": f"{set_name}:{speaker}:{source['id']}",
        "id": source["id"],
        "set": set_name,
        "split": split,
        "speaker": speaker,
        "audio": relative,
        "bytes": audio.stat().st_size,
        "audio_sha256": sha256(audio),
        "duration": round(duration, 3),
        "sample_rate": rate,
        "channels": channels,
        "bits_per_sample": bits,
        "text": source["text"],
        "norm": source["norm"],
        "lang": source.get("lang", "mix"),
        "category": source.get("category"),
        "en_spans": source.get("en_spans", []),
        "source": source.get("source"),
    }


def git_commit(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path("../moth-stt"))
    parser.add_argument("--dataset-root", type=Path, default=Path("."))
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    root = args.dataset_root.resolve()
    manifest_root = source_root / "recordings" / "manifests"

    rows: list[dict] = []
    by_set: dict[str, list[dict]] = defaultdict(list)
    for set_name, (files, _source_audio, prefix, split) in SETS.items():
        for name in files:
            for source in load_jsonl(manifest_root / name):
                row = canonical_row(source, set_name, prefix, split, root)
                rows.append(row)
                by_set[set_name].append(row)

    for set_name, expected in EXPECTED.items():
        actual = len(by_set[set_name])
        if actual != expected:
            raise SystemExit(f"{set_name}: expected {expected} rows, found {actual}")

    for field in ("uid", "audio"):
        values = Counter(row[field] for row in rows)
        duplicates = [value for value, count in values.items() if count > 1]
        if duplicates:
            raise SystemExit(f"duplicate {field}: {duplicates[:5]}")

    test_norm = {row["norm"] for row in by_set["T"]}
    train_norm = {row["norm"] for row in by_set["R-S1"] + by_set["R-S2"]}
    overlap = test_norm & train_norm
    if overlap:
        raise SystemExit(f"test/train text overlap: {sorted(overlap)[:5]}")

    manifest_dir = root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(manifest_dir / "train.jsonl", by_set["R-S1"] + by_set["R-S2"])
    write_jsonl(manifest_dir / "test.jsonl", by_set["T"])
    write_jsonl(manifest_dir / "anchor.jsonl", by_set["A"])
    write_jsonl(manifest_dir / "all.jsonl", rows)

    excluded = []
    for path, reason in EXCLUDED.items():
        full = source_root / path
        if not full.exists():
            continue
        files = [full] if full.is_file() else sorted(full.rglob("*.wav"))
        for file in files:
            excluded.append(
                {
                    "source": str(file.relative_to(source_root)),
                    "bytes": file.stat().st_size,
                    "reason": reason,
                }
            )
    write_jsonl(manifest_dir / "excluded.jsonl", excluded)

    speaker_seconds: Counter[str] = Counter()
    set_seconds: Counter[str] = Counter()
    for row in rows:
        speaker_seconds[row["speaker"]] += row["duration"]
        set_seconds[row["set"]] += row["duration"]

    stats = {
        "version": "1.0.0",
        "built_from_commit": git_commit(source_root),
        "sets": {
            name: {
                "clips": len(items),
                "speakers": sorted({row["speaker"] for row in items}),
                "seconds": round(set_seconds[name], 3),
                "hours": round(set_seconds[name] / 3600, 4),
            }
            for name, items in by_set.items()
        },
        "total": {
            "clips": len(rows),
            "seconds": round(sum(set_seconds.values()), 3),
            "hours": round(sum(set_seconds.values()) / 3600, 4),
        },
        "speakers": {
            speaker: {
                "clips": sum(1 for row in rows if row["speaker"] == speaker),
                "seconds": round(seconds, 3),
                "hours": round(seconds / 3600, 4),
            }
            for speaker, seconds in sorted(speaker_seconds.items())
        },
        "excluded_files": len(excluded),
    }
    (manifest_dir / "stats.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(json.dumps(stats, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
