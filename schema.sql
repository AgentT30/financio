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
COMMENT ON COLUMN categories.is_default IS 'True if system default category owned by admin';
COMMENT ON COLUMN categories.is_active IS 'Active status for soft delete/archive';

-- ============================================================================
-- ACCOUNTS TABLE
-- ============================================================================
-- Stores user financial accounts with encrypted sensitive data

CREATE TABLE IF NOT EXISTS accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('savings', 'credit_card', 'wallet', 'cash', 'fd', 'loan')),
    
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
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_acc_user_status ON accounts(user_id, status);
CREATE INDEX idx_acc_type ON accounts(account_type);

-- Update trigger
CREATE TRIGGER update_accounts_updated_at 
    BEFORE UPDATE ON accounts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE accounts IS 'User financial accounts with encrypted sensitive data';
COMMENT ON COLUMN accounts.account_number IS 'Full account number (encrypted via Django)';
COMMENT ON COLUMN accounts.account_number_last4 IS 'Last 4 digits for display (unencrypted)';
COMMENT ON COLUMN accounts.picture IS 'Path to uploaded account picture/icon';
COMMENT ON COLUMN accounts.color IS 'Hex color code for account theme (e.g., #3B82F6)';

-- ============================================================================
-- ACCOUNT BALANCES TABLE (Materialized)
-- ============================================================================
-- Fast balance lookups, updated atomically with ledger postings

CREATE TABLE IF NOT EXISTS account_balances (
    account_id BIGINT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
    balance_amount NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    last_posting_id BIGINT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Update trigger
CREATE TRIGGER update_account_balances_updated_at 
    BEFORE UPDATE ON account_balances 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE account_balances IS 'Materialized account balances for fast lookups';
COMMENT ON COLUMN account_balances.balance_amount IS 'Current balance calculated from ledger';
COMMENT ON COLUMN account_balances.last_posting_id IS 'Last posting that updated this balance';
