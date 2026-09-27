# Escalation standard (SKY distributed harness)

Some requests cross from website development into IT authority. When one does, **stop before implementing the affected production capability** and request IT review. Frontend work that does not depend on the escalated capability may continue.

## Escalation triggers

Escalate when a request involves any of the following:

- Replacing Next.js or the approved hosting platform.
- Adding or changing cloud infrastructure.
- Adding a database or production data store.
- Connecting to a company database or internal system.
- Authentication, authorization, or user-account management.
- Payments or financial transactions.
- Personal, employment, customer, or other sensitive data.
- New production credentials or elevated permissions.
- DNS, domain, or certificate changes.
- New backend services, queues, scheduled jobs, or persistent workers.
- Destructive migrations.
- Changes to deployment or production-release controls.
- Changes to `.it-harness/`.
- Missing or conflicting harness instructions.
- Any request whose operational or security impact cannot be determined confidently.

## Expected escalation response

When escalating:

1. Explain the requested business outcome in the requester's terms.
2. Identify the specific capability requiring IT review.
3. Explain why it crosses the SLT/IT authority boundary.
4. Propose a safe frontend-only mock or prototype if that would help the business evaluate the idea (`references/integrations.md`).
5. List the decisions or access required from IT.
6. Do not silently implement an alternative privileged architecture instead.
