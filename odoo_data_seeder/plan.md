# 🚀 Odoo Scenario Engine – Process Plan

## 🧠 Product Definition

**Odoo Scenario Engine** is an Odoo addon that allows developers to generate realistic, linked business data and simulate workflows inside a test database with one click.

---

## 🎯 Goal

Enable Odoo developers to:

* Generate realistic data instantly
* Simulate real business workflows
* Test reports, dashboards, and performance
* Avoid manual data entry and CSV imports

---

## 🧩 Core Concept

> Select scenario → Configure → Generate → Get full working dataset

---

# 🏗️ PHASE 1 – FOUNDATION (MVP CORE)

## 📌 Scope

Focus only on **Sales Scenario**

### Models Covered:

* `res.partner` (Customers)
* `product.product`
* `sale.order`
* `sale.order.line`
* `account.move` (Invoice)
* `account.payment`

---

## ⚙️ Key Features

### 1. Generator Wizard (UI)

Fields:

* Number of customers
* Number of products
* Number of sale orders
* Avg lines per order
* % confirmed
* % invoiced
* % paid
* Date range

Action:

* `Generate` button

---

### 2. Data Generation Engine

Responsibilities:

* Create realistic customers
* Create products
* Generate orders with time distribution
* Assign multiple lines per order
* Maintain logical relationships

---

### 3. Workflow Executor

Simulate real Odoo behavior:

* Create quotation
* Confirm sale orders
* Create delivery (optional for MVP skip)
* Create invoice
* Post invoice
* Register payment

---

### 4. Run Manager

Each generation creates a **Run**

Store:

* Name
* Scenario config
* Record counts
* Execution time
* Logs

---

### 5. Safety System

* Only allow in test DB (basic check)
* Confirmation before large generation
* Max record limits

---

# 🧱 MODULE STRUCTURE

```
odoo_scenario_engine/
├─ __init__.py
├─ __manifest__.py
├─ models/
│  ├─ scenario_run.py
│  ├─ generator_service.py
│  └─ helpers.py
├─ wizard/
│  └─ generate_wizard.py
├─ services/
│  ├─ data_generator.py
│  ├─ workflow_executor.py
│  ├─ field_adapter.py
│  └─ run_manager.py
├─ views/
│  ├─ wizard_views.xml
│  ├─ menu.xml
│  └─ run_views.xml
├─ security/
│  └─ ir.model.access.csv
└─ data/
   └─ default_scenarios.xml
```

---

# 🔁 DATA FLOW

1. User opens wizard
2. Inputs scenario config
3. Clicks Generate
4. System validates required fields
5. Data Generator creates base data
6. Workflow Executor processes flows
7. Run Manager logs everything
8. UI shows summary

---

# 🧠 GENERATION LOGIC

## Step 1 – Customers

* Use Faker
* Create realistic distribution

## Step 2 – Products

* Random price ranges
* Assign types

## Step 3 – Sale Orders

* Spread across date range
* Assign customers

## Step 4 – Order Lines

* Random products
* Quantity variation

## Step 5 – Workflow Execution

* Confirm % of orders
* Generate invoices
* Post invoices
* Register payments

---

# ⚠️ CUSTOM FIELD HANDLING

### MVP Strategy:

* Detect required fields
* If unknown required custom fields exist:

  * Stop generation
  * Show error message

Example:

> Missing required fields: x_customer_code

**Reminder (Deferred):** Implement custom required-field detection and a user-input wizard. (Not done yet.)

---

# 🚀 PHASE 2 – IMPROVEMENTS

## Features:

* Custom field mapping UI
* Scenario templates
* Batch deletion (cleanup)
* Preview mode
* Run comparison

---

# ⚡ PHASE 3 – ADVANCED

## Add:

* Inventory scenario
* Manufacturing scenario
* Multi-company support
* Scenario sharing
* Background job system (queue_job)

---

# 🧱 TECH STACK

## Core:

* Odoo addon/module
* Python
* PostgreSQL
* Odoo ORM

## Libraries:

* Faker
* random
* datetime

## Async (later):

* queue_job

---

# 🎯 MVP SUCCESS CRITERIA

The product is successful if:

> An Odoo developer can generate realistic test data in under 1 minute without manual setup.

---

# 🔥 FINAL POSITIONING

Not:

* Fake data generator
* CSV tool

But:

> **Odoo Business Scenario Simulator**

---

# 📌 DEVELOPMENT MILESTONES

## Milestone 1

* Wizard UI
* Generate customers + products

## Milestone 2

* Generate sale orders + lines

## Milestone 3

* Add invoice + payment flow

## Milestone 4

* Run manager + summary

## Milestone 5

* Safety checks

---

# 🧠 PRINCIPLES

* Keep it simple
* Focus on real workflow
* Use Odoo ORM always
* Avoid over-engineering
* Build for dev speed

---

# 🗺️ NEXT VERSION ROADMAP (18.0.2.0.0)

## Recommended Scope

Build **Sales to Delivery** as the next version.

Goal:

> Generate sales data, seed stock, confirm orders, create deliveries, reserve stock, validate deliveries, and track generated inventory records.

Include:

* `stock.picking`
* `stock.move`
* `stock.move.line`

Explicitly out of scope for this version:

* Purchase receipts
* Replenishment rules
* Manufacturing
* Lots/serial numbers
* Returns and backorders
* Multi-step warehouse routes
* Multi-warehouse balancing

Reason:

* This gives a full business flow through Sales + Inventory
* It keeps the implementation aligned with standard Odoo behavior
* It avoids low-level stock record generation that is harder to maintain and clean up

---

## Phase 0 – Stabilize Current Sales/Accounting Flow

Do this before inventory work.

Checklist:

* Add wizard validation for `date_end < date_start`
* Add wizard validation for percentage bounds (`0-100`)
* Track real generated invoice IDs
* Track real generated payment IDs
* Add missing payment tracking field(s) on run model
* Make cleanup service consistent with tracked generated records
* Update `test.md` to reflect actual implemented behavior
* Run smoke tests again after stabilization

Deliverable:

* Current sales/accounting scenario is stable enough to extend without creating debt in V2

---

## Phase 1 – Add Inventory Configuration Surface

Extend wizard and run model for delivery flow.

Wizard fields to add:

* `enable_inventory_flow`
* `percent_delivered`
* `warehouse_id`
* `stock_location_id`
* `initial_stock_per_product` or min/max stock quantity fields
* Optional `storable_product_ratio`

Run tracking fields to add:

* `generated_picking_ids`
* `generated_move_ids`
* `generated_move_line_ids`

Primary files:

* `wizard/generate_wizard.py`
* `wizard/wizard_views.xml`
* `models/scenario_run.py`
* `views/run_views.xml`

Deliverable:

* Inventory flow can be configured and inventory artifacts can be tracked on each run

---

## Phase 2 – Make Product Generation Inventory-Aware

Update product generation so all products are not consumables.

Checklist:

* Introduce a mix of `product` and `consu`
* Default to a practical ratio such as `70% storable / 30% consumable`
* Ensure only storable products participate in delivery workflow
* Keep existing pricing and company behavior unchanged

Primary files:

* `services/data_generator.py`

Deliverable:

* Generated sales data is compatible with stock picking and stock reservation flow

---

## Phase 3 – Add Stock Seeding Service

Create a dedicated service for initial stock setup.

Responsibilities:

* Select warehouse/internal location
* Seed stock quantities for generated storable products
* Log seeded quantities per run
* Keep test-database safety rules enforced

Implementation note:

* Prefer standard Odoo inventory quantity mechanisms
* Avoid manually creating low-level stock records unless required by the framework

Suggested file:

* `services/inventory_seed_service.py`

Deliverable:

* Sale orders can reserve stock because on-hand inventory exists before delivery execution

---

## Phase 4 – Extend Workflow Executor to Delivery

Drive inventory through normal Odoo business actions.

Target flow:

1. Confirm selected sale orders
2. Collect generated delivery pickings
3. Assign stock to pickings
4. Validate a configured percentage of deliveries
5. Capture generated moves and move lines

Checklist:

* Add picking collection helper
* Add stock assignment step
* Set done quantities through standard flow
* Validate selected pickings based on `% delivered`
* Return picking/move/move line IDs in workflow result

Primary file:

* `services/workflow_executor.py`

Deliverable:

* A full Sales to Delivery workflow exists without manually fabricating stock documents

---

## Phase 5 – Persist Inventory Results on Run

After delivery execution, save all inventory records to the run.

Checklist:

* Write generated pickings to run
* Write generated moves to run
* Write generated move lines to run
* Show these records in run form view
* Add useful summary counts and logs

Primary files:

* `services/data_generator.py`
* `views/run_views.xml`

Deliverable:

* Users can inspect generated inventory outcomes directly from generation history

---

## Phase 6 – Cleanup and Safety for Inventory Artifacts

Inventory cleanup must be deliberate and ordered.

Checklist:

* Handle move lines before moves where needed
* Handle moves before pickings where needed
* Respect Odoo restrictions for validated transfers
* Add safe cancellation/reset logic if direct unlink is not allowed
* Keep all cleanup restricted to test/sandbox databases

Primary file:

* `services/run_manager.py`

Deliverable:

* Generated inventory data can be removed safely without damaging linked records

---

## Phase 7 – Tests and Documentation

V2 is not complete without automated coverage and a manual checklist update.

Automated test priorities:

* Sale confirmation creates pickings
* Seeded stock allows reservation
* Validating deliveries creates move lines correctly
* `% delivered` controls how many pickings are completed
* Generated inventory records are saved on the run
* Cleanup handles inventory artifacts safely
* Production database safety still blocks execution

Documentation updates:

* Extend `test.md` with inventory workflow cases
* Document scope boundaries for V2
* Record deferred items clearly

Primary files:

* `tests/test_data_seeder.py`
* `test.md`

Deliverable:

* Inventory scenario is testable, documented, and safe to iterate on

---

## Suggested Delivery Sequence

1. Stabilize current sales/accounting flow
2. Add wizard + run model inventory fields
3. Implement stock seeding service
4. Make products inventory-aware
5. Extend workflow executor to delivery
6. Persist generated inventory records on runs
7. Add cleanup support
8. Add automated tests
9. Update `test.md`

---

## Version Boundary

Recommended release split:

* `18.0.1.x` = stabilize current sales/accounting seeder
* `18.0.2.0.0` = add Sales to Delivery inventory workflow

Success criteria for next version:

> An Odoo developer can generate sale orders and realistic delivery operations with one run in a safe test database.

---

# 🚀 FINAL STATEMENT

> One click → Full business dataset → Ready to test

This is your product.
