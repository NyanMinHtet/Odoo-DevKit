# Odoo-DevKit
A collection of Odoo modules designed to enhance the developer experience (DX) and streamline workflows.

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## Vision
  This repository is dedicated to making Odoo development faster, easier, and more enjoyable. It contains a curated set of modules that add helpful features and tools for developers, focusing on improving the overall Developer Experience (DX).

## Versioning

This repository maintains separate branches for each major Odoo version to ensure compatibility. Each module within this repository will follow this branching strategy.

-   **Odoo 17:** `17.0`
-   **Odoo 18:** `18.0`

Future versions will follow the same pattern. Please ensure you are using the branch that corresponds to your Odoo version.

## Available Modules
| Module | Description |
| :--- | :--- |
| **[web_swagger](./web_swagger/)** | Integrates Swagger UI for beautiful, interactive API documentation. |
| **[odoo_data_seeder](./odoo_data_seeder/)** | Generate realistic, linked business data and simulate workflows inside a test database with one click. |

## Contributing
Contributions are welcome, but changes must go through pull requests.

- Do not push directly to `main`.
- Do not force-push to `main`.
- Create a feature or fix branch from the correct Odoo version branch, usually `18.0`.
- Open a pull request with a clear summary, scope, testing notes, and affected modules.
- Keep pull requests focused. Avoid mixing unrelated fixes and features in one PR.

Recommended branch names:

- `feature/<short-description>`
- `fix/<short-description>`
- `docs/<short-description>`
- `refactor/<short-description>`

Examples:

- `feature/inventory-delivery-seeder`
- `fix/swagger-menu-loading`
- `docs/contribution-guide`

Before opening a pull request:

- follow Odoo version and module conventions used in this repo
- update module documentation when behavior changes
- update `test.md` when adding or changing features
- include steps to verify the change in a sandbox or test database

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full contribution workflow and PR format.

## License
This project is licensed under the LGPL-3 License. See the [LICENSE](LICENSE) file for details.
