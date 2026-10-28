# Synthetic evaluation

Run from the repository root:

```powershell
& '.\backend\.venv\Scripts\python.exe' evaluation/generate.py
& '.\backend\.venv\Scripts\python.exe' evaluation/run.py
```

Both commands were executed. Generator v1 freezes **240 cases,32institutions,528policy-labelled pairs and98identity queries** with file hashes. It refuses to overwrite a changed corpus. Cases contain no gold labels, split names or template metadata; evaluator-only files hold these. Conservative generation-family/wording groups stay in one split. Known held-out institutions also have separate development families;16unseen institutions have no development cases. Held-out queries have their counterparts in the same held-out gallery, which is never used for tuning.

The generated cases cover exact/paraphrased refund requests, distinct complainants, independent faculty issues, date contradictions, missing facts/IDs, alias/name collisions, all lifecycle states and untrusted instruction text. Annotation follows explicit synthetic policy; **no independent human label review has occurred**. Category and structured reference fields make this an intentionally artificial rules benchmark. Hindi text appears in missing-evidence examples; this does not test Hindi semantic understanding.

`docs/evidence/stage8/latest.json` identifies the latest immutable run directory. It contains summary/per-class support/precision/recall/F1/confusion matrix, UNKNOWN coverage, per-split results, identity errors, raw classifications, raw rankings, false positives/negatives and latency samples. Earlier runs remain preserved. Hashes identify matcher/generator/evaluator versions. Timing is measured on the recorded host; it excludes HTTP/UI/startup and does not claim national-scale performance. The vector first pass starts with an empty SQLite cache but later queries may hit it; the warm repeat reuses it.

Observed on run20261027T151206Z-50f45006:168held-out pairs (12DUPLICATE,20RELATED,44INDEPENDENT,92UNKNOWN) matched the generated policy labels; the classification error file is empty.40retrieval queries had mean counterpart recall@1=.6 and recall@3=1.0 for both methods. The baseline warm median was.3765ms; optional character-vector warm median1.4244ms, including its cache operations.98/98synthetic exact/alias/ambiguity identity expectations matched. These values describe this frozen artificial corpus only, not real-world accuracy.

The optional encoder is `hashed-character-ngrams-128-v1`, a statistical text vector rather than a semantic language model. It did not improve retrieval; **the explainable baseline remains the default**. Both methods share the same relationship classifier, so no independent enhanced-classifier F1 claim is made. Semantic/LLM status stays unavailable. A strict optional-adapter validator is tested with synthetic valid/invalid/outage fixtures; no live model result is invented.

The API separately prioritises explicit incident references before its50candidate cap, including older disposed complaints. Tests add55newer unrelated records to prove a referenced disposed case is retained. Full role/security tests verify scope before candidate ranking. This is a bounded prototype strategy; no indexed full-text/production database scale result is claimed.
