# User Journey Examples

## Purpose
This document gives realistic examples so business and technical audiences understand the intended behavior.

## Journey 1: Casual FAQ
```text
User: What is IVF?
Agent: Answers from website/FAQ retrieval, gives a short disclaimer, and asks whether the user wants appointment help.
Outcome: No registration required.
```

## Journey 2: Level 1 Identity
```text
User: I have been reading about IVF and want to know more.
Agent: May ask for name and phone so the clinic can continue the conversation if the user wants follow-up.
Outcome: Lead created with name, phone, preferred language.
```

## Journey 3: Appointment Request
```text
User: I want to meet the doctor this week.
Agent: Collects Level 2 details: location, date/time preference, consultation type, reason for visit.
Outcome: Appointment request created.
```

## Journey 4: Returning User
```text
User: My name is Anjali, phone is 9XXXXXXXXX. I spoke two days ago.
Agent: Looks up user by phone, uses session/memory if available, and continues naturally.
Outcome: Continuity without forcing the user to repeat everything.
```

## Journey 5: Telugu Transliteration
```text
User: ivf gurinchi details kavali
Agent: Detects Telugu transliteration in Latin script and replies in Telugu transliteration unless the user changes language.
Outcome: Multilingual accessibility.
```

## Journey 6: Emergency
```text
User: This is urgent, I need help now.
Agent: Gives urgent disclaimer, creates emergency ticket if contact is available, and says the user will receive a call from our doctor or concerned authority.
Outcome: Human handoff.
```
