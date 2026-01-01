-- SQL Patch: Update Timezone Information to IST (UTC + 5:30)
-- ----------------------------------------------------------------------------
-- This script shifts all existing timezone-aware timestamps by +5 hours 30 mins.
-- Execute this AFTER setting USE_TZ = False in Django settings.
-- It ensures that data previously stored in UTC now represents IST when read as naive.

-- ============================================================================
-- 1. CORE TRANSACTION & TRANSFER TABLES
-- ============================================================================

-- Transactions
UPDATE transactions SET datetime_ist = datetime_ist + INTERVAL '5 hours 30 minutes';
UPDATE transactions SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE transactions SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';
UPDATE transactions SET deleted_at = deleted_at + INTERVAL '5 hours 30 minutes' WHERE deleted_at IS NOT NULL;

-- Transfers
UPDATE transfers SET datetime_ist = datetime_ist + INTERVAL '5 hours 30 minutes';
UPDATE transfers SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE transfers SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';
UPDATE transfers SET deleted_at = deleted_at + INTERVAL '5 hours 30 minutes' WHERE deleted_at IS NOT NULL;

-- ============================================================================
-- 2. LEDGER TABLES
-- ============================================================================

-- Journal Entries
UPDATE journal_entries SET occurred_at = occurred_at + INTERVAL '5 hours 30 minutes';
UPDATE journal_entries SET created_at = created_at + INTERVAL '5 hours 30 minutes';

-- Postings
UPDATE postings SET created_at = created_at + INTERVAL '5 hours 30 minutes';

-- ============================================================================
-- 3. AUDIT & ACTIVITY LOGS
-- ============================================================================

-- Activity Logs
UPDATE activity_logs SET created_at = created_at + INTERVAL '5 hours 30 minutes';

-- ============================================================================
-- 4. ACCOUNT & CARD TABLES
-- ============================================================================

-- Bank Accounts
UPDATE bank_accounts SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE bank_accounts SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';
UPDATE bank_account_balances SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';

-- Debit Cards
UPDATE debit_cards SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE debit_cards SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';

-- Credit Cards
UPDATE credit_cards SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE credit_cards SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';
UPDATE credit_card_balances SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';

-- ============================================================================
-- 5. INVESTMENT TABLES
-- ============================================================================

-- Brokers
UPDATE brokers SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE brokers SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';

-- Investments
UPDATE investments SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE investments SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';

-- Investment Transactions
UPDATE investment_transactions SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE investment_transactions SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';

-- ============================================================================
-- 6. FIXED DEPOSITS & CATEGORIES
-- ============================================================================

-- Fixed Deposits
UPDATE fixed_deposits SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE fixed_deposits SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';

-- Categories
UPDATE categories SET created_at = created_at + INTERVAL '5 hours 30 minutes';
UPDATE categories SET updated_at = updated_at + INTERVAL '5 hours 30 minutes';

-- ============================================================================
-- 7. SYSTEM & USER TABLES
-- ============================================================================

-- Users (Generic Django Tables)
UPDATE auth_user SET last_login = last_login + INTERVAL '5 hours 30 minutes' WHERE last_login IS NOT NULL;
UPDATE auth_user SET date_joined = date_joined + INTERVAL '5 hours 30 minutes';

-- Recovery Tokens
UPDATE authn_userrecovery SET created_at = created_at + INTERVAL '5 hours 30 minutes';

-- ----------------------------------------------------------------------------
-- Patch Complete
-- ----------------------------------------------------------------------------
