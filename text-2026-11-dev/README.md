# S1-dev script set (2026-11-17)

`R-S1.jsonl` contains **900 sentences** selected deterministically from
`../text/pool.jsonl` (seed `20261117`):

- balanced across the eight categories: 113 each for acronym, brand,
  control_en, control_it; 112 each for italianized, phrase, single_word,
  switch;
- **unreviewed** (`reviewed: false`): a human must read them before recording;
- no exact or near-duplicate overlap with T, A, R-S1 or R-S2 (the whole pool was
  checked against those scripts; 0 exact, 0 near-duplicate);
- mean 5.63 words, max 9 words, estimated **30 min** at 2.8 words/s. With
  retakes and pauses expect 35–45 min.

900 was chosen instead of 600 because the pool sentences are short: 600 would
be only ~20 min, below the protocol's 30–60 min dev window. If a full 45–60 min
session is wanted, select another 450–900 sentences from the remaining pool
without reusing these IDs.

## Review

```bash
cd ../moth-cs-dataset
python -m scripts.generate_scripts review --kind R --speaker S1 \
  --scripts-dir text-2026-11-dev
python -m scripts.generate_scripts mark-reviewed --kind R --speaker S1 \
  --scripts-dir text-2026-11-dev --reviewer <name>
```

## Record

```bash
uv run --no-project --with numpy --with soundfile --with num2words \
  python -m scripts.record --speaker S1 --kind R \
  --scripts-dir text-2026-11-dev --audio-dir audio/R-S1-dev --dry-run

uv run --no-project --with numpy --with soundfile --with num2words \
  python -m scripts.record --speaker S1 --kind R \
  --scripts-dir text-2026-11-dev --audio-dir audio/R-S1-dev
```

Then build the dev manifest and patch it as described in
`moth-50/experiments/E-002-s1-dev.md`.

**Do not** run `scripts/verify.py` on the v1.0.0 checkout with this new audio:
it checks the fixed v1.0.0 counts. Use it only after creating a new dataset
version.
