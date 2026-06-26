# FAQ CRUD Process

## Purpose
This document defines how FAQs are created, updated, deleted, and re-indexed.

## Source Of Truth
Use Google Sheet `FAQ` as the editable source and local JSONL/CSV as a mirrored build artifact.

## Create FAQ
```text
Clinic team adds question and answer in Google Sheet
status = active
index rebuild script includes it
```

## Update FAQ
```text
Clinic team edits answer
updated_at changes
index rebuild script refreshes embedding
```

## Delete FAQ
Prefer soft delete:

```text
status = inactive
```

This keeps audit history.

## Rebuild Flow
```text
Read FAQ sheet
validate required fields
export faq_source.jsonl
generate embeddings
build/update vector index
write index metadata
```
