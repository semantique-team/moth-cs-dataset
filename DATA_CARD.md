# Data card — Moth code-switching recordings

Version 1.0.0 · 2026-11-16 · companion to the
[Moth model](https://huggingface.co/semantique-team/moth-stt) and paper.

## 1. Summary

| Field | Value |
|---|---|
| Content | Read Italian sentences with English words and phrases (code-switching IT+EN) |
| Speakers | S1 (the author), S2, S3 |
| Utterances | 2,193 |
| Duration | 87.8 min (1.46 h) |
| Audio | 48 kHz, mono, 16-bit PCM WAV |
| Transcripts | Normalised text, English word spans, category |
| Splits | `train` 1,413 / `test` 600 / `anchor` 180 |
| Language | Italian with English-origin terms; `lang` is `mix` for every row |
| Licence | CC BY 4.0 (audio and transcripts) |
| Consent | Option A (CC BY 4.0), all three speakers |
| Source commit | `semantique-team/moth-stt@f3ecd1b` |

The dataset was recorded for a 20 MB browser speech recogniser, not as a
general-purpose corpus. Its value is the **code-switching annotation** (English
spans and category) and the **controlled test/anchor design**, not scale.

## 2. Sets

| Set | Script | Who reads | Use | Clips | Minutes |
|---|---|---|---|---:|---:|
| **T** | 600 unique sentences (200 per speaker) | S1, S2, S3 | Test only | 600 | 23.2 |
| **R-S1** | 741 sentences (641 base + 50 term addendum v1 + 50 v3) | S1 | Training | 741 | 34.9 |
| **R-S2** | 672 sentences (622 base + 50 term addendum) | S2 | Training | 672 | 22.7 |
| **A** | 60 sentences from T, read by every speaker | S1, S2, S3 | Speaker-vs-sentence control | 180 | 7.0 |

`T` and `R` are disjoint by design; `verify.py` checks that no normalised text
is shared. `A` deliberately reuses 60 T sentences, so it overlaps `test` by
construction; it is not an independent dev set.

### Per-speaker totals

| Speaker | T | R | A | Total | Minutes |
|---|---:|---:|---:|---:|---:|
| S1 | 200 | 741 | 60 | 1,001 | 45.5 |
| S2 | 200 | 672 | 60 | 932 | 32.5 |
| S3 | 200 | 0 | 60 | 260 | 9.8 |

S3 never contributes to training. S3 did inform development through repeated
evaluation, so it is **not** a pristine unseen speaker. There is no
speaker-disjoint test set in this release.

## 3. Recording protocol

- Quiet room; one speaker at a time; one sentence per file.
- Native 48 kHz mono WAV, 16-bit; light silence trim only, no denoising,
  loudness normalisation or compression.
- File names `<speaker>_<NNNN>.wav`; the recorder writes one file per cue and a
  `session.log.jsonl` with timestamp, cue id, action and duration.
- S1 recorded T on 2026-10-19 and R-S1 over 2026-10-19/23; a 15-file alternate
  session (`S1_alt_2026-10-19T1724`) was superseded and is excluded.
- S2 recorded T on 2026-10-30 and R-S2 over 2026-10-30; the 50-sentence term
  addendum was recorded on 2026-11-11. **No S2 session log is present in the
  source checkout** (T, R-S2, anchor); the addendum builder report says 50/50
  files accepted, 0 errors. Do not infer retake or skip counts for S2.
- S3 recorded T and A on 2026-10-30.
- S1: 12 retakes over 200 T takes, 0 skips (session log). S2 addendum: 50/50
  files accepted by the builder, 0 errors. S3: session log retained.
- **Devices were not logged for every session.** This is a documented gap, not
  an inferred value. Do not claim a device per speaker in derived work.

## 4. Transcripts and annotation

- Sentence scripts were generated with LLM assistance, then imported, deduped,
  quota-checked and human-reviewed by the author. The scripts are in `text/`.
- `text` is lowercase, without punctuation or digits; apostrophes only for
  elision (`l'ho`, `un'idea`). English words keep standard spelling; Italianised
  forms are written as Italians write them (`deployato`, `forwardare`).
- `en_spans` are `[start, end)` index pairs over `text.split()`, covering
  English-origin words including Italianised forms.
- `category` is one of `single_word`, `phrase`, `brand`, `acronym`,
  `italianized`, `switch`, `control_it`, `control_en`.
- No per-row generator or date is retained in the manifests; the source scripts
  and the repository history are the provenance.

## 5. Consent and personal data

All three speakers chose **Option A (CC BY 4.0)** and confirmed it on
2026-11-16. Signed forms are held offline by the organiser and are **not** in
this repository or in the Hugging Face dataset. The published identifiers are
`S1`, `S2`, `S3` only.

The consent form asked that the voice not be used to train synthetic voices
(TTS/voice cloning) or biometric identification systems. **CC BY 4.0 does not
encode that restriction.** It is recorded here as an ethical request to
downstream users; it is not a licence condition. This tension is documented
rather than hidden. A future consent addendum could either accept TTS use
explicitly or move to a use-restricted licence.

Voice is personal data. Do not attempt to identify the speakers, and do not use
the dataset for surveillance, speaker profiling or any application the speakers
did not consent to. To request removal, contact the maintainers through
<https://huggingface.co/semantique-team>.

## 6. Quality checks

`scripts/verify.py` checks, without third-party dependencies:

- exact counts and per-speaker breakdown;
- unique `uid` and `audio`;
- every WAV exists, is 48 kHz mono 16-bit, matches its duration within 100 ms
  and matches its SHA-256;
- no unreferenced WAV under `audio/`;
- no normalised text overlap between `train` and `test`;
- every anchor sentence appears in `test`;
- valid `en_spans`.

The build also measured every file with `wave` and `afinfo`. One file,
`audio/R-S2/S2/S2_0624.wav`, had `RIFF`/`data` sizes of `0xFFFFFFFF` (an ffmpeg
streaming artefact): the header was repaired to the real file sizes without
touching the samples. The original SHA-256 and the repaired SHA-256 are in
`releases/v1.0.0.json`.

### Excluded files (16)

| Files | Reason |
|---|---|
| 15 WAV in `S1_alt_2026-10-19T1724` | Superseded alternate take session; canonical T takes are in `audio/T/S1` |
| 1 WAV `R-S2/S2/S2_0001.wav` | Unlabelled take, rejected at import and absent from `R-S2.jsonl` |

They are listed with byte sizes in `manifests/excluded.jsonl` and are not part
of the published audio.

## 7. Limitations

- **Scripted, read speech.** No spontaneous code-switching, no conversational
  overlap, no disfluency annotation.
- **Three speakers, one accent region, quiet rooms.** No telephone, far-field or
  heavy-noise condition except the separate Moth noise evaluation (not part of
  this dataset).
- **Small.** 1.46 h is a benchmark/fine-tuning set, not enough to train a
  recogniser from scratch.
- **S1 has rhotacism** (non-standard /r/). This is a real speaker characteristic
  and is disclosed; it also means T-S1 is a matched speaker for the Moth model
  trained on R-S1.
- **No speaker-disjoint test.** S3 is unseen by training but informed model
  development.
- **No word-level timestamps**, no diarization, no confidence scores.
- **LLM-generated sentences.** Human-reviewed, but the text distribution reflects
  the generation prompt, not a natural corpus sample.
- **Devices not logged** for every session.

## 8. Baseline

Moth 0.8.1 (INT8 ONNX, 19.71 MB package) on the canonical `test` split:
**24.08% WER / 55.23% ETA** over the 600 T utterances. The per-speaker spread is
5.34 pp WER and 12.02 pp ETA on the original scoring; see the paper and
`runs/E-038` in the model repository. These numbers are a reference point, not a
leaderboard claim.

## 9. Licence

- Audio and transcripts: **CC BY 4.0** — see `LICENSE-CC-BY-4.0.txt`.
- Code: **Apache-2.0** — see `NOTICE` and the model repository.
- Attribution: cite the dataset (see `CITATION.cff`) and the model/paper.

## 10. Citation

```bibtex
@dataset{moth_cs_2026,
  author    = {Bosi, Tancredi and Zanolli, Roberto and {Semantique Team}},
  title     = {Moth Italian--English Code-Switching Speech Dataset},
  year      = {2026},
  version   = {1.0.0},
  publisher = {Semantique Team},
  url       = {https://huggingface.co/datasets/semantique-team/moth-cs},
  note      = {CC BY 4.0}
}
```

A Zenodo DOI will be added to `CITATION.cff` and `releases/v1.0.0.json` when the
archive is deposited.
