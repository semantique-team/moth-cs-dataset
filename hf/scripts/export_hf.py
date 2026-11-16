#!/usr/bin/env python3
"""Build the Hugging Face dataset files under ``hf/``.

The parquet files embed the 48 kHz WAV audio, so a download of
``hf/data/*.parquet`` is self-contained. The README in ``hf/`` is the dataset
card; ``hf/manifests`` and ``hf/SHA256SUMS`` are the provenance copy.

Run with the optional dependencies::

    uv run --no-project --with datasets --with soundfile --with pyarrow \
        python scripts/export_hf.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from datasets import Audio, Dataset, Features, Sequence, Value

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "hf"
SPLITS = {"train": "train.jsonl", "test": "test.jsonl", "anchor": "anchor.jsonl"}

FEATURES = Features(
    {
        "uid": Value("string"),
        "id": Value("string"),
        "set": Value("string"),
        "split": Value("string"),
        "speaker": Value("string"),
        "audio": Audio(sampling_rate=48000),
        "bytes": Value("int64"),
        "audio_sha256": Value("string"),
        "duration": Value("float32"),
        "sample_rate": Value("int32"),
        "channels": Value("int16"),
        "bits_per_sample": Value("int16"),
        "text": Value("string"),
        "norm": Value("string"),
        "lang": Value("string"),
        "category": Value("string"),
        "en_spans": Sequence(Sequence(Value("int32"))),
        "source": Value("string"),
    }
)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> int:
    data_dir = OUT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for split, name in SPLITS.items():
        rows = load_jsonl(ROOT / "manifests" / name)
        for row in rows:
            path = ROOT / row["audio"]
            row["audio"] = {"bytes": path.read_bytes(), "path": None}
        dataset = Dataset.from_list(rows, features=FEATURES)
        path = data_dir / f"{split}-00000-of-00001.parquet"
        dataset.to_parquet(str(path))
        print(f"{split:6} {len(dataset):5d} rows  {path.stat().st_size / 1e6:7.1f} MB")

    for name in (
        "README.md",
        "DATA_CARD.md",
        "NOTICE",
        "CITATION.cff",
        "LICENSE-CC-BY-4.0.txt",
        "LICENSE-APACHE-2.0",
        "SHA256SUMS",
    ):
        shutil.copy2(ROOT / name, OUT / name)
    for directory in ("manifests", "text", "scripts", "docs", "releases"):
        shutil.copytree(
            ROOT / directory,
            OUT / directory,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
