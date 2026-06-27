from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.retrieval.metadata import enrich_document_row


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = BASE_DIR / "rag_pipeline/drmadhupatil_corpus/06_output_rag_documents_ready/drmadhupatil_rag_corpus.jsonl"
DEFAULT_OUTPUT_DIR = BASE_DIR / "rag_pipeline/drmadhupatil_corpus/07_output_enriched_documents"
DEFAULT_OUTPUT_PATH = DEFAULT_OUTPUT_DIR / "drmadhupatil_enriched_rag_corpus.jsonl"
DEFAULT_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "metadata_enrichment_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add deterministic business metadata to RAG documents.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"Input corpus not found: {args.input}")

    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    enriched_rows = [enrich_document_row(row) for row in rows]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in enriched_rows) + "\n",
        encoding="utf-8",
    )

    page_types = _count_values(row["metadata"].get("page_type", "") for row in enriched_rows)
    priorities = _count_values(row["metadata"].get("source_priority", "") for row in enriched_rows)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metadata_version": "v1_business_rules",
        "input_path": str(args.input),
        "output_path": str(args.output),
        "document_count": len(enriched_rows),
        "page_types": page_types,
        "source_priorities": priorities,
        "required_fields": [
            "page_type",
            "service_slug",
            "service_name",
            "specialty",
            "conditions",
            "treatments",
            "intent",
            "appointment_eligible",
            "emergency_related",
            "source_priority",
        ],
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("RAG metadata enriched")
    print(f"documents={len(enriched_rows)}")
    print(f"output={args.output}")
    print(f"manifest={args.manifest}")
    print(f"page_types={page_types}")


def _count_values(values) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


if __name__ == "__main__":
    main()
