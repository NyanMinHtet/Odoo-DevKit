# Odoo-DevKit - AI Agent Guidelines

This document provides guidelines for AI agents working with the Odoo-DevKit repository.

## Module Development Guidelines

### Code Style
- Follow Odoo 18.0 conventions
- Use Python 3.10+ features appropriately
- All Python files must have `# -*- coding: utf-8 -*-` header
- Use Odoo's `_` for translations: `from odoo import _, models, fields, api`
- Model names use `sandbox.` prefix for namespacing

### File Organization
```
module_name/
├── __init__.py          # Module imports
├── __manifest__.py      # Module metadata
├── requirements.txt     # Python dependencies
├── models/              # Data models
├── wizard/              # Transient models (wizards)
├── services/            # Business logic services
├── views/               # XML views
├── security/            # Access rules
└── data/                # Static data
```

### Testing Requirements
- All features must have test cases in `test.md`
- Test in sandbox/test databases only
- Validate safety checks before generation

## Dependencies

### odoo_data_seeder
```python
depends = ['base', 'sale', 'sale_management', 'account']
```

### web_swagger_ui
```python
depends = ['base', 'web']
```

## Safety Rules

1. **Database Safety**: Never allow data generation in production databases
   - Check database name for keywords: test, sandbox, dev, stage, demo
   - Raise `ValidationError` if production DB detected

2. **Rate Limits**: Enforce maximum record limits
   - Customers: max 1000
   - Products: max 500
   - Orders: max 5000

3. **Data Cleanup**: Provide cleanup utilities for test data removal

## Version Compatibility

- Target Odoo 18.0 (branch: `18.0`)
- Future versions: maintain separate branches (`17.0`, `18.0`, etc.)
- Manifest version format: `18.0.X.Y.Z`

## Common Patterns

### Model Definition
```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'sandbox.my.model'
    _description = 'My Model Description'

    name = fields.Char(string='Name', required=True)
    state = fields.Selection([...], default='draft')
```

### Wizard Pattern
```python
class MyWizard(models.TransientModel):
    _name = 'sandbox.my.wizard'

    def action_process(self):
        # Validation
        self._check_safety()
        # Processing
        result = self.env['sandbox.service'].do_work()
        # Return action
        return {'type': 'ir.actions.act_window', ...}
```

### Service Pattern
```python
class MyService(models.AbstractModel):
    _name = 'sandbox.my.service'

    def process(self, params):
        # Business logic
        records = self.env['model'].create([...])
        return {'count': len(records)}
```

## XML Guidelines

### Views
- Use `list` instead of `tree` for Odoo 18+
- Always define `id`, `name`, `model`, `arch`
- Use proper widget attributes
- Use True or False for readonly, invisible, etc.. (attributes) never use 1 or 0  
- in 18+ attrs are not use anymore

### Menus
- Hierarchy: root → parent → children
- Use `sequence` for ordering

## Error Handling

```python
from odoo.exceptions import UserError, ValidationError

# For user-facing errors
raise UserError(_("Message for user"))

# For validation failures
raise ValidationError(_("Validation failed"))
```

## Logging

```python
import logging
_logger = logging.getLogger(__name__)

_logger.info("Generation started")
_logger.warning("Large dataset detected")
_logger.error("Generation failed", exc_info=True)
```

## Security

### Access CSV Format
```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model.user,model_res_users,base.group_user,1,1,1,1
```

## Installation Checklist

- [ ] Module in addons path
- [ ] Dependencies installed
- [ ] `pip install -r requirements.txt`
- [ ] Update app list
- [ ] Install module
- [ ] Verify menus appear
- [ ] Run smoke tests

## Agent Tasks

When working on this repo, agents should:

1. **Read existing code** before making changes
2. **Follow existing patterns** in the codebase
3. **Update test.md** when adding new features
4. **Check __manifest__.py** for dependency requirements
5. **Verify XML syntax** (use `list` not `tree` in Odoo 18)
6. **Test safety checks** before any data generation

## Communication

When reporting issues:
- Include Odoo version
- Include module name
- Include error traceback
- Specify if issue is in test or production
