---
license: cc-by-4.0
language:
  - it
  - en
task_categories:
  - automatic-speech-recognition
pretty_name: Moth Italian–English Code-Switching Speech
size_categories:
  - n<1K
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/train-*.parquet
      - split: test
        path: data/test-*.parquet
      - split: anchor
        path: data/anchor-*.parquet
---

# Moth — Italian–English code-switching speech dataset

Scripted Italian speech with English words and phrases mixed in, recorded by three
speakers for the [Moth](https://huggingface.co/semantique-team/moth-stt) speech
recognizer. The dataset is small and deliberately narrow: **2,193 utterances,
1.46 hours, 3 speakers, read speech**. It is a benchmark and a fine-tuning seed,
not a general-purpose code-switching corpus.

| Split | Content | Clips | Minutes | Speakers |
|---|---|---|---:|---|
| `train` | R-S1 + R-S2 | 1,413 | 57.6 | S1 (741), S2 (672) |
| `test` | T | 600 | 23.2 | S1, S2, S3 (200 each) |
| `anchor` | A | 180 | 7.0 | S1, S2, S3 (60 each) |
| **Total** | | **2,193** | **87.8** | **3** |

`anchor` contains the same 60 T sentences read by every speaker; it separates the
speaker effect from the sentence effect. `train` and `test` have **no normalised
text overlap**. S3 never contributes to `train`.

## Quick start

```python
from datasets import load_dataset

ds = load_dataset("semantique-team/moth-cs", revision="v1.0.0")
print(ds)
print(ds["test"][0])
```

Offline, from this checkout:

```bash
python scripts/verify.py
python - <<'PY'
import json
rows = [json.loads(line) for line in open("manifests/test.jsonl")]
print(rows[0]["audio"], rows[0]["text"])
PY
```

Each row has `uid`, `id`, `set`, `split`, `speaker`, `audio`, `bytes`,
`audio_sha256`, `duration`, `sample_rate`, `channels`, `bits_per_sample`,
`text`, `norm`, `lang`, `category`, `en_spans` and `source`.

- `text` is the verbatim transcript after the project's normalisation: lowercase,
  no punctuation or digits, apostrophes only for elision.
- `norm` is the comparison form used by the Moth scorer (identical to `text` for
  these rows).
- `en_spans` are `[start, end)` word index ranges for English-origin words.
- `category` is one of `single_word`, `phrase`, `brand`, `acronym`,
  `italianized`, `switch`, `control_it`, `control_en`.
- Audio is 48 kHz, mono, 16-bit PCM WAV. Resample to 16 kHz for most ASR models.

## Files

```
audio/                 # canonical tree: T/<speaker>, R-S1/S1, R-S2/S2, anchor/<speaker>
manifests/
  train.jsonl          # R-S1 + R-S2
  test.jsonl           # T
  anchor.jsonl         # A
  all.jsonl            # all 2,193 rows
  excluded.jsonl       # 16 files deliberately not published, with reasons
  stats.json           # counts, hours, source commit
scripts/
  build_canonical.py   # migration from the legacy moth-stt manifests
  verify.py            # stdlib-only integrity check
  export_hf.py         # build the Hugging Face parquet files
  record.py            # macOS recorder used for the sessions
  build_manifest.py    # legacy manifest builder
  generate_scripts.py  # sentence-script import/dedupe/quota tool
text/                  # the sentence scripts (T, A, R-S1, R-S2, pool)
metadata/session-logs/ # recorder logs (timestamps, ids, durations)
docs/                  # protocol, consent summary, recording guide
releases/v1.0.0.json   # counts, hashes, provenance, licence and consent record
```

## Licence

- **Audio and transcripts:** [CC BY 4.0](LICENSE-CC-BY-4.0.txt).
- **Code:** Apache-2.0 (derived from `semantique-team/moth-stt`); see `NOTICE`.
- **Ethical request:** the speakers asked that their voices not be used to train
  synthetic voices (TTS/voice cloning) or biometric identification systems.
  CC BY 4.0 does not encode that restriction; please respect it. See
  `docs/consent.md`.

## Consent and privacy

All three speakers chose **Option A (CC BY 4.0)**. Signed forms are held offline
by the organiser and are not part of this repository. Only the technical speaker
ids `S1`, `S2`, `S3` are published; no names, ages or contact details are
included. Voice is personal data: do not attempt to re-identify the speakers.

## Known limitations

- Three speakers, all Italian L1, recorded in quiet rooms; no spontaneous
  code-switching and no telephone/noisy channel.
- S1 has rhotacism (a non-standard /r/); this is documented in the data card
  because it affects the per-speaker error profile.
- S3 is held out from training but informed development, so it is not a pristine
  unseen speaker.
- Recording devices were not logged for every session, and the S2 session logs
  are missing (T, R-S2, anchor); see `DATA_CARD.md`.
- The sentence scripts were generated with LLM assistance and human-reviewed;
  the manifests contain no generator metadata per row.
- One S2 file (`S2_0624.wav`) had ffmpeg streaming sizes in its WAV header. The
  header was repaired without touching the samples; the original SHA-256 is in
  `releases/v1.0.0.json`.

## Citation

See `CITATION.cff`. A Zenodo DOI will be added when the archive is deposited.
The companion model and paper are at
[`semantique-team/moth-stt`](https://huggingface.co/semantique-team/moth-stt).

## Provenance

Built from `semantique-team/moth-stt` at commit
`f3ecd1b0f4f0c5c044fa637e5fb5dd8a0c798d97` (2026-11-15). The model release is
0.8.1. The dataset was assembled on 2026-11-16; the audio is the 48 kHz master,
not a resampled derivative.
