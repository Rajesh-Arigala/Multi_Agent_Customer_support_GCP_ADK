# Data Storage Schema

## Purpose
This document defines the initial storage approach.

## Storage Decision
Use Google Sheets immediately for operational access and keep a local CSV mirror for development and backup.

## Why Google Sheets First
- Clinic team can access and update records.
- No database admin overhead.
- Easy to audit during first deployment.
- Can later be swapped for Firestore or Cloud SQL through a storage interface.

## Storage Interface
```text
StorageService
-> GoogleSheetsStore for production operations
-> CsvStore for local development and backup
```

## Core Tables
```text
Users
Leads
Appointments
EmergencyTickets
FAQ
AuditLog
```

## Local Mirror
```text
data/users.csv
data/leads.csv
data/appointments.csv
data/emergency_tickets.csv
data/faqs.csv
data/audit_log.csv
```

## Identity Rule
```text
user_id = normalized phone number
session_id = runtime conversation session
memory = long-term facts and preferences
```
