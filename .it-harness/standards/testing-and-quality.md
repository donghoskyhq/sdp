# Testing and quality standard (SKY distributed harness)

Validation must be proportionate: a copy tweak does not need the full battery, but no change ships on assertion alone. Select the checks relevant to the change from this list.

## Available checks

- **Type checking** (`tsc --noEmit` or the project's typecheck script).
- **Linting** (the project's lint script).
- **Automated tests**, where the project has them.
- **Production build** (`next build` or the project's build script) — required for anything beyond trivial content edits.
- **Manual preview review** of the changed pages or flows.
- **Responsive behaviour** at representative breakpoints when layout or components change.
- **Accessibility basics**: semantic structure, labels, contrast, keyboard operability for changed UI.
- **Broken-link and navigation checks** when routes, links, or the sitemap change.
- **Browser console/runtime errors** on the affected pages.
- **Regression checks** for user journeys the change could affect.

## Honest reporting

With every change, report:

- Which checks were run.
- Which passed.
- Which failed, with the failure output.
- Which were not available in the project (e.g. no test suite exists).
- Remaining assumptions and risks.

Report failures as failures — do not soften, omit, or work around them, and do not weaken a check to make it pass (`core.md`).
