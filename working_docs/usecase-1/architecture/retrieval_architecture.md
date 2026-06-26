# Retrieval Architecture

## Purpose
This document defines how website and FAQ answers are retrieved.

## Retrieval Sources
```text
curated FAQs
website content
service catalog
clinic location data
```

## Recommended Folder Model
```text
knowledge_base/
  website/
    pages.jsonl
  faqs/
    faq_source.jsonl
  indexes/
    website_faq_vector.index
    metadata.json
```

## Retrieval Flow
```text
User question
-> embed query
-> retrieve top FAQ/website chunks
-> apply confidence threshold
-> answer from retrieved content if confidence is good
-> route to Google Search if confidence is low
```

## FAQ Record Example
```json
{
  "faq_id": "FAQ-001",
  "category": "ivf",
  "question": "What is IVF?",
  "answer": "IVF is a fertility treatment where eggs and sperm are combined outside the body.",
  "tags": ["ivf", "fertility"],
  "status": "active",
  "updated_at": "2026-06-26"
}
```

## Grounding Rule
The agent must prefer clinic-owned website/FAQ content. Google Search is fallback, not the default.
