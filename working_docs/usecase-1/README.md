# Usecase 1 Working Documentation

## Purpose
This folder contains the working documentation for the doctor appointment agent use case. The goal is to define product intent, architecture, data, operations, and safety requirements before implementation begins.

## Use Case Summary
The agent is a multilingual clinic website assistant for Dr. Madhu Patil. It answers patient and prospect questions from website/FAQ embeddings, supports light lead capture, helps users request in-person, phone, or video consultation appointments, and escalates urgent concerns to the registration desk and our doctor or concerned authority.

## Folder Map
```text
doctors/       doctor profile, clinic locations, services catalog
use_cases/     journeys, emergency flow, multilingual support
architecture/  system architecture, agent schema, data, retrieval, deployment
operations/    Google Sheets, FAQ CRUD, appointments, SMS, human handoff
safety/        medical disclaimer, emergency response, privacy notes
product/       cost control strategy
```

## Core Business Intent
```text
Answer questions -> build trust -> capture useful identity -> book consultation -> notify humans -> preserve safety.
```

## Implementation Boundary
These documents define intent. They are not implementation. Implementation starts only after explicit approval.
