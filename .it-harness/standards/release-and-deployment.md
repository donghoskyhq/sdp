# Release and deployment standard (SKY distributed harness)

## Operating model

```text
Request
→ plan
→ isolated website change
→ checks
→ preview
→ business review
→ IT review where required
→ controlled production release
```

## Pilot process

During the pilot, releases work as follows:

- Development occurs on a project branch, never directly on the production branch.
- Preview is deployed through AWS Amplify Hosting from the branch or pull request.
- Ordinary development sessions are not given production credentials; previews must not use production credentials or sensitive production data (`security.md`).
- IT manually reviews final diffs before anything reaches production.
- Architecture-sensitive changes (anything matching an `escalation.md` trigger) require IT approval before merge.
- Harness updates are distributed by IT from the IT Harness & Architecture repository — they are not performed as ordinary website changes.

## Current limitations (facts, not future promises)

The pilot relies on manual review. There is **no** automated integrity checking of `.it-harness/` contents and **no** automated fleet-wide synchronization of harness versions. Enforcement comes from GitHub branch protections, Amplify configuration, credential scoping, and the manual IT review above — not from these instruction files.
