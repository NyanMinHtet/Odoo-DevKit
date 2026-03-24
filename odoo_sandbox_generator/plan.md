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

# 🚀 FINAL STATEMENT

> One click → Full business dataset → Ready to test

This is your product.

