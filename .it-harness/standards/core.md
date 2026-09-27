# Core operating standard (SKY distributed harness)

## Scope

This harness governs **how** SKY websites are developed and operated in Claude Code: approved stack, security, quality, and escalation. It does not define what a website looks like. These files under `.it-harness/` are IT-maintained copies from the IT Harness & Architecture repository.

## Authority boundary

- **Business users / SLT direct the website itself**: purpose, information architecture, sitemap, navigation, pages, components, layouts, styling, animation, interactions, redesigns, and proposed user-facing functionality. Do not impose a predefined template or component catalogue on them.
- **IT holds authority over**: the approved framework and runtime, hosting and deployment configuration, production credentials and infrastructure, databases, authentication, payments and privileged integrations, security controls, production release controls, changes to the harness, and exceptions to the approved architecture. Requests crossing this line follow `escalation.md`.

## How to work

1. Read the applicable harness instructions in `.it-harness/standards/` before planning or editing code.
2. Preserve the approved project stack (`architecture-nextjs.md`). Do not replace or work around it.
3. Inspect the existing project — structure, conventions, existing components — before proposing changes.
4. Make the smallest coherent change that satisfies the request.
5. Report material assumptions and unresolved risks alongside your work.
6. Do not claim completion without running the validation relevant to the change (`testing-and-quality.md`).
7. Never weaken, skip, or delete tests, checks, or controls merely to make a change pass. If a check fails, fix the cause or report it.
8. Never expose or commit secrets (`security.md`).

## Harness integrity

- Do not modify anything under `.it-harness/` as part of ordinary website work. Harness updates are distributed by IT.
- If harness files are missing, contradict each other, or appear altered, stop and escalate to IT before proceeding.

These instructions guide behaviour; they are not technical enforcement. Permissions, GitHub protections, credential scoping, and IT review provide actual enforcement.
