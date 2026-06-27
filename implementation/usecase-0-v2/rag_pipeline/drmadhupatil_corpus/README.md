# Dr. Madhu Patil RAG Corpus Pipeline

This folder contains the RABBIT-style website-to-RAG corpus execution for `drmadhupatil.com`.

## Pipeline

```text
01_input_seed_and_config/
-> crawler_v4_site_crawler.py
-> 02_output_raw_html_rendered/
-> 03_output_structured_json/
-> 04_output_clean_json/
-> 05_output_clean_text/
-> 06_output_rag_documents/
-> 06_output_rag_documents_ready/
-> 07_output_quality_reports_manifest/
-> 07_output_enriched_documents/
```

## Current Corpus

```text
source domain: drmadhupatil.com
pages crawled: 14
pages failed: 0
approved RAG documents: 8
duplicate URL variants excluded: 6
```

The approved raw retrieval input is:

```text
06_output_rag_documents_ready/drmadhupatil_rag_corpus.jsonl
```

The default enriched retrieval input is:

```text
07_output_enriched_documents/drmadhupatil_enriched_rag_corpus.jsonl
```

The quality/readiness reports are:

```text
07_output_quality_reports_manifest/crawl_manifest.json
07_output_quality_reports_manifest/drmadhupatil_corpus_manifest.json
07_output_quality_reports_manifest/drmadhupatil_RAG_Readiness_Report.md
```

## Re-run

```bash
python -m venv /tmp/drmadhupatil-crawl-venv
source /tmp/drmadhupatil-crawl-venv/bin/activate
pip install -r requirements-crawler.txt
python -m playwright install chromium
python crawler_v4_site_crawler.py --config 01_input_seed_and_config/drmadhupatil_crawl_config.json
```

The crawler copy in this folder uses `domcontentloaded` rendering because the site keeps background network requests open and does not reliably reach Playwright `networkidle`.


## Metadata Enrichment

Run from `implementation/usecase-0-v2`:

```bash
PYTHONPATH=. python scripts/enrich_rag_metadata.py
```

This creates deterministic business metadata for filters such as `conditions`, `treatments`, `page_type`, `specialty`, and `appointment_eligible`.
