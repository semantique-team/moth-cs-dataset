# Recording and annotation protocol

This is the protocol used for v1.0.0. It is kept here so the data can be
extended without re-deriving the rules, and so the splits remain comparable.

## Design

| Set | Script | Who reads | Use |
|---|---|---|---|
| **T** | 600 unique sentences, 200 per speaker | S1, S2, S3 | Test only |
| **R-S1** / **R-S2** | 600–1,000 sentences, disjoint from T | S1, S2 | Training |
| **A** | 60 sentences from T | every speaker | Speaker-vs-sentence control |

- T and R are disjoint; the importer refuses exact and near-duplicates (word
  3-gram Jaccard > 0.8) across all scripts.
- A deliberately reuses T sentences. It is **not** an independent dev set.
- S3 is held out from training and must never receive an R script.

## Sentence format

One JSON object per line:

```json
{"text": "ho spostato il meeting a domani", "category": "single_word",
 "en_spans": [[3, 4]], "generator": "<model>", "date": "YYYY-MM-DD"}
```

- `text` is already normalised: lowercase, no punctuation or digits,
  apostrophes only for elision; English words in standard spelling;
  Italianised forms as Italians write them.
- `category` is one of `single_word`, `phrase`, `brand`, `acronym`,
  `italianized`, `switch`, `control_it`, `control_en`.
- `en_spans` are `[start, end)` word index ranges for English-origin words.

The full generation prompt and quotas are in the model repository's
`recordings/README.md` and in `scripts/generate_scripts.py`. The published scripts are in
`text/`; do not edit them in place for a new version.

## Recording

- Quiet room, one speaker at a time, one sentence per file.
- 48 kHz mono WAV, 16-bit; light silence trim only; no denoising or loudness
  normalisation.
- Natural conversational speed; English words pronounced as in conversation.
  Retakes only for flubs; log retakes and skips.
- File names `<speaker>_<NNNN>.wav`.
- Target level around −12/−6 dBFS; no clipping.

On macOS the recorder is `scripts/record.py` (requires `ffmpeg`):

```bash
# T for a new speaker: audio/T/<speaker>/
uv run --no-project --with numpy --with soundfile --with num2words \
    python -m scripts.record --speaker S3 --kind T --dry-run

# A: audio/anchor/<speaker>/
python -m scripts.record --speaker S3 --kind A
```

The recorder writes a `session.log.jsonl` next to the audio. Keep it: it is the
retake/skip record.

## Building a manifest

The v1.0.0 manifests were produced by `scripts/build_canonical.py` from the
legacy `moth-stt` manifests. For a new session, `scripts/build_manifest.py`
validates the audio against the script and writes a manifest fragment with
canonical paths:

```bash
uv run --no-project --with numpy --with soundfile --with num2words \
    python -m scripts.build_manifest build --kind T --speaker S3 \
    --scripts-dir text --audio-dir audio/T --out manifests/T-S3.jsonl
```

Then merge the fragment into the canonical split and rerun `verify.py`. Do not
overwrite `manifests/train.jsonl`, `test.jsonl` or `anchor.jsonl` in place for a
new release: create a new version and keep v1.0.0 reproducible.

## Validation

```bash
python scripts/verify.py
```

The check is stdlib-only and fails on a missing file, a hash mismatch, a wrong
duration, a non-48 kHz/mono/16-bit WAV, an unreferenced WAV, a train/test text
overlap or an invalid `en_spans`.

## Extending the dataset

1. Choose a new technical id (for example `S5`); add it to `T_SPEAKERS` in
   `scripts/generate_scripts.py`.
2. Generate and human-review the T/A scripts **before** recording.
3. Record; keep the session logs.
4. Build the fragment, merge, run `verify.py`, bump the version in
   `releases/` and publish a new dataset revision.
5. Never add a new speaker to an existing published version: fingerprints and
   hashes would change and comparisons would break.
