-- Financio Database Schema
-- PostgreSQL 16
-- Generated: 2025-11-16
-- Timezone: All timestamps stored in UTC, displayed in IST (Asia/Kolkata)

-- ============================================================================
-- CATEGORIES TABLE
-- ============================================================================
-- Stores transaction categories with hierarchical structure (max 3 levels)
-- Default categories owned by admin user, users can create custom categories

CREATE TABLE IF NOT EXISTS categories (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    parent_id BIGINT NULL REFERENCES categories(id) ON DELETE SET NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense', 'transfer', 'fee')),
    color VARCHAR(7) NULL,
    icon VARCHAR(50) NULL,
    description TEXT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_category_per_user UNIQUE (user_id, name, type),
    CONSTRAINT valid_color_format CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Indexes for performance
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_type ON categories(type);
CREATE INDEX idx_cat_user_active ON categories(user_id, is_active);

-- Update trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_categories_updated_at 
BEFORE UPDATE ON categories 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE categories IS 'Transaction categories with hierarchical structure (max 3 levels)';
COMMENT ON COLUMN categories.user_id IS 'Owner of category (admin for system defaults)';
COMMENT ON COLUMN categories.name IS 'Category name (e.g., Groceries, Salary)';
COMMENT ON COLUMN categories.parent_id IS 'Parent category for hierarchical organization';
COMMENT ON COLUMN categories.type IS 'Category type: income, expense, transfer, or fee';
COMMENT ON COLUMN categories.color IS 'Hex color code for UI visualization (optional)';
COMMENT ON COLUMN categories.icon IS 'Icon name or emoji for category (e.g., 🍔, 🚗, 💰)';
COMMENT ON COLUMN categories.description IS 'Optional description for the category';
COMMENT ON COLUMN categories.is_default IS 'True if system default category owned by admin';
COMMENT ON COLUMN categories.is_active IS 'Active status for soft delete/archive';

-- ============================================================================
-- BANK ACCOUNTS TABLE
-- ============================================================================
-- Stores user bank accounts with encrypted sensitive data
-- Inherits from BaseAccount abstract model in Django

CREATE TABLE IF NOT EXISTS bank_accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    account_type VARCHAR(20) NOT NULL DEFAULT 'savings' CHECK (account_type IN ('savings', 'checking', 'current', 'salary')),
    
    -- Institution details
    institution VARCHAR(100) NULL,
    branch_name VARCHAR(100) NULL,
    ifsc_code VARCHAR(11) NULL CHECK (ifsc_code IS NULL OR ifsc_code ~ '^[A-Z]{4}0[A-Z0-9]{6}$'),
    customer_id VARCHAR(50) NULL,
    
    -- Account identifiers (account_number stored encrypted via Django)
    account_number BYTEA NULL,  -- Encrypted field stored as binary
    account_number_last4 VARCHAR(4) NULL,
    
    -- Financial information
    opening_balance NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    
    -- Dates and status
    opened_on DATE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    
    -- Additional information
    notes TEXT NULL,
    
    -- Visual customization
    picture VARCHAR(255) NULL,  -- Path to uploaded picture
    color VARCHAR(7) NULL CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'),
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_account_per_user UNIQUE (user_id, institution, account_number_last4)
);

-- Indexes for performance
CREATE INDEX idx_bank_acc_user_id ON bank_accounts(user_id);
CREATE INDEX idx_bank_acc_user_status ON bank_accounts(user_id, status);
CREATE INDEX idx_bank_acc_type ON bank_accounts(account_type);

-- Update trigger
CREATE TRIGGER update_bank_accounts_updated_at 
    BEFORE UPDATE ON bank_accounts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE bank_accounts IS 'User bank accounts with encrypted sensitive data (inherits from BaseAccount)';
COMMENT ON COLUMN bank_accounts.account_type IS 'Type of bank account: savings, checking, or salary';
COMMENT ON COLUMN bank_accounts.account_number IS 'Full account number (encrypted via Django)';
COMMENT ON COLUMN bank_accounts.account_number_last4 IS 'Last 4 digits for display (unencrypted)';
COMMENT ON COLUMN bank_accounts.picture IS 'Path to uploaded account picture/icon';
COMMENT ON COLUMN bank_accounts.color IS 'Hex color code for account theme (e.g., #3B82F6)';

-- ============================================================================
-- BANK ACCOUNT BALANCES TABLE (Materialized)
-- ============================================================================
-- Fast balance lookups, updated atomically with ledger postings

CREATE TABLE IF NOT EXISTS bank_account_balances (
    account_id BIGINT PRIMARY KEY REFERENCES bank_accounts(id) ON DELETE CASCADE,
    balance_amount NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    last_posting_id BIGINT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Update trigger
CREATE TRIGGER update_bank_account_balances_updated_at 
    BEFORE UPDATE ON bank_account_balances 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE bank_account_balances IS 'Materialized bank account balances for fast lookups';
COMMENT ON COLUMN bank_account_balances.balance_amount IS 'Current balance calculated from ledger';
COMMENT ON COLUMN bank_account_balances.last_posting_id IS 'Last posting that updated this balance';

-- ============================================================================
-- ACTIVITY LOGS TABLE
-- ============================================================================
-- Audit log for tracking user actions (CRUD operations)
-- Uses content_type for GenericForeignKey to reference any model

CREATE TABLE IF NOT EXISTS activity_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL CHECK (action IN ('create', 'update', 'delete', 'archive', 'activate')),
    
    -- GenericForeignKey fields
    content_type_id INTEGER NOT NULL REFERENCES django_content_type(id) ON DELETE CASCADE,
    object_id INTEGER NOT NULL,
    
    -- Object representation (stored for reference even if object is deleted)
    object_repr VARCHAR(200) NOT NULL,
    
    -- Change details
    changes JSONB NULL,
    
    -- Metadata
    ip_address INET NULL,
    user_agent TEXT NULL,
    
    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_activity_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_action ON activity_logs(action);
CREATE INDEX idx_activity_user_time ON activity_logs(user_id, created_at);
CREATE INDEX idx_activity_object ON activity_logs(content_type_id, object_id);
CREATE INDEX idx_activity_created_at ON activity_logs(created_at);

-- Comments
COMMENT ON TABLE activity_logs IS 'Audit log for tracking user actions (CRUD operations)';
COMMENT ON COLUMN activity_logs.user_id IS 'User who performed the action';
COMMENT ON COLUMN activity_logs.action IS 'Type of action: create, update, delete, archive, activate';
COMMENT ON COLUMN activity_logs.content_type_id IS 'Django content type ID for GenericForeignKey';
COMMENT ON COLUMN activity_logs.object_id IS 'ID of the object being acted upon';
COMMENT ON COLUMN activity_logs.object_repr IS 'String representation of object (preserved even if object deleted)';
COMMENT ON COLUMN activity_logs.changes IS 'JSON field containing field-level changes for updates';
COMMENT ON COLUMN activity_logs.ip_address IS 'IP address of user when action was performed';
COMMENT ON COLUMN activity_logs.user_agent IS 'Browser user agent string';

-- ============================================================================
-- CONTROL ACCOUNTS TABLE
-- ============================================================================
-- Synthetic ledger accounts for double-entry bookkeeping
-- Only 2 instances: Income Control and Expense Control

CREATE TABLE IF NOT EXISTS control_accounts (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    account_type VARCHAR(20) NOT NULL UNIQUE CHECK (account_type IN ('income', 'expense')),
    description TEXT NOT NULL
);

-- Comments
COMMENT ON TABLE control_accounts IS 'Synthetic ledger accounts for double-entry bookkeeping (only 2 instances)';
COMMENT ON COLUMN control_accounts.name IS 'Control account name (e.g., Income Control Account)';
COMMENT ON COLUMN control_accounts.account_type IS 'Type: income or expense';
COMMENT ON COLUMN control_accounts.description IS 'Description of the control account purpose';

-- ============================================================================
-- JOURNAL ENTRIES TABLE
-- ============================================================================
-- Journal entries for double-entry bookkeeping
-- Each entry contains 2+ postings that must sum to zero

CREATE TABLE IF NOT EXISTS journal_entries (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    occurred_at TIMESTAMPTZ NOT NULL,
    memo TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_journal_user_id ON journal_entries(user_id);
CREATE INDEX idx_journal_occurred_at ON journal_entries(occurred_at);
CREATE INDEX idx_journal_user_time ON journal_entries(user_id, occurred_at);

-- Comments
COMMENT ON TABLE journal_entries IS 'Journal entries for double-entry bookkeeping';
COMMENT ON COLUMN journal_entries.user_id IS 'Owner of the journal entry';
COMMENT ON COLUMN journal_entries.occurred_at IS 'When the financial event occurred (IST)';
COMMENT ON COLUMN journal_entries.memo IS 'Description of the transaction';
COMMENT ON COLUMN journal_entries.created_at IS 'When this entry was recorded (IST)';

-- ============================================================================
-- POSTINGS TABLE
-- ============================================================================
-- Individual debit/credit entries within a journal entry
-- Uses content_type for GenericForeignKey to reference any account type

CREATE TABLE IF NOT EXISTS postings (
    id BIGSERIAL PRIMARY KEY,
    journal_entry_id BIGINT NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    
    -- GenericForeignKey to account (BankAccount, ControlAccount, etc.)
    account_content_type_id INTEGER NOT NULL REFERENCES django_content_type(id) ON DELETE PROTECT,
    account_object_id INTEGER NOT NULL,
    
    -- Amount (signed: positive = debit, negative = credit)
    amount NUMERIC(18, 2) NOT NULL,
    
    -- Posting type
    posting_type VARCHAR(10) NOT NULL CHECK (posting_type IN ('debit', 'credit')),
    
    -- Currency
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    
    -- Optional memo
    memo TEXT NULL,
    
    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_debit_amount CHECK (posting_type != 'debit' OR amount >= 0),
    CONSTRAINT valid_credit_amount CHECK (posting_type != 'credit' OR amount <= 0)
);

-- Indexes for performance
CREATE INDEX idx_posting_journal ON postings(journal_entry_id);
CREATE INDEX idx_posting_account ON postings(account_content_type_id, account_object_id);
CREATE INDEX idx_posting_type ON postings(posting_type);

-- Comments
COMMENT ON TABLE postings IS 'Individual debit/credit entries within journal entries';
COMMENT ON COLUMN postings.journal_entry_id IS 'Parent journal entry';
COMMENT ON COLUMN postings.account_content_type_id IS 'Django content type ID for GenericForeignKey to account';
COMMENT ON COLUMN postings.account_object_id IS 'ID of the account (BankAccount, ControlAccount, etc.)';
COMMENT ON COLUMN postings.amount IS 'Signed amount: positive for debit, negative for credit';
COMMENT ON COLUMN postings.posting_type IS 'Debit or Credit (for reporting clarity)';
COMMENT ON COLUMN postings.currency IS 'Currency code (fixed to INR for V1)';
COMMENT ON COLUMN postings.memo IS 'Optional posting-specific memo (can override journal entry memo)';

-- ============================================================================
-- TRANSACTIONS TABLE
-- ============================================================================
-- User-facing transaction model for income/expense tracking
-- Each transaction links to a JournalEntry in the ledger

CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    -- Transaction details
    datetime_ist TIMESTAMPTZ NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    amount NUMERIC(18, 2) NOT NULL CHECK (amount > 0),
    
    -- Account reference (GenericForeignKey)
    account_content_type_id INTEGER NOT NULL REFERENCES django_content_type(id) ON DELETE PROTECT,
    account_object_id INTEGER NOT NULL,
    
    -- Payment method
    method_type VARCHAR(20) NOT NULL CHECK (method_type IN ('upi', 'card', 'netbanking', 'cash', 'wallet', 'imps_neft_rtgs', 'cheque', 'other')),
    
    -- Description and category
    purpose TEXT NOT NULL,
    category_id BIGINT NULL REFERENCES categories(id) ON DELETE PROTECT,
    
    -- Link to journal entry (one-to-one)
    journal_entry_id BIGINT NULL UNIQUE REFERENCES journal_entries(id) ON DELETE PROTECT,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    deleted_at TIMESTAMPTZ NULL
);

-- Indexes for performance
CREATE INDEX idx_txn_user_id ON transactions(user_id);
CREATE INDEX idx_txn_datetime_ist ON transactions(datetime_ist);
CREATE INDEX idx_txn_user_time ON transactions(user_id, datetime_ist);
CREATE INDEX idx_txn_user_type ON transactions(user_id, transaction_type);
CREATE INDEX idx_txn_category ON transactions(category_id);
CREATE INDEX idx_txn_account ON transactions(account_content_type_id, account_object_id);
CREATE INDEX idx_txn_deleted_at ON transactions(deleted_at);
CREATE INDEX idx_txn_method_type ON transactions(method_type);

-- Update trigger
CREATE TRIGGER update_transactions_updated_at 
    BEFORE UPDATE ON transactions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE transactions IS 'User-facing transaction model for income/expense tracking';
COMMENT ON COLUMN transactions.user_id IS 'Owner of the transaction';
COMMENT ON COLUMN transactions.datetime_ist IS 'Date and time of transaction (IST)';
COMMENT ON COLUMN transactions.transaction_type IS 'Type of transaction: income or expense';
COMMENT ON COLUMN transactions.amount IS 'Transaction amount (always positive)';
COMMENT ON COLUMN transactions.account_content_type_id IS 'Django content type ID for GenericForeignKey to account';
COMMENT ON COLUMN transactions.account_object_id IS 'ID of the account (BankAccount, CreditCard, etc.)';
COMMENT ON COLUMN transactions.method_type IS 'Payment method: upi, card, netbanking, cash, wallet, imps_neft_rtgs, cheque, other';
COMMENT ON COLUMN transactions.purpose IS 'Description or purpose of transaction';
COMMENT ON COLUMN transactions.category_id IS 'Transaction category (must match transaction type)';
COMMENT ON COLUMN transactions.journal_entry_id IS 'Linked journal entry in ledger (one-to-one)';
COMMENT ON COLUMN transactions.created_at IS 'When transaction was recorded (IST)';
COMMENT ON COLUMN transactions.updated_at IS 'Last update timestamp (IST)';
COMMENT ON COLUMN transactions.deleted_at IS 'Soft delete timestamp (NULL = active)';

-- ============================================================================
-- TRANSFERS TABLE
-- ============================================================================
-- Money transfers between two accounts
-- Each transfer creates a journal entry with two postings (debit from_account, credit to_account)

CREATE TABLE IF NOT EXISTS transfers (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    
    -- Transfer details
    datetime_ist TIMESTAMPTZ NOT NULL,
    amount NUMERIC(18, 2) NOT NULL CHECK (amount > 0),
    
    -- From account reference (GenericForeignKey)
    from_account_content_type_id INTEGER NOT NULL REFERENCES django_content_type(id) ON DELETE PROTECT,
    from_account_object_id INTEGER NOT NULL,
    
    -- To account reference (GenericForeignKey)
    to_account_content_type_id INTEGER NOT NULL REFERENCES django_content_type(id) ON DELETE PROTECT,
    to_account_object_id INTEGER NOT NULL,
    
    -- Payment method
    method_type VARCHAR(20) NOT NULL CHECK (method_type IN ('upi', 'card', 'netbanking', 'cash', 'wallet', 'imps_neft_rtgs', 'cheque', 'other')),
    
    -- Description/memo
    memo TEXT NOT NULL,
    
    -- Link to journal entry (one-to-one)
    journal_entry_id BIGINT NULL UNIQUE REFERENCES journal_entries(id) ON DELETE PROTECT,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    deleted_at TIMESTAMPTZ NULL,
    
    -- Constraints
    CONSTRAINT different_accounts CHECK (
        from_account_content_type_id != to_account_content_type_id OR 
        from_account_object_id != to_account_object_id
    )
);

-- Indexes for performance
CREATE INDEX idx_transfer_user_id ON transfers(user_id);
CREATE INDEX idx_transfer_datetime_ist ON transfers(datetime_ist);
CREATE INDEX idx_transfer_user_date ON transfers(user_id, datetime_ist);
CREATE INDEX idx_transfer_from_account ON transfers(from_account_content_type_id, from_account_object_id);
CREATE INDEX idx_transfer_to_account ON transfers(to_account_content_type_id, to_account_object_id);
CREATE INDEX idx_transfer_user_deleted ON transfers(user_id, deleted_at);
CREATE INDEX idx_transfer_deleted_at ON transfers(deleted_at);

-- Update trigger
CREATE TRIGGER update_transfers_updated_at 
    BEFORE UPDATE ON transfers 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE transfers IS 'Money transfers between two accounts with double-entry ledger integration';
COMMENT ON COLUMN transfers.user_id IS 'Owner of the transfer';
COMMENT ON COLUMN transfers.datetime_ist IS 'Date and time of transfer (IST)';
COMMENT ON COLUMN transfers.amount IS 'Transfer amount (always positive)';
COMMENT ON COLUMN transfers.from_account_content_type_id IS 'Django content type ID for GenericForeignKey to source account';
COMMENT ON COLUMN transfers.from_account_object_id IS 'ID of the source account';
COMMENT ON COLUMN transfers.to_account_content_type_id IS 'Django content type ID for GenericForeignKey to destination account';
COMMENT ON COLUMN transfers.to_account_object_id IS 'ID of the destination account';
COMMENT ON COLUMN transfers.method_type IS 'Transfer method: upi, card, netbanking, cash, wallet, imps_neft_rtgs, cheque, other';
COMMENT ON COLUMN transfers.memo IS 'Transfer description/notes';
COMMENT ON COLUMN transfers.journal_entry_id IS 'Linked journal entry in ledger (one-to-one)';
COMMENT ON COLUMN transfers.created_at IS 'When transfer was recorded (IST)';
COMMENT ON COLUMN transfers.updated_at IS 'Last update timestamp (IST)';
COMMENT ON COLUMN transfers.deleted_at IS 'Soft delete timestamp (NULL = active)';
