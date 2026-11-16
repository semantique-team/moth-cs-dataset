#!/usr/bin/env python3
"""Write releases/v1.0.0.json from the manifests and the checksum file.

Run after ``scripts/build_canonical.py`` and after ``SHA256SUMS`` has been
generated. The record is descriptive: publishing to Hugging Face or Zenodo is a
separate, explicit step.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = "1.0.0"
SOURCE_COMMIT = "f3ecd1b0f4f0c5c044fa637e5fb5dd8a0c798d97"
MANIFESTS = ("train.jsonl", "test.jsonl", "anchor.jsonl", "all.jsonl", "excluded.jsonl", "stats.json")
PUBLISHED = {
    "at": "2026-11-16",
    "hf_url": "https://huggingface.co/datasets/semantique-team/moth-cs",
    "hf_revision": "v1.0.0",
    "hf_data_commit": "1d8865b384f9bb4b40b2809beb78a046890ef673",
    "visibility": "public",
}

HEADER_FIX = {
    "file": "audio/R-S2/S2/S2_0624.wav",
    "issue": "RIFF and data chunk sizes were 0xFFFFFFFF (ffmpeg streaming header)",
    "original_sha256": "d747fd0d5ce62dfe9b06ed72bb59d1f8b98ee0351f00ae8cb26c056f86a98ce8",
    "repaired_sha256": "811cc8e142b6a931f2a500fcaa94c1a6a963109d260d50469e89db5147339d58",
    "samples_touched": False,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    stats = json.loads((ROOT / "manifests" / "stats.json").read_text(encoding="utf-8"))
    manifest_hashes = {
        name: sha256(ROOT / "manifests" / name) for name in MANIFESTS
    }
    checksum_path = ROOT / "SHA256SUMS"
    if not checksum_path.is_file():
        raise SystemExit("run the SHA256SUMS generation before record_release.py")
    audio_files = list((ROOT / "audio").rglob("*.wav"))
    record = {
        "version": VERSION,
        "date": date.today().isoformat(),
        "status": "published" if PUBLISHED else "prepared; not uploaded",
        "published": PUBLISHED,
        "source_repo": "semantique-team/moth-stt",
        "source_commit": SOURCE_COMMIT,
        "model_release": "0.8.1",
        "hf_repo": "semantique-team/moth-cs",
        "github_repo": "semantique-team/moth-cs-dataset",
        "zenodo_doi": None,
        "license": {
            "audio": "CC-BY-4.0",
            "transcripts": "CC-BY-4.0",
            "code": "Apache-2.0",
        },
        "consent": {
            "option": "A (CC-BY-4.0)",
            "speakers": ["S1", "S2", "S3"],
            "confirmed": "2026-11-16",
            "signed_forms": "offline, not in the repository",
        },
        "counts": stats,
        "audio_files": len(audio_files),
        "audio_bytes": sum(path.stat().st_size for path in audio_files),
        "hf_parquet_files": len(list((ROOT / "hf" / "data").glob("*.parquet"))),
        "hf_parquet_bytes": sum(
            path.stat().st_size for path in (ROOT / "hf" / "data").glob("*.parquet")
        ),
        "manifests_sha256": manifest_hashes,
        "sha256sums_sha256": sha256(checksum_path),
        "header_fix": HEADER_FIX,
        "notes": [
            "16 files excluded and documented in manifests/excluded.jsonl.",
            "S3 never contributes to train; S3 informed development and is not a pristine holdout.",
            "Devices were not logged for every session; do not infer them.",
            "No S2 session log is present (T, R-S2, anchor); the addendum builder report is the only S2 record.",
            "CC-BY-4.0 does not encode the speakers' no-TTS request; see docs/consent.md.",
        ],
    }
    out = ROOT / "releases" / f"v{VERSION}.json"
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
