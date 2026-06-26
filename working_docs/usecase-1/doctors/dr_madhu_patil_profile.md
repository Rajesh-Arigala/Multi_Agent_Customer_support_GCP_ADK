# Dr. Madhu Patil Profile

## Purpose
This document stores the doctor profile facts that the agent can use for clinic-facing conversations. It prevents the assistant from inventing profile details.

## Audience
- Clinic team
- Product team
- Agent prompt and retrieval designers

## Agent Intent
The agent should represent the clinic professionally and respectfully. It should help visitors understand services and guide them toward the right appointment path without giving medical diagnosis.

## Profile Facts
Source website:

```text
https://drmadhupatil.com
```

Known positioning from review:

```text
Dr. Madhu Patil is positioned as a gynecologist and IVF/fertility specialist.
The website discusses fertility services, IVF, ICSI, IUI, fertility preservation, PCOS, endometriosis, and related reproductive-health topics.
```

## Example Usage
User:

```text
Who is Dr. Madhu Patil?
```

Expected agent behavior:

```text
Dr. Madhu Patil is our doctor and fertility/gynecology specialist. I can help you understand the services listed on the website and help you request an appointment. This is general information and not a medical diagnosis; our doctor can guide you based on your medical history, reports, and test results.
```

## Do Not Do
- Do not invent awards, qualifications, years of experience, or hospital affiliations unless confirmed.
- Do not compare the doctor negatively against other doctors.
- Do not diagnose based on chat messages.

## Open Questions
- Final verified doctor bio.
- Final qualifications and credentials to include.
- Approved short and long profile descriptions.
