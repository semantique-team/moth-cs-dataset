# Registrazioni Moth — guida operativa

Questa guida descrive come registrare nuove sessioni per estendere il dataset
oltre la v1.0.0. La v1.0.0 è chiusa: S1, S2 e S3 hanno già registrato T, R e A.
S4 non è stato registrato e non fa parte del dataset.

## Prima di registrare

1. Leggere e firmare `docs/consent-template.md`. Senza consenso scritto non si
   registra. La scelta va annotata in `docs/consent.md` e nel release record.
2. Non caricare audio su GitHub, issue, PR o servizi pubblici. L'audio è dato
   personale: va trasferito privatamente all'organizzatore.
3. Su macOS servono `git`, Python ≥ 3.12, `uv` e `ffmpeg`.
4. Non servono checkpoint o shard: bastano questo repository e lo script.

```bash
git clone <url-del-repository-dataset>
cd moth-cs-dataset
brew install ffmpeg   # solo macOS
# le dipendenze Python vengono installate da `uv run --with ...` qui sotto
```

## Ruoli

| Speaker | T | A | R |
|---|---|---|---|
| S1 | completo | completo | completo (741) |
| S2 | completo | completo | completo (672) |
| S3 | completo | completo | **mai** (held out) |
| S4 | non registrato | non registrato | non applicabile |

Per un nuovo speaker usare un id nuovo (`S5`, `S6`, …) e aggiungerlo a
`T_SPEAKERS` in `scripts/generate_scripts.py`; non riusare un id esistente.

## Registrare

Il recorder `scripts/record.py` usa `ffmpeg`/AVFoundation e funziona solo su
macOS. Mostra una frase alla volta e salva un WAV per frase.

```bash
# prova a vuoto: elenca le frasi senza registrare
python -m scripts.record --speaker S5 --kind T --dry-run

# sessione T: audio/T/S5/S5_0001.wav
python -m scripts.record --speaker S5 --kind T

# anchor A: audio/anchor/S5/S5_0001.wav
python -m scripts.record --speaker S5 --kind A
```

Comandi durante la sessione:

- **Enter**: avvia la registrazione; **Enter** di nuovo: ferma e salva.
- **p**: riascolta; **r**: rifai; **s**: salta; **q**: esci.
- Al primo utilizzo macOS chiede il permesso microfono al terminale. Se lo
  neghi: Impostazioni di Sistema → Privacy e sicurezza → Microfono → abilita il
  terminale.
- Durata target 1–30 s, parlato naturale, picchi circa −12/−6 dBFS, niente
  clipping. Meglio sessioni da 50–60 frasi.

## Dopo la sessione

Il recorder scrive `session.log.jsonl` accanto all'audio: conservalo. Poi:

```bash
python -m scripts.build_manifest build --kind T --speaker S5 \
    --scripts-dir text --audio-dir audio/T --out manifests/T-S5.jsonl
python scripts/verify.py
```

Se il manifest nuovo è a posto, va mergiato in una **nuova versione** del
dataset (non in v1.0.0), con un nuovo `releases/vX.Y.Z.json`. Non modificare i
manifest pubblicati: gli hash e i confronti con il modello precedente si
romperebbero.

## Privacy

- Solo l'id tecnico dello speaker compare nel dataset; niente nomi, età, email.
- Non usare la voce per TTS, identificazione biometrica o sorveglianza.
- Se uno speaker ritira il consenso, rimuovere le sue righe dalla versione
  successiva e annotare la rimozione nel release record.
