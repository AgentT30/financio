# Accounts App

## Overview

The Accounts app manages all user financial accounts including banks, credit cards, wallets, cash, fixed deposits, and loans. It serves as the foundation for transaction tracking and balance management with encrypted sensitive data storage.

## Design Decisions

### Multiple Account Types

**Decision**: Support 6 distinct account types within a single model.

**Rationale**:
- Unified interface for all financial accounts
- Simplifies balance aggregation and net worth calculation
- Reduces code duplication
- Each type shares core attributes (name, balance, status)
- Type-specific details handled via optional fields or related models

**Supported Types**:
1. `savings` - Bank savings accounts
2. `credit_card` - Credit card accounts
3. `wallet` - Digital wallets (PayTM, PhonePe, Amazon Pay, etc.)
4. `cash` - Physical cash on hand
5. `fd` - Fixed deposits (linked to FD model)
6. `loan` - Loan accounts (linked to Loan model)

### Encrypted Account Numbers

**Decision**: Store full account numbers encrypted, auto-extract last 4 digits for display.

**Rationale**:
- **Security**: Full numbers never stored in plain text
- **Usability**: Last 4 digits sufficient for visual identification
- **Compliance**: Meets data protection standards
- **Transparency**: Users can view full numbers when needed via decryption

**Implementation**:
- Uses `django-encrypted-model-fields` with Fernet encryption
- `account_number`: Encrypted full number (EncryptedCharField)
- `account_number_last4`: Auto-extracted unencrypted last 4 digits
- Encryption key stored in environment variable (`FIELD_ENCRYPTION_KEY`)

### Materialized Balance Table

**Decision**: Separate `AccountBalance` model for fast balance lookups.

**Rationale**:
- **Performance**: Avoid expensive SUM queries on postings table
- **Consistency**: Single source of truth updated atomically with ledger
- **Scalability**: Handles thousands of transactions per account efficiently
- **Audit**: Tracks last posting that updated balance

**Implementation**:
- OneToOne relationship with Account
- Updated atomically when ledger postings are created
- Read-only in admin to prevent manual tampering

### Institution Details

**Decision**: Store branch name, IFSC code, and customer ID as separate optional fields.

**Rationale**:
- **Structured Data**: Enables validation (e.g., IFSC format)
- **Queryable**: Can filter/search by branch or institution
- **Future Features**: IFSC lookup, branch-wise reports
- **Better UX**: Proper form fields vs free-text notes

**Fields**:
- `institution`: Bank/institution name (free text)
- `branch_name`: Branch location
- `ifsc_code`: 11-character code with format validation
- `customer_id`: Bank's customer ID for user

### Visual Customization

**Decision**: Support custom pictures and color themes per account.

**Rationale**:
- **UX Enhancement**: Visual differentiation in UI lists
- **Personalization**: Users can upload bank logos or custom icons
- **Quick Recognition**: Color coding speeds up account identification
- **Dashboard Appeal**: Improved visual hierarchy in dashboard

**Fields**:
- `picture`: ImageField for account icons (stored in `media/account_pictures/`)
- `color`: Hex color code with validation (#RRGGBB format)

### Uniqueness Constraint

**Decision**: Unique together on `(user, institution, account_number_last4)`.

**Rationale**:
- Prevents duplicate account entries per user
- Allows same account number across different users (privacy)
- Institution + last4 combo is practically unique per user
- Handles cases where full number isn't stored

### Soft Delete via Status

**Decision**: Use `status` field (active/archived) instead of deletion.

**Rationale**:
- Preserves transaction history
- Allows account reactivation
- Supports closed account reporting
- Maintains referential integrity

## Field Design

| Field | Type | Purpose |
|-------|------|---------|
| `user` | ForeignKey(User) | Account owner |
| `name` | CharField(100) | Display name/nickname |
| `account_type` | CharField(20) | savings/credit_card/wallet/cash/fd/loan |
| `institution` | CharField(100) | Bank/institution name (optional) |
| `branch_name` | CharField(100) | Branch name (optional) |
| `ifsc_code` | CharField(11) | IFSC code with validation (optional) |
| `customer_id` | CharField(50) | Customer ID (optional) |
| `account_number` | EncryptedCharField | Full number encrypted (optional) |
| `account_number_last4` | CharField(4) | Last 4 digits auto-extracted (read-only) |
| `opening_balance` | Decimal(18,2) | Initial balance |
| `currency` | CharField(3) | Fixed to INR for V1 |
| `opened_on` | DateField | Account opening date (optional) |
| `status` | CharField(20) | active/archived |
| `notes` | TextField | Free-form notes (optional) |
| `picture` | ImageField | Account icon/logo (optional) |
| `color` | CharField(7) | Hex color theme (optional) |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last modification timestamp |

## Constraints & Validations

1. **Unique Together**: `(user, institution, account_number_last4)` - Prevents duplicates
2. **IFSC Format**: `^[A-Z]{4}0[A-Z0-9]{6}$` - 11 characters, 5th char is 0
3. **Currency**: Fixed to INR for V1 (validated in `clean()`)
4. **Color Format**: `^#[0-9A-Fa-f]{6}$` - Valid hex code
5. **Status**: Must be 'active' or 'archived'

## Key Methods

### `get_masked_account_number()`
Returns masked format: `****1234`

### `get_current_balance()`
Fetches from AccountBalance model, falls back to opening_balance if no balance record exists.

### `archive()` / `activate()`
Soft delete/restore account by updating status field.

### `can_delete()`
Checks if account has transactions (will implement with Transaction model).

### `save()`
Auto-extracts last 4 digits from account_number before saving.

## Database Schema

```sql
CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id),
    name VARCHAR(100) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    institution VARCHAR(100),
    branch_name VARCHAR(100),
    ifsc_code VARCHAR(11) CHECK (ifsc_code ~ '^[A-Z]{4}0[A-Z0-9]{6}$'),
    customer_id VARCHAR(50),
    account_number BYTEA,  -- Encrypted
    account_number_last4 VARCHAR(4),
    opening_balance NUMERIC(18,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'INR',
    opened_on DATE,
    status VARCHAR(20) DEFAULT 'active',
    notes TEXT,
    picture VARCHAR(255),
    color VARCHAR(7) CHECK (color ~ '^#[0-9A-Fa-f]{6}$'),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, institution, account_number_last4)
);

CREATE TABLE account_balances (
    account_id BIGINT PRIMARY KEY REFERENCES accounts(id),
    balance_amount NUMERIC(18,2) DEFAULT 0.00,
    last_posting_id BIGINT,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

## Indexes

- `user_id` - Fast user-scoped queries
- `(user_id, status)` - Active accounts per user
- `account_type` - Filter by account type

## Security Considerations

### Encryption Key Management

- **Environment Variable**: `FIELD_ENCRYPTION_KEY` stored in `.env` file
- **Never Committed**: `.env` is in `.gitignore`
- **Production**: Use secure key management service
- **Key Rotation**: Changing key makes old data unreadable (plan carefully)

### Data Access

- **Encrypted at Rest**: Account numbers stored as binary encrypted data
- **Decrypted on Read**: Automatic decryption when accessing `account_number` field
- **Display Safety**: Only last 4 digits shown in listings
- **Full Access**: Available when user explicitly views account details

## AccountBalance Model

### Purpose
Materialized view of account balance for performance.

### Update Strategy
1. Transaction/posting created → Ledger module updates balance atomically
2. Uses database transaction for consistency
3. Records `last_posting_id` for audit trail

### Read-Only Admin
- Cannot manually add/delete balance records
- Prevents data corruption
- Balance updates only via ledger operations

## Usage Examples

### Creating Account
```python
account = Account.objects.create(
    user=user,
    name="HDFC Savings",
    account_type="savings",
    institution="HDFC Bank",
    branch_name="MG Road",
    ifsc_code="HDFC0001234",
    account_number="1234567890123456",  # Encrypted automatically
    opening_balance=10000.00,
    color="#FF6B35",
    opened_on=date(2023, 1, 1)
)
# account_number_last4 is auto-set to "3456"
```

### Getting Balance
```python
balance = account.get_current_balance()  # From AccountBalance model
```

### Archiving Account
```python
account.archive()  # Sets status to 'archived'
```

### Masked Display
```python
masked = account.get_masked_account_number()  # "****3456"
```

## Future Enhancements

1. **Multi-Currency**: Support for USD, EUR, etc. with exchange rates
2. **Account Linking**: Link external accounts via APIs (Plaid, Yodlee)
3. **Auto-Sync**: Fetch transactions from bank APIs
4. **Interest Calculation**: Auto-calculate savings account interest
5. **Credit Limit Tracking**: For credit card accounts
6. **Joint Accounts**: Multi-user account ownership
7. **Account Templates**: Quick setup for common bank accounts

## Integration Points

### Related Models (Future)
- **FD**: OneToOne link for Fixed Deposit details
- **Loan**: OneToOne link for Loan details
- **Transaction**: ForeignKey to Account for all transactions
- **Transfer**: References both source and destination Accounts
- **Trade**: References funding Account for investments

### Ledger Integration
- Account balance updated via `Posting` records
- Double-entry bookkeeping ensures accuracy
- AccountBalance materialized from ledger postings

## Admin Interface

Provides:
- Masked account number display
- Current balance from AccountBalance
- Color preview with visual swatch
- Picture upload interface
- Bulk actions for archiving/activating
- Search by name, institution, customer ID
- Filter by type, status, institution
- Optimized queries with `select_related` and `prefetch_related`
