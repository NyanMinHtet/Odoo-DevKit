# Odoo Data Seeder

## Overview
**Odoo Data Seeder** is an Odoo addon that allows developers to generate realistic, linked business data and simulate workflows inside a test database with one click.

## Features
- Generate realistic data instantly
- Simulate real business workflows
- Test reports, dashboards, and performance
- Avoid manual data entry and CSV imports

## Installation
1. Place the module in your addons path
2. Update the app list: `Apps > Update Apps List`
3. Install the module: `Apps > Odoo Data Seeder`

## Usage
1. Go to **Data Seeder > Generate Data**
2. Configure your scenario:
   - Number of customers, products, orders
   - Workflow percentages (confirmed, invoiced, paid)
   - Date range
   - Price and quantity settings
3. Click **Generate**
4. View the generated data in **Data Seeder > Generation History**

## Safety
- Only works in test/sandbox databases (database name must contain: test, sandbox, dev, stage, or demo)
- Maximum limits: 1000 customers, 500 products, 5000 orders
- Confirmation required before large generation

## Requirements
- Python: `faker` library (optional but recommended)
  ```bash
  pip install faker
  ```

## Automated Tests
Run the module tests without manual UI steps:

```bash
./odoo/odoo-bin -c odoo.conf -d sandbox -u odoo_data_seeder --test-enable --test-tags /odoo_data_seeder --stop-after-init
```

Notes:
- Replace `-c odoo.conf` with your actual config path if different.
- Use a test database name (for example: `sandbox`, `dev_db`, `test_db`).
- `--stop-after-init` exits after running tests, which is ideal for CI/local checks.

## Dependencies
- `base`
- `sale`
- `sale_management`
- `account`

## License
LGPL-3
