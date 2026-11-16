# Session logs

One JSON object per take: `ts`, `id`, `action` (`ok`, `retake`, `skip`) and
`duration`. They document retakes and skips; they contain no free text.

| File | Session |
|---|---|
| `T-S1.jsonl` | S1, T, 2026-10-19 |
| `T-S3.jsonl` | S3, T, 2026-10-30 |
| `R-S1-S1.jsonl` | S1, R-S1, 2026-10-19/23 |
| `anchor-S1.jsonl` | S1, anchor A, 2026-10-19 |
| `anchor-S3.jsonl` | S3, anchor A, 2026-10-30 |
| `excluded-S1-alt.jsonl` | S1 alternate session, superseded and not published |

## Missing logs

There is **no S2 session log** in the source checkout: not for T, not for
R-S2, not for the anchor. The S2 term addendum (2026-11-11) has a builder report
saying 50/50 files were accepted with 0 errors, but the recorder log was not
returned. Do not invent retake or skip counts for S2.

The data card states this limitation; it is also in
`releases/v1.0.0.json` under `notes`.
