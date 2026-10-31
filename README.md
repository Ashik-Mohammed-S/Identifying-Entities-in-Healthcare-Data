# Healthcare Entity Extraction

[![Validation](https://github.com/Ashik-Mohammed-S/Identifying-Entities-in-Healthcare-Data/actions/workflows/validate.yml/badge.svg)](https://github.com/Ashik-Mohammed-S/Identifying-Entities-in-Healthcare-Data/actions/workflows/validate.yml)

Extract contiguous disease and treatment spans from the supplied annotated sentences.

Independent public portfolio work; historical educational notebooks remain under `historical/`. The current implementation and results described here take precedence over historical in-sample numbers.

## Data and approach

2,599 training sentences (45,902 tokens) and 1,056 test sentences (18,618 tokens), with original separate token/label files.

Preserve source tokenization, verify every token/label pair, compute sentence-context POS features once, and fit a CRF on training sentences. Evaluate entity tokens and exact label/start/end spans, excluding the majority O label from entity F1.

## Current full-data result

| Measure | Current analysis | Baseline where applicable |
| --- | --- | --- |
| Entity-token micro-F1 | 0.693 | — |
| Exact-span precision | 0.681 | — |
| Exact-span recall | 0.538 | — |
| Exact-span F1 | 0.601 | — |

Results are specific to the documented dataset and split. See generated `results/analysis.json` after execution for full metrics and assumptions.

## Run locally

Use the Python version in `.python-version`, then:

```sh
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
python scripts/fetch_data.py
python scripts/run_notebook.py --mode full
```

Reference data is committed under `dataset/`, directly or as reconstructable compressed parts. The downloader verifies checksums and restores stored data offline. See [DATA.md](DATA.md) and [dataset-sources.json](dataset-sources.json) for provenance and upstream terms. Package installation and the spaCy model, where needed, require network access on a fresh machine.

## Review the implementation

Inspect source token alignment, contextual POS batching and the exact-span scorer. Start with [scripts/analysis.py](scripts/analysis.py), then the root notebook. The workflow validates dependencies, smoke checks and full-data notebook execution with dataset downloads disabled.

## Limitations

Annotation research only: no patient-facing inference, diagnosis or clinical decision support. Span boundaries are harder than token classification. The corpus does not establish transfer to clinical production data.

[Method notes](ANALYSIS.md) · [All portfolio projects](https://github.com/Ashik-Mohammed-S/Ashik-Mohammed-S/blob/main/PORTFOLIO.md)
