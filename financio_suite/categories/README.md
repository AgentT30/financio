# Categories App

## Overview

The Categories app manages transaction categorization with hierarchical structure support. It enables users to organize their financial transactions into meaningful groups for reporting and analytics.

## Design Decisions

### Hierarchical Structure

**Decision**: Support parent-child category relationships with a maximum depth of 3 levels.

**Rationale**:
- Provides flexibility for detailed categorization (e.g., Expense > Shopping > Groceries)
- 3-level limit prevents over-complication and maintains usability
- Enables drill-down reporting from broad categories to specific sub-categories

**Implementation**:
- Self-referential `parent` ForeignKey field
- Depth validation in `clean()` method
- Circular reference prevention

### Default Categories

**Decision**: System default categories owned by admin user, visible to all users.

**Rationale**:
- Provides out-of-box experience for new users
- Standardizes common categories (Groceries, Salary, etc.)
- Users can still create custom categories for their specific needs
- Admin ownership prevents accidental deletion/modification

**Implementation**:
- `is_default` boolean flag
- `user` field points to admin for defaults
- Unique constraint: `(user, name, type)` allows same-named categories per user

### Category Types

**Decision**: Four fixed category types - Income, Expense, Transfer, Fee.

**Rationale**:
- Aligns with accounting principles and transaction flows
- Simplifies reporting (Income vs Expense analysis)
- Transfer type handles inter-account movements
- Fee type separates bank charges from regular expenses

**Types**:
- `income` - Money received (Salary, Interest, Dividends, etc.)
- `expense` - Money spent (Groceries, Rent, Bills, etc.)
- `transfer` - Inter-account movements (not income/expense)
- `fee` - Bank charges, transaction fees, penalties

### Color Coding

**Decision**: Optional hex color code for visual identification.

**Rationale**:
- Improves UI/UX with color-coded charts and lists
- Makes category identification faster
- Validation ensures consistent hex format (#RRGGBB)

### Soft Delete

**Decision**: Use `is_active` flag instead of hard deletion.

**Rationale**:
- Preserves historical data integrity
- Prevents breaking transaction records
- Allows category reactivation if needed
- Supports audit trail requirements

### Field Design

| Field | Type | Purpose |
|-------|------|---------|
| `user` | ForeignKey | Category owner (admin for defaults) |
| `name` | CharField(100) | Category display name |
| `parent` | Self-ForeignKey | Parent category (nullable) |
| `type` | CharField(20) | Income/Expense/Transfer/Fee |
| `color` | CharField(7) | Optional hex color (#RRGGBB) |
| `is_default` | Boolean | System default flag |
| `is_active` | Boolean | Soft delete flag |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last modification timestamp |

## Constraints & Validations

1. **Unique Together**: `(user, name, type)` - Prevents duplicate category names per user per type
2. **Max Depth**: 3 levels enforced in model validation
3. **Type Matching**: Parent and child must have same type
4. **Color Format**: Validated hex code pattern `^#[0-9A-Fa-f]{6}$`
5. **Circular References**: Prevented in `clean()` method

## Key Methods

### `get_full_path()`
Returns hierarchical path string (e.g., "Expense > Shopping > Groceries")

### `get_children()`
Returns all active child categories

### `get_all_descendants()`
Recursively fetches all descendants in the hierarchy

### `can_delete()`
Checks if category is safe to delete (not in use by transactions)

### `get_depth()`
Calculates current depth in hierarchy (1 for root, 2 for child, 3 for grandchild)

## Database Schema

```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id),
    name VARCHAR(100) NOT NULL,
    parent_id BIGINT NULL REFERENCES categories(id),
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense', 'transfer', 'fee')),
    color VARCHAR(7) NULL CHECK (color ~ '^#[0-9A-Fa-f]{6}$'),
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, name, type)
);
```

## Indexes

- `user_id` - Fast user-scoped queries
- `parent_id` - Efficient hierarchy traversal
- `type` - Quick filtering by category type
- `(user_id, is_active)` - Composite for active categories per user

## Usage Examples

### Creating Root Category
```python
category = Category.objects.create(
    user=admin_user,
    name="Shopping",
    type="expense",
    color="#3B82F6",
    is_default=True
)
```

### Creating Child Category
```python
child = Category.objects.create(
    user=user,
    name="Groceries",
    type="expense",
    parent=shopping_category,
    color="#10B981"
)
```

### Getting Full Path
```python
category.get_full_path()  # "Expense > Shopping > Groceries"
```

## Future Enhancements

1. **Budget Integration**: Link categories to monthly budget limits
2. **ML Categorization**: Auto-suggest categories based on transaction description
3. **Category Icons**: Support custom icons alongside colors
4. **Spending Trends**: Category-based spending analytics
5. **Category Rules**: Auto-categorization rules based on merchant/amount

## Related Models

- **Transaction**: Uses Category for classification
- **Budget** (future): Monthly limits per category
- **Report**: Category-based analytics

## Admin Interface

The Django admin provides:
- Color preview with visual swatch
- Hierarchical path display
- Depth level indicator
- Parent category selection
- Filtered lists by type and status
- Search by name and user
