# Anti-Hallucination Policy

## Purpose
This document ensures RAG by RABBIT stays evidence-based.

## Rules
```text
answer from retrieved evidence
do not invent credentials
do not invent client names
do not invent current role status
do not invent compensation numbers
do not invent availability
say uncertainty when evidence is missing
```

## Example
User:

```text
Has Rajesh built a dedicated GenAI project?
```

Expected behavior:

```text
Answer based on current indexed evidence. If the dedicated GenAI section is pending, say that clearly and mention available AI/MLOps/RAG evidence.
```

## Debug Need
Debug/owner mode may expose source chunks and retrieval scores. Public user mode should stay clean.
