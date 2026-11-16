# Consent and personal data

## Status

All three speakers (S1, S2, S3) chose **Option A — CC BY 4.0** and confirmed
their consent to the maintainers on **2026-11-16**. The signed forms are held
offline by the organiser; they are **not** part of this repository, the Hugging
Face dataset or the Zenodo deposit.

| Speaker | Role | Consent | Training use | Publication |
|---|---|---|---|---|
| S1 | author | A (CC BY 4.0) | T, R-S1, A | audio + transcripts |
| S2 | external | A (CC BY 4.0) | T, R-S2, A | audio + transcripts |
| S3 | external, held out | A (CC BY 4.0) | T, A only | audio + transcripts |

S3 never contributes to `train` (see `manifests/train.jsonl` and the
`HELD_OUT_SPEAKERS` constant in `scripts/generate_scripts.py`).

## What the consent covers

The form used for the sessions is reproduced in `consent-template.md`. In
summary, each speaker agreed that:

1. their voice was recorded reading Italian sentences with English words;
2. the audio is used to train and evaluate an open-source speech recognizer;
3. the model and materials are public;
4. under Option A, the audio and transcripts may be published and reused,
   including commercially, with attribution;
5. only a technical id (`S1`, `S2`, `S3`) is associated with the recordings;
6. the voice will not be used for synthetic voice training (TTS) or biometric
   identification.

## Known licence caveat: TTS

The consent form asks that the voice not be used to train synthetic voices.
**CC BY 4.0 does not encode that restriction.** A downstream user who complies
with CC BY 4.0 (attribution) may legally use the audio for TTS or speaker
identification, even though the speakers asked them not to.

This is recorded rather than hidden. The dataset card repeats the request under
"Ethical use". If the restriction must be legally binding, the options are:

- re-consent the speakers to a use-restricted licence (for example an
  OpenRAIL-style licence), or
- keep the audio private and publish only the manifests and transcripts.

Neither change is part of v1.0.0. Do not silently relicense the audio.

## Withdrawal

A speaker may withdraw consent at any time. Because the dataset is versioned and
public downloads cannot be recalled, withdrawal applies to the next release:
the affected rows are removed from the manifests and the audio is deleted from
the canonical tree, and a new version is published with a removal note. Contact
the maintainers through <https://huggingface.co/semantique-team>.

## Data minimisation

- No names, ages, addresses, employers or contact details are published.
- Session logs contain timestamps, cue ids and durations, not free text.
- The recording guide asks speakers not to upload audio to public services; the
  transfer to the organiser was private.
- Do not attempt to re-identify the speakers. Voice is personal data.
