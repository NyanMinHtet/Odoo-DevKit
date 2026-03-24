# Odoo Data Seeder - Test Checklist

## Pre-Installation Tests

### Environment Setup
- [ ] Odoo 18.0 environment is running
- [ ] Dependencies installed: `sale`, `sale_management`, `account`
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
- [ ] Date range fields (start and end)
- [ ] Company selection (multi-company enabled)

#### Price Settings
- [ ] Min price field (default: 10.0)
- [ ] Max price field (default: 500.0)
- [ ] Min quantity field (default: 1)
- [ ] Max quantity field (default: 50)

#### Validation Tests
- [ ] Error shown when using production database
- [ ] Error when customer count > 1000
- [ ] Error when product count > 500
- [ ] Error when order count > 5000
- [ ] Error when end date < start date
- [ ] Error when percentages > 100

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
- [ ] Confirmed orders have state = "sale_order"
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

#### Run Views
- [ ] List view shows all runs
- [ ] Form view shows run details
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
