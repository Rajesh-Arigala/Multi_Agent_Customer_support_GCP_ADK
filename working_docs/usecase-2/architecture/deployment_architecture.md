# Deployment Architecture

## Purpose
This document defines the intended deployment path for RAG by RABBIT.

## Current State
RABBIT Assistant already exists as a Render-hosted Flask RAG app backed by Azure AI Search and Azure OpenAI.

## Target State
RAG by RABBIT should be deployable as a chat widget on `rajesharigala.com` with an action-agent backend.

## Deployment Layers
```text
rajesharigala.com chat widget
-> RAG by RABBIT backend API
-> RABBIT RAG retrieval layer
-> engagement/action tools
-> Google Sheets or CRM-style storage
-> notification/contact layer
-> observability and audit logs
```

## Future Sentinel Connection
Sentinel Gateway can later sit in front of model/tool execution for governance, routing, safety, validation, evaluation, cost control, and observability.
