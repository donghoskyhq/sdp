# Dependency guidance

Read this before adding or upgrading a package in a SKY website project.

## Position

Dependencies are **permitted when justified**. A blanket prohibition would unnecessarily restrict website development — good libraries for UI, animation, forms, and content are a normal part of building a modern site. The requirement is judgement, not avoidance.

## Before adding a package

1. **Check it's actually needed.** Avoid adding packages for functionality already provided safely by the platform (Next.js, React, the browser, Node built-ins) or by dependencies the project already has. A date formatter, a class-name joiner, or a simple carousel may not earn a dependency.
2. **Review the package**: its purpose (does it do one clear thing the project needs?), maintenance status (recent releases, responsive maintainers, healthy usage), and security implications (install scripts, network access, transitive dependency weight, known advisories).
3. **Keep the lockfile updated** and committed together with `package.json`. The lockfile is what pins the project's versions (`standards/architecture-nextjs.md`).
4. **Report the addition** in your summary of the change: what was added, why, and what was considered.

## When a dependency requires escalation

Follow `standards/escalation.md` before adopting any dependency that:

- Introduces privileged infrastructure (its own backend, database client wired to production, hosting agent).
- Connects the project to an external service requiring accounts, API keys, or contracts.
- Creates a material operational commitment — something IT would have to run, pay for, patch, or monitor.

A styling library is a website decision; a payments SDK is an IT decision.
