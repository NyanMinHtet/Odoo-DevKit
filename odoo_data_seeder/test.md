# Odoo Data Seeder - Test Checklist

## Pre-Installation Tests

### Environment Setup
- [ ] Odoo 18.0 environment is running
- [ ] Dependencies installed: `sale`, `sale_management`, `account`, `stock`, `sale_stock`
- [ ] Python `faker` library available (optional): `pip install faker`
- [ ] Test database created (name contains: test, sandbox, dev, stage, or demo)

### Module Installation
- [ ] Module appears in Apps list
- [ ] No installation errors
- [ ] All views load without errors
- [ ] Menu items are visible: Data Seeder > Generation History
- [ ] Menu items are visible: Data Seeder > Generate Data

---

## Functional Tests

### Wizard UI Tests

#### Basic Configuration
- [ ] Wizard opens with default values
- [ ] All fields are editable in draft state
- [ ] Customer count field accepts values (default: 10)
- [ ] Product count field accepts values (default: 5)
- [ ] Order count field accepts values (default: 20)
- [ ] Average lines per order field accepts values (default: 3)

#### Workflow Settings
- [ ] Percent confirmed field (0-100)
- [ ] Percent invoiced field (0-100)
- [ ] Percent paid field (0-100)
- [ ] Percent delivered field (0-100)
- [ ] Date range fields (start and end)
- [ ] Company selection (multi-company enabled)

#### Price Settings
- [ ] Min price field (default: 10.0)
- [ ] Max price field (default: 500.0)
- [ ] Min quantity field (default: 1)
- [ ] Max quantity field (default: 50)
- [ ] Initial stock per product field (default: 25)

#### Inventory Settings
- [ ] Inventory flow toggle can be enabled
- [ ] Warehouse field is available for inventory runs
- [ ] Stock location field is available for inventory runs
- [ ] Storable product ratio field accepts values (0-100)

#### Validation Tests
- [ ] Error shown when using production database
- [ ] Error when customer count > 1000
- [ ] Error when product count > 500
- [ ] Error when order count > 5000
- [ ] Error when end date < start date
- [ ] Error when percentages are outside 0-100
- [ ] Error when initial stock per product is negative
- [ ] Error when inventory flow is enabled without a warehouse

#### Generation Execution
- [ ] Generate button starts process
- [ ] State changes to "Running"
- [ ] Log displays progress
- [ ] Success message on completion
- [ ] Redirects to run record after completion
- [ ] Cancel button works during draft state

---

### Data Generation Tests

#### Customer Generation
- [ ] Correct number of customers created
- [ ] Customers have valid names
- [ ] Customers have email addresses
- [ ] Customers have phone numbers
- [ ] Customers have addresses (street, city, zip)
- [ ] Customer type distribution (individual/company)

#### Product Generation
- [ ] Correct number of products created
- [ ] Products have valid names
- [ ] Products have prices within configured range
- [ ] Products have cost prices
- [ ] Products have product category assigned
- [ ] Default generation keeps products untracked in Inventory
- [ ] Inventory-aware generation creates a mix of tracked and untracked goods

#### Inventory Seeding
- [ ] Tracked goods receive on-hand stock in the selected internal location
- [ ] Untracked goods do not receive stock quants
- [ ] Seeded quantity matches the configured initial stock per product

#### Sale Order Generation
- [ ] Correct number of orders created
- [ ] Orders are assigned to valid customers
- [ ] Orders have dates within configured range
- [ ] Order lines are created per order
- [ ] Order lines have valid products
- [ ] Order lines have quantities within range
- [ ] Order lines have correct prices

---

### Workflow Execution Tests

#### Order Confirmation
- [ ] Correct percentage of orders confirmed
- [ ] Confirmed orders have state = "sale"
- [ ] Unconfirmed orders remain in "draft" state

#### Invoice Creation
- [ ] Invoices created for confirmed orders
- [ ] Correct percentage of orders invoiced
- [ ] Invoices have correct amounts
- [ ] Invoices are posted (state = "posted")

#### Payment Registration
- [ ] Payments registered for invoices
- [ ] Correct percentage of invoices paid
- [ ] Invoice payment_state updated to "paid"
- [ ] Payment amounts match invoice residual

#### Delivery Execution
- [ ] Deliveries are created for confirmed orders containing tracked goods
- [ ] Correct percentage of eligible pickings are validated
- [ ] Delivered pickings move to state = "done"
- [ ] Non-delivered pickings remain open for later processing
- [ ] Generated pickings are linked on the run
- [ ] Generated stock moves are linked on the run
- [ ] Generated stock move lines are linked on the run

---

### Run Management Tests

#### Run Record
- [ ] Run record created after generation
- [ ] Run name is auto-generated with timestamp
- [ ] Configuration snapshot stored
- [ ] Record counts are accurate
- [ ] Execution time is recorded
- [ ] Log contains generation steps
- [ ] Generated records are linked
- [ ] Generated invoice records are linked on the run
- [ ] Generated payment records are linked on the run
- [ ] Generated picking records are linked on the run
- [ ] Generated stock move records are linked on the run
- [ ] Generated stock move line records are linked on the run

#### Run Views
- [ ] List view shows all runs
- [ ] Form view shows run details
- [ ] Form view shows generated invoices
- [ ] Form view shows generated payments
- [ ] Search view filters work (Done, Running, Error)
- [ ] Group by options work (State, Scenario)
- [ ] Status bar displays correct state

---

## Default Scenarios Tests

### Default Sales Scenario
- [ ] Scenario loads with 50 customers, 10 products, 100 orders
- [ ] Workflow percentages: 80% confirmed, 70% invoiced, 60% paid
- [ ] Date range: last 90 days
- [ ] Can be used as template

### Small Test Scenario
- [ ] Scenario loads with 10 customers, 5 products, 20 orders
- [ ] Workflow percentages: 90% confirmed, 80% invoiced, 70% paid
- [ ] Date range: last 30 days
- [ ] Suitable for quick testing

### Large Performance Test
- [ ] Scenario loads with 500 customers, 50 products, 2000 orders
- [ ] Workflow percentages: 75% confirmed, 60% invoiced, 50% paid
- [ ] Date range: last 365 days
- [ ] Tests performance with large dataset

---

## Integration Tests

### Sales Module Integration
- [ ] Sale orders appear in Sales app
- [ ] Order confirmation works with standard Odoo flow
- [ ] Order lines link to correct products

### Accounting Module Integration
- [ ] Invoices appear in Accounting app
- [ ] Invoice posting works with standard Odoo flow
- [ ] Payments register correctly
- [ ] Journal entries are created

### Inventory Module Integration
- [ ] Deliveries appear in Inventory app
- [ ] Reservation uses standard Odoo stock assignment
- [ ] Validation uses standard Odoo transfer flow
- [ ] On-hand stock decreases after delivered pickings are validated

### Partner/Contact Integration
- [ ] Generated customers appear in Contacts app
- [ ] Customer records are properly linked to orders

---

## Performance Tests

### Small Dataset (10 customers, 20 orders)
- [ ] Generation completes in < 10 seconds

### Medium Dataset (50 customers, 100 orders)
- [ ] Generation completes in < 60 seconds

### Large Dataset (500 customers, 2000 orders)
- [ ] Generation completes in < 5 minutes
- [ ] No memory errors
- [ ] Database remains responsive

---

## Edge Case Tests

- [ ] Zero customers/products/orders handled gracefully
- [ ] Minimum values (1 customer, 1 product, 1 order) work
- [ ] Maximum percentage values (100%) work
- [ ] Single day date range works
- [ ] Very large date range works
- [ ] Multi-company isolation works
- [ ] Concurrent generation attempts handled

---

## Regression Tests

After any code changes:
- [ ] All above tests pass
- [ ] No breaking changes to existing functionality
- [ ] Module upgrades work without data loss

---

## Test Environment Cleanup

After testing:
- [ ] Delete generated test data
- [ ] Remove test runs
- [ ] Reset sequences if needed
- [ ] Document any issues found
- [ ] Cleanup blocks runs that already have validated deliveries

---

## Expected Behaviour

### Standard Sales Generation
- [ ] In a test database, the wizard creates customers, products, and sale orders within the configured limits
- [ ] Orders are randomly dated inside the selected date range
- [ ] Confirmation, invoicing, and payment percentages control how much of the workflow is executed
- [ ] The run record stores generated customers, products, orders, invoices, and payments

### Sales To Delivery Generation
- [ ] When inventory flow is disabled, generated goods remain untracked and no stock pickings are created
- [ ] When inventory flow is enabled, generated goods use Odoo 18 tracked goods behavior through `is_storable`
- [ ] The configured storable product ratio controls the mix of tracked and untracked goods
- [ ] Tracked goods receive the configured initial on-hand quantity in the selected internal stock location
- [ ] Confirmed sale orders containing tracked goods create delivery pickings through standard Odoo sales and stock rules
- [ ] The configured delivered percentage controls how many eligible pickings are validated
- [ ] Validated pickings create stock moves and stock move lines that are visible on the run form
- [ ] Delivered quantities reduce stock in the seeded location

### Cleanup Behaviour
- [ ] Cleanup can remove generated customers, products, orders, invoices, payments, and open inventory records in test databases
- [ ] Cleanup clears generated internal stock quantities before deleting tracked products
- [ ] Cleanup refuses to delete runs that already contain validated deliveries and instead requires an explicit stock return flow

---

## Test Report Template

```
Test Date: __________
Tester: __________
Odoo Version: __________
Database: __________

Results:
- Passed: ___ / ___
- Failed: ___ / ___
- Blocked: ___ / ___

Issues Found:
1. _________________________________
2. _________________________________
3. _________________________________

Notes:
_________________________________
_________________________________
```
