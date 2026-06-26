# Retrieval Architecture

## Purpose
This document defines how RAG by RABBIT answers from evidence.

## Retrieval Sources
```text
rajesharigala.com website corpus
RABBIT approved chunks
Azure AI Search index
project evidence
profile positioning context
future Sentinel evidence
```

## Retrieval Flow
```text
Stakeholder question
-> query embedding
-> Azure AI Search hybrid retrieval
-> answer with evidence
-> if evidence is insufficient, say uncertainty or use web fallback when appropriate
```

## Evidence Rule
The agent must not invent unsupported claims. If evidence is missing, it should say the information is not available yet and offer a useful next direction.

## Example
User:

```text
What GenAI projects has Rajesh built?
```

Expected behavior:

```text
Answer from current indexed evidence. If dedicated GenAI pages are not indexed, say so clearly and mention currently available AI/MLOps/RAG evidence.
```
