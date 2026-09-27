# Approved architecture: Next.js (SKY distributed harness)

This standard defines the approved technical profile. It says nothing about the website's appearance — see "Open to SLT direction" below.

## Approved stack

- **Next.js with the App Router**, written in **TypeScript**.
- The versions pinned in the project's `package.json` and lockfile are authoritative. Do not upgrade or downgrade framework or runtime versions as a side effect of other work.
- Source control on GitHub; previews and deployment through AWS Amplify Hosting; pull-request-based review (`release-and-deployment.md`).

## Component and code boundaries

- Use Server Components by default where appropriate; use Client Components when browser state, browser APIs, or interactivity require them.
- Keep browser-delivered code separated from privileged server operations (server actions, route handlers, server-only modules).
- Preserve maintainable boundaries between UI, application logic, and external integrations.
- Use environment-specific configuration for anything that differs between preview and production; never place credentials or server-only values in client bundles (`security.md`).

## Stability rules

- No silent framework migration (to another framework, a different router paradigm, or plain JavaScript).
- No silent introduction of an additional backend, runtime, or hosting platform. Wanting one triggers escalation (`escalation.md`).
- Avoid unnecessary dependencies (`references/dependency-guidance.md`) and custom infrastructure when the platform already provides the capability.
- Examine the existing project structure and follow its conventions before reorganizing it; reorganize only when the change requires it.

## Open to SLT direction

The following are business decisions, not architecture, and remain fully open to SLT/business direction:

- Sitemap and navigation.
- Page structure.
- Components.
- Styling.
- Animation.
- User journeys.
- Frontend interaction design.
- Overall visual and creative direction.
