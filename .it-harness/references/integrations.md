# Integrations guidance

Read this before building anything that connects the website to data, services, or systems. It explains the three integration tiers and where common features fall.

## The three tiers

1. **Frontend prototype or mock** — no real data or service. Static content, hard-coded sample data, simulated flows, `mailto:` links. Fully within business/SLT direction; build freely. Label mocks clearly so no one mistakes them for working integrations.

2. **Approved external/public integration** — a third-party service listed in the project `CLAUDE.md`'s "Approved integrations", using public/publishable keys only and no SKY-internal access. Build against the approved interface; adding a *new* external service follows `references/dependency-guidance.md` and, where it creates operational commitments, `standards/escalation.md`.

3. **Privileged production integration** — anything touching company databases or internal systems, production credentials, authentication, payments, or personal/sensitive data. Always requires escalation, and once approved must go through an **IT-approved server-side interface** (a server action, route handler, or IT-provided API) — never directly from browser code (`standards/security.md`).

## Examples

| Feature | Prototype/mock | Approved external | Privileged production |
|---|---|---|---|
| **Booking** | Simulated booking flow with sample availability | Embedded IT-approved booking widget/SaaS | Booking wired to an internal reservations system |
| **Contact form** | Form that displays a "sent" state without sending | IT-approved form service with a publishable key | Form posting to internal CRM or company email infrastructure |
| **Customer accounts** | Static "my account" mock screens | — (accounts are inherently privileged) | Any real sign-up/login/user store → escalate |
| **Payments** | Fake checkout for design review, clearly labelled | — (payments are inherently privileged) | Any real payment processing → escalate |
| **Internal business systems** | Screens using representative sample data | — | Any live connection to a SKY system → escalate, then IT-approved server-side interface |
| **Databases** | Local JSON/static content as stand-in data | — | Adding or connecting any database → escalate |
| **Analytics** | None needed for a mock | IT-approved analytics snippet with its public site ID | Analytics fed personal or internal data → escalate |

## Rule of thumb

If the feature needs a secret, an account IT controls, or real customer/company data, it is privileged: escalate first, and implement only through the server-side interface IT approves. If it can work with public keys or no keys at all, check the project's approved list. If it can be faked convincingly, prototype it now and let the business review the experience while IT reviews the capability.
