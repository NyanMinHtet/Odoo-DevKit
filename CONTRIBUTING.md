# Contributing to Odoo-DevKit

Thanks for contributing to Odoo-DevKit.

This repository is intended to be collaborative, but changes must be reviewed through pull requests.

## Branch Policy

- `main` is protected.
- Do not push directly to `main`.
- Do not force-push to `main`.
- Open a pull request for all changes.

Use the Odoo version branch that matches your target work:

- `17.0`
- `18.0`

If you are contributing to Odoo 18 modules, branch from `18.0`, not `main`, unless maintainers explicitly ask otherwise.

## What To Contribute

Good contributions include:

- new developer tools for Odoo
- bug fixes
- documentation improvements
- tests
- performance or DX improvements

Please keep each pull request focused on one topic.

## Branch Naming

Use one of these formats:

- `feature/<short-description>`
- `fix/<short-description>`
- `docs/<short-description>`
- `refactor/<short-description>`
- `test/<short-description>`

Examples:

- `feature/data-seeder-delivery-flow`
- `fix/run-cleanup-safety`
- `docs/update-pr-guidelines`

## Development Expectations

Follow the repository conventions:

- target the correct Odoo version branch
- follow Odoo 18.0 conventions where applicable
- keep module structure consistent
- update documentation when behavior changes
- update `test.md` when adding or changing features
- test only in sandbox, dev, or test databases for generation-related modules

## Pull Request Format

Use this structure in the PR description:

### Summary
- What changed
- Why the change is needed

### Scope
- Modules affected
- In scope
- Out of scope

### Implementation Notes
- Key design choices
- Data model, view, or workflow changes

### Testing
- What was tested
- Database/environment used
- Manual test steps
- Automated test results

### Checklist
- [ ] Branch is based on the correct Odoo version branch
- [ ] No direct push to `main`
- [ ] Documentation updated if needed
- [ ] `test.md` updated if behavior changed
- [ ] Changes tested in a safe database
- [ ] PR is focused and does not include unrelated changes

## Pull Request Review Guidelines

To make review easier:

- keep diffs small when possible
- explain tradeoffs clearly
- include screenshots for UI changes
- include reproduction steps for bug fixes
- mention any known limitations

## Suggested Commit Style

Commit messages should be short and descriptive.

Examples:

- `feat(odoo_data_seeder): add delivery validation flow`
- `fix(web_swagger_ui): prevent menu load error`
- `docs: add contribution and PR guidelines`

## Issues

If you are not sure about the design, open an issue first before implementing a large change.

That is especially helpful for:

- new modules
- cross-module refactors
- schema changes
- workflow changes with backward compatibility impact
