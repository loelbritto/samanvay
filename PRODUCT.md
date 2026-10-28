# Samanvay

Samanvay is a clearly labelled student prototype for institutional complaint coordination. Its people, institutions, complaints, policies and integrations are synthetic demonstrations. It has no official AICTE connection.

## Users and work

Officers find complaints, review evidence and record the next action. Supervisors assign owners and exercise explicitly delegated powers. Coordinators agree institution plans across bureaus without taking over case ownership. Management sees its authorised scope. Administrators maintain demonstration accounts without acquiring complaint access.

The first screen should help an officer choose what to work on. The user reported too many controls and technical terms and asked for a professional redesign, delegating implementation choices. Prefer plain labels, a calm work queue, obvious ownership and progressively disclosed secondary actions. No standing aesthetic preference beyond this has been confirmed.

## Invariants

Preserve every complaint and original submission. Institution identity, complaint relationship, complaint ownership and coordination responsibility are separate concepts. Persistent database state backs workflows; optimistic versions, scope checks, audit events and outbox jobs remain authoritative. Automated relationship output is a suggestion requiring authorised human review; it never merges records or decides outcomes.

## Platform and limits

Local web app: React, TypeScript, Vite, FastAPI and SQLAlchemy, with SQLite and private evidence files. Keep the existing databases intact. Production hosting, official integrations, real notification delivery and validated ML accuracy are outside the demonstrated implementation. Browser acceptance requires actual rendered evidence; code checks cannot substitute for it.
