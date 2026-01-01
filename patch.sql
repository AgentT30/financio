-- SQL Patch: Final IST Naive Conversion
-- ----------------------------------------------------------------------------
-- 1. CONVERT ALL TIMESTAMPTZ COLUMNS TO NAIVE TIMESTAMP
-- ----------------------------------------------------------------------------

ALTER TABLE transactions ALTER COLUMN datetime_ist TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE transactions ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE transactions ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE transactions ALTER COLUMN deleted_at TYPE TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE transfers ALTER COLUMN datetime_ist TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE transfers ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE transfers ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE transfers ALTER COLUMN deleted_at TYPE TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE journal_entries ALTER COLUMN occurred_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE journal_entries ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE postings ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE activity_logs ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE bank_accounts ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE bank_accounts ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE bank_account_balances ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE credit_cards ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE credit_cards ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE credit_card_balances ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE categories ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE categories ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE fixed_deposits ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE fixed_deposits ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;

-- Investment Tables (Django Migration managed)
ALTER TABLE brokers ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE brokers ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE investments ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE investments ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE investment_transactions ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE investment_transactions ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;

-- Auth & System
ALTER TABLE auth_user ALTER COLUMN last_login TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE auth_user ALTER COLUMN date_joined TYPE TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE authn_userrecovery ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;

-- ----------------------------------------------------------------------------
-- 2. SYNCHRONIZE DATA VALUES (Fill UTC gaps)
-- ----------------------------------------------------------------------------

-- Fix record #2 specifically
UPDATE transactions SET datetime_ist = created_at WHERE id = 2;

-- Shift any remaining UTC values (14:xx) to match the IST clock (19:xx)
UPDATE transactions SET datetime_ist = datetime_ist + INTERVAL '5 hours 30 minutes' WHERE datetime_ist < created_at - INTERVAL '1 hour';
UPDATE transfers SET datetime_ist = datetime_ist + INTERVAL '5 hours 30 minutes' WHERE datetime_ist < created_at - INTERVAL '1 hour';
UPDATE journal_entries SET occurred_at = occurred_at + INTERVAL '5 hours 30 minutes' WHERE occurred_at < created_at - INTERVAL '1 hour';
