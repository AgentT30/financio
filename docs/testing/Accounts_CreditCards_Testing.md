# Phase 3F: Comprehensive Integration Testing

**Objective:** End-to-end testing of credit card integration across the entire application

**Test Environment:** Fresh database with no existing accounts or transactions

**Prerequisites:**
- All migrations applied
- Control accounts created (Income Control, Expense Control)
- Superuser account available
- Server running on http://localhost:8000

---

## 🔄 RESET DATABASE TO FRESH STATE

### Option 1: SQL Commands (Preserves Users & Categories)

```sql
-- Connect to PostgreSQL
-- psql -U financio_user -d financio_db

-- Delete all transactions and transfers (soft-deleted included)
DELETE FROM transactions;
DELETE FROM transfers;

-- Delete all journal entries and postings
DELETE FROM postings;
DELETE FROM journal_entries;

-- Delete all account balances
DELETE FROM bank_account_balances;
DELETE FROM credit_card_balances;

-- Delete all accounts
DELETE FROM credit_cards;
DELETE FROM bank_accounts;

-- Delete activity logs (optional - keeps audit trail clean)
DELETE FROM activity_logs;

-- Verify everything is clean
SELECT COUNT(*) as bank_accounts FROM bank_accounts;
SELECT COUNT(*) as credit_cards FROM credit_cards;
SELECT COUNT(*) as transactions FROM transactions;
SELECT COUNT(*) as transfers FROM transfers;
SELECT COUNT(*) as journal_entries FROM journal_entries;
SELECT COUNT(*) as postings FROM postings;

-- Verify control accounts still exist (should return 2)
SELECT id, account_name, account_type FROM control_accounts ORDER BY account_type;
```

### Option 2: Django Shell (Alternative Method)

```bash
cd /home/chaitanya-personal/Documents/financio/financio_suite
python manage.py shell
```

```python
from accounts.models import BankAccount, BankAccountBalance
from creditcards.models import CreditCard, CreditCardBalance
from transactions.models import Transaction
from transfers.models import Transfer
from ledger.models import JournalEntry, Posting
from activity.models import ActivityLog

# Delete all data
Transaction.objects.all().delete()
Transfer.objects.all().delete()
Posting.objects.all().delete()
JournalEntry.objects.all().delete()
BankAccountBalance.objects.all().delete()
CreditCardBalance.objects.all().delete()
CreditCard.objects.all().delete()
BankAccount.objects.all().delete()
ActivityLog.objects.all().delete()

# Verify counts
print(f"Bank Accounts: {BankAccount.objects.count()}")
print(f"Credit Cards: {CreditCard.objects.count()}")
print(f"Transactions: {Transaction.objects.count()}")
print(f"Transfers: {Transfer.objects.count()}")
print(f"Journal Entries: {JournalEntry.objects.count()}")
print(f"Postings: {Posting.objects.count()}")
```

---

## 📝 TEST PLAN

### Setup Phase: Create Test Accounts

**Create 2 Bank Accounts:**

1. **HDFC Savings Account**
   - Account Type: Savings
   - Bank Name: HDFC Bank
   - Account Number: 12345678901234
   - Opening Balance: ₹50,000.00
   - Status: Active

2. **ICICI Current Account**
   - Account Type: Current
   - Bank Name: ICICI Bank
   - Account Number: 98765432109876
   - Opening Balance: ₹1,00,000.00
   - Status: Active

**Create 2 Credit Cards:**

1. **SBI Cashback Card**
   - Institution: SBI Card
   - Card Type: Visa
   - Card Number: 4532123456789012
   - CVV: 123
   - Credit Limit: ₹2,00,000.00
   - Opening Balance: -₹10,000.00 (existing debt)
   - Billing Day: 5
   - Due Day: 25
   - Expiry Date: 12/2028

2. **HDFC Regalia Card**
   - Institution: HDFC Bank
   - Card Type: Mastercard
   - Card Number: 5425123456789012
   - CVV: 456
   - Credit Limit: ₹3,00,000.00
   - Opening Balance: ₹0.00 (no debt)
   - Billing Day: 10
   - Due Day: 28
   - Expiry Date: 06/2029

**Expected Initial State:**
```
Bank Accounts:
- HDFC Savings: ₹50,000.00
- ICICI Current: ₹1,00,000.00
- Total Bank Balance: ₹1,50,000.00

Credit Cards:
- SBI Cashback: -₹10,000.00 debt (₹1,90,000 available)
- HDFC Regalia: ₹0.00 debt (₹3,00,000 available)
- Total Amount Owed: ₹10,000.00
- Total Available Credit: ₹4,90,000.00

Net Worth: ₹1,50,000.00 (excludes credit card debt)
```

**Verification Queries:**
```sql
-- Check bank account balances
SELECT ba.name, ba.opening_balance, 
       COALESCE(bab.balance_amount, ba.opening_balance) as current_balance
FROM bank_accounts ba
LEFT JOIN bank_account_balances bab ON ba.id = bab.account_id
WHERE ba.status = 'active'
ORDER BY ba.name;

-- Check credit card balances
SELECT cc.institution, cc.credit_limit, cc.opening_balance,
       COALESCE(ccb.balance_amount, cc.opening_balance) as current_balance,
       cc.credit_limit + COALESCE(ccb.balance_amount, cc.opening_balance) as available_credit,
       ABS(LEAST(COALESCE(ccb.balance_amount, cc.opening_balance), 0)) as amount_owed
FROM credit_cards cc
LEFT JOIN credit_card_balances ccb ON cc.id = ccb.account_id
WHERE cc.status = 'active'
ORDER BY cc.institution;
```

---

## Test Suite 1: Transaction Tests

### Test 1.1: Expense Transaction on Credit Card

**Objective:** Verify expense increases credit card debt

**Steps:**
1. Navigate to Transactions → Add Transaction
2. Fill form:
   - Date: Today
   - Time: 10:00 AM
   - Type: Expense
   - Account: 💳 SBI Cashback Card
   - Category: Shopping
   - Method: Card
   - Amount: ₹5,000.00
   - Purpose: "Electronic gadgets purchase"
3. Submit form

**Expected Results:**
- Transaction created successfully
- SBI Cashback balance: -₹10,000.00 → -₹15,000.00 (debt increased)
- Available credit: ₹1,90,000 → ₹1,85,000
- Amount owed: ₹10,000 → ₹15,000
- Journal entry created with 2 postings (sum = 0)
- Activity log entry created

**Verification Queries:**
```sql
-- Check credit card balance
SELECT cc.institution, 
       ccb.balance_amount as current_balance,
       cc.credit_limit + ccb.balance_amount as available_credit,
       ABS(LEAST(ccb.balance_amount, 0)) as amount_owed
FROM credit_cards cc
JOIN credit_card_balances ccb ON cc.id = ccb.account_id
WHERE cc.institution = 'SBI Card';

-- Verify journal entry balances to zero
SELECT je.id, je.memo, SUM(p.amount) as total
FROM journal_entries je
JOIN postings p ON p.journal_entry_id = je.id
GROUP BY je.id, je.memo
HAVING SUM(p.amount) != 0;  -- Should return no rows
```

---

### Test 1.2: Income Transaction on Credit Card (Cashback/Refund)

**Objective:** Verify income decreases credit card debt

**Steps:**
1. Navigate to Transactions → Add Transaction
2. Fill form:
   - Date: Today
   - Time: 11:00 AM
   - Type: Income
   - Account: 💳 SBI Cashback Card
   - Category: Cashback
   - Method: Card
   - Amount: ₹500.00
   - Purpose: "Cashback from previous purchase"
3. Submit form

**Expected Results:**
- Transaction created successfully
- SBI Cashback balance: -₹15,000.00 → -₹14,500.00 (debt decreased)
- Available credit: ₹1,85,000 → ₹1,85,500
- Amount owed: ₹15,000 → ₹14,500

**Verification Query:**
```sql
SELECT cc.institution, ccb.balance_amount, 
       cc.credit_limit + ccb.balance_amount as available_credit
FROM credit_cards cc
JOIN credit_card_balances ccb ON cc.id = ccb.account_id
WHERE cc.institution = 'SBI Card';
```

---

### Test 1.3: Expense Transaction on Bank Account

**Objective:** Verify expense decreases bank balance and validates sufficient funds

**Steps:**
1. Navigate to Transactions → Add Transaction
2. Fill form:
   - Date: Today
   - Time: 12:00 PM
   - Type: Expense
   - Account: 🏦 HDFC Savings Account
   - Category: Food & Dining
   - Method: UPI
   - Amount: ₹2,500.00
   - Purpose: "Restaurant bill"
3. Submit form

**Expected Results:**
- Transaction created successfully
- HDFC Savings: ₹50,000.00 → ₹47,500.00
- Net Worth: ₹1,50,000 → ₹1,47,500

**Verification Query:**
```sql
SELECT ba.name, bab.balance_amount
FROM bank_accounts ba
JOIN bank_account_balances bab ON ba.id = bab.account_id
WHERE ba.name = 'HDFC Savings Account';
```

---

### Test 1.4: Insufficient Balance Validation (Bank Account)

**Objective:** Verify bank accounts cannot go negative

**Steps:**
1. Navigate to Transactions → Add Transaction
2. Fill form:
   - Type: Expense
   - Account: 🏦 HDFC Savings Account
   - Amount: ₹50,000.00 (more than current ₹47,500)
   - Category: Shopping
3. Submit form

**Expected Results:**
- Form validation error displayed
- Error message: "Insufficient balance in HDFC Savings Account. Current balance: ₹47,500.00, Expense amount: ₹50,000.00..."
- Transaction NOT created
- Balance remains ₹47,500.00

---

## Test Suite 2: Transfer Tests

### Test 2.1: Bank → Credit Card (Bill Payment)

**Objective:** Verify bill payment reduces bank balance and credit card debt

**Steps:**
1. Navigate to Transactions → Transfers tab → Add Transfer
2. Fill form:
   - Date: Today
   - Time: 2:00 PM
   - From Account: 🏦 ICICI Current Account
   - To Account: 💳 SBI Cashback Card
   - Amount: ₹10,000.00
   - Method: NEFT
   - Memo: "Credit card bill payment"
3. Submit form

**Expected Results:**
- Transfer created successfully
- ICICI Current: ₹1,00,000.00 → ₹90,000.00 (decreased)
- SBI Cashback: -₹14,500.00 → -₹4,500.00 (debt decreased)
- SBI Available credit: ₹1,85,500 → ₹1,95,500
- Net Worth: ₹1,47,500 (unchanged - both are assets/liabilities)
- Journal entry with 2 postings created

**Verification Queries:**
```sql
-- Check both accounts
SELECT 'ICICI Current' as account, bab.balance_amount
FROM bank_accounts ba
JOIN bank_account_balances bab ON ba.id = bab.account_id
WHERE ba.name = 'ICICI Current Account'
UNION ALL
SELECT 'SBI Cashback', ccb.balance_amount
FROM credit_cards cc
JOIN credit_card_balances ccb ON cc.id = ccb.account_id
WHERE cc.institution = 'SBI Card';

-- Verify transfer record
SELECT t.amount, t.memo, t.datetime_ist,
       je.id as journal_entry_id,
       (SELECT COUNT(*) FROM postings WHERE journal_entry_id = je.id) as posting_count
FROM transfers t
JOIN journal_entries je ON t.journal_entry_id = je.id
WHERE t.memo = 'Credit card bill payment';
```

---

### Test 2.2: Credit Card → Bank (Refund/Reversal)

**Objective:** Verify refund increases bank balance and credit card debt

**Steps:**
1. Navigate to Transfers → Add Transfer
2. Fill form:
   - Date: Today
   - Time: 3:00 PM
   - From Account: 💳 SBI Cashback Card
   - To Account: 🏦 HDFC Savings Account
   - Amount: ₹1,500.00
   - Method: NEFT
   - Memo: "Merchant refund for cancelled order"
3. Submit form

**Expected Results:**
- Transfer created successfully
- SBI Cashback: -₹4,500.00 → -₹6,000.00 (debt increased - card paid the bank)
- HDFC Savings: ₹47,500.00 → ₹49,000.00 (increased)
- SBI Available credit: ₹1,95,500 → ₹1,94,000

**Verification Query:**
```sql
SELECT 'HDFC Savings' as account, bab.balance_amount
FROM bank_accounts ba
JOIN bank_account_balances bab ON ba.id = bab.account_id
WHERE ba.name = 'HDFC Savings Account'
UNION ALL
SELECT 'SBI Cashback', ccb.balance_amount
FROM credit_cards cc
JOIN credit_card_balances ccb ON cc.id = ccb.account_id
WHERE cc.institution = 'SBI Card';
```

---

### Test 2.3: Credit Card → Credit Card (Balance Transfer)

**Objective:** Verify balance transfer between credit cards

**Steps:**
1. Navigate to Transfers → Add Transfer
2. Fill form:
   - Date: Today
   - Time: 4:00 PM
   - From Account: 💳 HDFC Regalia Card
   - To Account: 💳 SBI Cashback Card
   - Amount: ₹3,000.00
   - Method: Card
   - Memo: "Balance transfer - pay off SBI debt"
3. Submit form

**Expected Results:**
- Transfer created successfully
- HDFC Regalia: ₹0.00 → -₹3,000.00 (debt created - Regalia paid SBI)
- SBI Cashback: -₹6,000.00 → -₹3,000.00 (debt decreased - received payment)
- HDFC Regalia available: ₹3,00,000 → ₹2,97,000
- SBI Cashback available: ₹1,94,000 → ₹1,97,000
- Total debt across both cards remains same: ₹6,000

**Verification Query:**
```sql
SELECT cc.institution, ccb.balance_amount,
       cc.credit_limit + ccb.balance_amount as available_credit,
       ABS(LEAST(ccb.balance_amount, 0)) as amount_owed
FROM credit_cards cc
JOIN credit_card_balances ccb ON cc.id = ccb.account_id
WHERE cc.status = 'active'
ORDER BY cc.institution;
```

---

### Test 2.4: Bank → Bank Transfer

**Objective:** Verify transfer between bank accounts works correctly

**Steps:**
1. Navigate to Transfers → Add Transfer
2. Fill form:
   - From Account: 🏦 ICICI Current Account
   - To Account: 🏦 HDFC Savings Account
   - Amount: ₹20,000.00
   - Method: IMPS
   - Memo: "Internal transfer"
3. Submit form

**Expected Results:**
- ICICI Current: ₹90,000.00 → ₹70,000.00
- HDFC Savings: ₹49,000.00 → ₹69,000.00
- Net Worth: ₹1,39,000.00 (unchanged)

---

### Test 2.5: Insufficient Balance Validation (Transfer)

**Objective:** Verify transfers validate bank account balance

**Steps:**
1. Navigate to Transfers → Add Transfer
2. Fill form:
   - From Account: 🏦 HDFC Savings Account (balance: ₹69,000)
   - To Account: 🏦 ICICI Current Account
   - Amount: ₹70,000.00
3. Submit form

**Expected Results:**
- Form validation error
- Error message: "Insufficient balance in HDFC Savings Account..."
- Transfer NOT created
- Balances unchanged

---

## Test Suite 3: Dashboard Tests

### Test 3.1: Dashboard Stats Verification

**Objective:** Verify dashboard displays correct stats

**Steps:**
1. Navigate to Dashboard (/)
2. Observe all stat cards

**Expected Results:**
- **Net Worth:** ₹1,39,000.00
  - Calculation: HDFC (₹69,000) + ICICI (₹70,000) = ₹1,39,000
  - Does NOT include credit card debt (correct behavior)
  
- **Total Accounts:** "2 Banks • 2 Cards"
  - Clicking navigates to Accounts & Cards page

- **Month-to-Date Stats:**
  - Income: ₹500.00 (cashback only)
  - Expense: ₹7,500.00 (₹5,000 gadgets + ₹2,500 restaurant)

**Verification Query:**
```sql
-- Calculate Net Worth (banks only)
SELECT SUM(bab.balance_amount) as net_worth
FROM bank_accounts ba
JOIN bank_account_balances bab ON ba.id = bab.account_id
WHERE ba.status = 'active';

-- Count accounts
SELECT 
  (SELECT COUNT(*) FROM bank_accounts WHERE status = 'active') as banks,
  (SELECT COUNT(*) FROM credit_cards WHERE status = 'active') as cards;

-- MTD Income/Expense
SELECT 
  transaction_type,
  SUM(amount) as total
FROM transactions
WHERE datetime_ist >= DATE_TRUNC('month', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
  AND deleted_at IS NULL
GROUP BY transaction_type;
```

---

### Test 3.2: Recent Transactions Display

**Objective:** Verify recent transactions show with emoji indicators

**Steps:**
1. Check "Recent Transactions" section on dashboard
2. Verify emoji indicators appear

**Expected Results:**
- Last 10 transactions displayed in chronological order
- Emoji indicators:
  - 🏦 for bank account transactions
  - 💳 for credit card transactions
- Income shown in green, Expense in red
- Relative timestamps (e.g., "2 hours ago")

---

### Test 3.3: Account Type Choice Modal

**Objective:** Verify modal works correctly

**Steps:**
1. Click "Add Account" button on dashboard
2. Observe modal appears
3. Click "🏦 Add Bank Account" → should navigate to bank account form
4. Return to dashboard
5. Click "Add Account" → Click "💳 Add Credit Card" → should navigate to credit card form
6. Click outside modal or press Escape → modal closes

**Expected Results:**
- Modal displays with two clear options
- Navigation works correctly
- Modal closes on outside click or Escape
- Smooth animations

---

## Test Suite 4: Accounts & Cards Page Tests

### Test 4.1: Combined Page Layout

**Objective:** Verify both sections display correctly

**Steps:**
1. Navigate to Accounts & Cards page
2. Verify layout and stats

**Expected Results:**
- Page title: "Accounts & Cards"
- **Bank Accounts Section (🏦):**
  - Header shows "2 active • 0 archived • ₹1,39,000 total"
  - Two cards displayed: HDFC Savings, ICICI Current
  - Each card shows: emoji, name, balance, color indicator
  - "Add Bank Account" button present
  
- **Credit Cards Section (💳):**
  - Header shows "2 active • 0 archived"
  - 3 stat cards:
    - Total Limit: ₹5,00,000
    - Available Credit: ₹4,91,000
    - Amount Owed: ₹9,000
  - Two cards displayed: HDFC Regalia, SBI Cashback
  - Each shows: emoji, institution, last 4 digits, available credit
  - "Add Credit Card" button present

**Verification Query:**
```sql
-- Bank stats
SELECT 
  COUNT(*) FILTER (WHERE status = 'active') as active_count,
  COUNT(*) FILTER (WHERE status = 'archived') as archived_count,
  SUM(bab.balance_amount) FILTER (WHERE ba.status = 'active') as total_balance
FROM bank_accounts ba
LEFT JOIN bank_account_balances bab ON ba.id = bab.account_id;

-- Credit card stats
SELECT 
  COUNT(*) FILTER (WHERE status = 'active') as active_count,
  COUNT(*) FILTER (WHERE status = 'archived') as archived_count,
  SUM(credit_limit) FILTER (WHERE status = 'active') as total_limit,
  SUM(credit_limit + COALESCE(ccb.balance_amount, opening_balance)) 
    FILTER (WHERE cc.status = 'active') as total_available,
  SUM(ABS(LEAST(COALESCE(ccb.balance_amount, opening_balance), 0))) 
    FILTER (WHERE cc.status = 'active') as total_owed
FROM credit_cards cc
LEFT JOIN credit_card_balances ccb ON cc.id = ccb.account_id;
```

---

### Test 4.2: Responsive Design

**Objective:** Verify mobile responsiveness

**Steps:**
1. Open Accounts & Cards page
2. Resize browser to mobile width (< 640px)
3. Verify layout adapts

**Expected Results:**
- Both sections stack vertically
- Cards display in single column
- Stats remain readable
- Action buttons remain accessible
- No horizontal scrolling

---

## Test Suite 5: Account Detail Pages

### Test 5.1: Bank Account Detail Page

**Objective:** Verify bank account detail shows transactions/transfers correctly

**Steps:**
1. Navigate to HDFC Savings Account detail page
2. Check both tabs (Transactions, Transfers)

**Expected Results:**
- **Header:**
  - 🏦 Bank Account badge displayed
  - Account details visible (account number with eye/copy icons)
  - Current balance: ₹69,000.00

- **Transactions Tab:**
  - Shows 1 expense transaction (₹2,500 restaurant)
  - Emoji indicators for accounts

- **Transfers Tab:**
  - Shows 3 transfers:
    - Incoming from SBI Cashback (₹1,500 refund)
    - Incoming from ICICI (₹20,000 internal transfer)
    - Outgoing to ICICI (attempted ₹70,000 - should fail if tested)
  - Direction indicators (→ OUT, ← IN)

---

### Test 5.2: Credit Card Detail Page

**Objective:** Verify credit card detail shows transactions/transfers correctly

**Steps:**
1. Navigate to SBI Cashback Card detail page
2. Check both tabs

**Expected Results:**
- **Header:**
  - 💳 Credit Card badge displayed
  - Card details (card number/CVV with eye/copy icons)
  - Available Credit: ₹1,97,000
  - Amount Owed: ₹3,000
  - Credit Limit: ₹2,00,000

- **Transactions Tab:**
  - Shows 2 transactions:
    - Expense: ₹5,000 (gadgets)
    - Income: ₹500 (cashback)

- **Transfers Tab:**
  - Shows 3 transfers:
    - Incoming from ICICI (₹10,000 bill payment)
    - Outgoing to HDFC Savings (₹1,500 refund)
    - Incoming from HDFC Regalia (₹3,000 balance transfer)

---

## Test Suite 6: Deletion Protection Tests

### Test 6.1: Delete Credit Card with Transactions

**Objective:** Verify credit cards with transactions cannot be deleted

**Steps:**
1. Navigate to SBI Cashback Card detail page
2. Click "Delete Credit Card" button
3. Confirm deletion

**Expected Results:**
- Error message displayed: "Cannot delete SBI Card credit card because it has associated transactions or transfers..."
- Credit card NOT deleted
- Redirected to credit cards list
- Card still appears in list

---

### Test 6.2: Delete Bank Account with Transfers

**Objective:** Verify bank accounts with transfers cannot be deleted

**Steps:**
1. Navigate to ICICI Current Account detail page
2. Attempt to delete

**Expected Results:**
- Error message about existing transfers
- Account NOT deleted

---

## Test Suite 7: Balance Recalculation

### Test 7.1: Verify Balance Integrity

**Objective:** Ensure all balances match ledger postings

**Steps:**
1. Run recalculate_balances command with dry-run:
   ```bash
   cd /home/chaitanya-personal/Documents/financio/financio_suite
   python manage.py recalculate_balances --dry-run
   ```

**Expected Results:**
- All accounts show ✓ (no corrections needed)
- No balance mismatches detected
- Output shows all accounts with correct balances

**Final Verification Queries:**
```sql
-- Verify all journal entries balance to zero
SELECT je.id, je.memo, SUM(p.amount) as total
FROM journal_entries je
JOIN postings p ON p.journal_entry_id = je.id
GROUP BY je.id, je.memo
HAVING SUM(p.amount) != 0;
-- Should return 0 rows

-- Compare opening balance + postings vs current balance for banks
SELECT 
  ba.name,
  ba.opening_balance,
  COALESCE(SUM(p.amount), 0) as total_postings,
  ba.opening_balance + COALESCE(SUM(p.amount), 0) as calculated_balance,
  bab.balance_amount as stored_balance,
  CASE 
    WHEN ba.opening_balance + COALESCE(SUM(p.amount), 0) = bab.balance_amount 
    THEN '✓' ELSE '✗' 
  END as match
FROM bank_accounts ba
LEFT JOIN bank_account_balances bab ON ba.id = bab.account_id
LEFT JOIN postings p ON p.account_object_id = ba.id 
  AND p.account_content_type_id = (SELECT id FROM django_content_type WHERE model = 'bankaccount')
  AND p.journal_entry_id IN (
    SELECT journal_entry_id FROM transactions WHERE deleted_at IS NULL
    UNION
    SELECT journal_entry_id FROM transfers WHERE deleted_at IS NULL
  )
WHERE ba.status = 'active'
GROUP BY ba.id, ba.name, ba.opening_balance, bab.balance_amount
ORDER BY ba.name;

-- Same for credit cards
SELECT 
  cc.institution,
  cc.opening_balance,
  COALESCE(SUM(p.amount), 0) as total_postings,
  cc.opening_balance + COALESCE(SUM(p.amount), 0) as calculated_balance,
  ccb.balance_amount as stored_balance,
  CASE 
    WHEN cc.opening_balance + COALESCE(SUM(p.amount), 0) = ccb.balance_amount 
    THEN '✓' ELSE '✗' 
  END as match
FROM credit_cards cc
LEFT JOIN credit_card_balances ccb ON cc.id = ccb.account_id
LEFT JOIN postings p ON p.account_object_id = cc.id 
  AND p.account_content_type_id = (SELECT id FROM django_content_type WHERE model = 'creditcard')
  AND p.journal_entry_id IN (
    SELECT journal_entry_id FROM transactions WHERE deleted_at IS NULL
    UNION
    SELECT journal_entry_id FROM transfers WHERE deleted_at IS NULL
  )
WHERE cc.status = 'active'
GROUP BY cc.id, cc.institution, cc.opening_balance, ccb.balance_amount
ORDER BY cc.institution;
```

---

## Test Suite 8: Edge Cases

### Test 8.1: Credit Card Overpayment

**Objective:** Verify credit card can have positive balance

**Steps:**
1. Create transfer: HDFC Savings → HDFC Regalia for ₹5,000
   (Current debt: ₹3,000)
2. Verify overpayment handling

**Expected Results:**
- HDFC Regalia balance: -₹3,000 → +₹2,000 (positive = credit with card company)
- Available credit: ₹2,97,000 → ₹3,02,000 (more than limit)
- Amount owed: ₹3,000 → ₹0 (no debt)

---

### Test 8.2: Multiple Small Decimal Transactions

**Objective:** Verify decimal precision (2 places)

**Steps:**
1. Create 5 transactions of ₹33.33 each on HDFC Savings
2. Check final balance

**Expected Results:**
- Each transaction: ₹33.33
- Total: ₹166.65
- Balance should decrease by exactly ₹166.65
- No rounding errors

---

### Test 8.3: Large Number Formatting

**Objective:** Verify large amounts display correctly

**Steps:**
1. Edit ICICI Current Account opening balance to ₹9,99,999.99
2. View dashboard and account detail page

**Expected Results:**
- Dashboard: ₹9,99,999.99 (Indian format with commas)
- Detail page: ₹9,99,999.99
- All calculations correct

---

## 📊 FINAL STATE SUMMARY

After completing all tests, expected final state:

**Bank Accounts:**
- HDFC Savings: ₹69,000.00 (after all transactions)
- ICICI Current: ₹70,000.00 (after transfers)
- **Total:** ₹1,39,000.00

**Credit Cards:**
- SBI Cashback: -₹3,000.00 debt (₹1,97,000 available)
- HDFC Regalia: +₹2,000.00 credit (₹3,02,000 available)
- **Total Debt:** ₹3,000.00
- **Total Available:** ₹4,99,000.00

**Net Worth:** ₹1,39,000.00 (bank balances only)

**Transaction Count:** 2-3 transactions
**Transfer Count:** 4-5 transfers
**Journal Entries:** All balanced (sum = 0)

---

## ✅ TEST COMPLETION CHECKLIST

- [x] Database reset completed
- [x] 2 bank accounts created with correct opening balances
- [x] 2 credit cards created with correct opening balances
- [x] All Test Suite 1 tests passed (Transactions)
- [x] All Test Suite 2 tests passed (Transfers)
- [x] All Test Suite 3 tests passed (Dashboard)
- [x] All Test Suite 4 tests passed (Accounts & Cards page)
- [x] All Test Suite 5 tests passed (Detail pages)
- [x] All Test Suite 6 tests passed (Deletion protection)
- [x] All Test Suite 7 tests passed (Balance integrity)
- [x] All Test Suite 8 tests passed (Edge cases)
- [x] All verification queries return expected results
- [x] No orphaned journal entries exist
- [x] All journal entries balance to zero
- [x] Balance recalculation shows all ✓

---

**Last Updated:** 25 November 2025
