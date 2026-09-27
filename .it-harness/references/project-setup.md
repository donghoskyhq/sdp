# Project setup (manual pilot procedure)

How IT sets up a new SKY website project during the pilot. Every step is manual and performed by IT (or with IT alongside the business owner).

## Steps

1. **Create or prepare the project repository** on GitHub. Configure the default branch and enable pull-request-based review (branch protection on the production branch).

2. **Start with a minimal working Next.js/TypeScript foundation** — App Router enabled, TypeScript configured, versions pinned in `package.json` and the lockfile. `create-next-app` defaults are an acceptable starting point.

3. **Do not apply a predefined visual website template.** The business owner will direct the site's design, sitemap, and components through Claude Code. The foundation should be structurally minimal.

4. **Copy the approved harness into `.it-harness/`** from an up-to-date checkout of the IT Harness & Architecture repository:

   ```bash
   node scripts/copy-harness.mjs <path-to-project>
   ```

   Use `--dry-run` first if you want to preview the file list, and `--replace` when updating an existing copy.

5. **Create the project `CLAUDE.md`**: copy `templates/project-CLAUDE.md` to the project root as `CLAUDE.md` and fill in every placeholder (project name, business owner, purpose, audience, scope, design direction, approved integrations, constraints, commands). The copy script deliberately never writes this file.

6. **Have the design team fill in the brand guidelines**: copy `templates/project-brand-guidelines.md` to the project root as `brand-guidelines.md` and hand it to the design team to complete (logo assets, palette, typography, imagery, motion, accessibility commitments) before the project is handed over to the business owner. This file is design-team-owned project content — it is not part of `.it-harness/` and is not distributed by the copy script. Commit the brand's logo and font assets it references at the same time.

7. **Record provenance**: confirm `.it-harness/manifest.json` shows the correct harness version and source commit (the copy script stamps these automatically when run from a Git checkout). Commit the harness, `CLAUDE.md`, and `brand-guidelines.md` together with a message noting the harness version.

8. **Configure repository access**: give the business owner and any collaborators appropriate GitHub access; keep production-branch merge rights with IT for the pilot.

9. **Configure Amplify preview**: connect the repository to AWS Amplify Hosting with branch/PR previews enabled. Do not provide production credentials or sensitive production data to preview environments.

10. **Verify loading in a fresh local Claude Code session**: open the project, start a new session, and confirm the standards are loaded (e.g. ask Claude what the escalation triggers are, or use `/context`/`/memory` to inspect loaded files).

11. **Verify loading in a fresh browser/cloud Claude Code session**: select the project repository in a cloud session and repeat the check. Remember cloud sessions only receive committed files, so `.it-harness/` and `CLAUDE.md` must be pushed first.

12. **Conduct manual diff and preview review before release**: before the first production release (and each subsequent one), IT reviews the full diff and the Amplify preview per `standards/release-and-deployment.md`.

## Updating the harness in an existing project

Re-run the copy script with `--replace` from a checkout at the approved version; review the printed list of changing files; commit via a pull request labelled as a harness update, reviewed by IT — not as part of an ordinary website change.
