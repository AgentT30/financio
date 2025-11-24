# Financio - Development TODO

## ✅ Completed
- [x] Django project setup with all apps
- [x] Database models: Categories (hierarchical, 3-level max)
- [x] Database models: Accounts (6 types with encryption) - **LEGACY, TO BE REFACTORED**
- [x] Database models: AccountBalance (materialized table) - **LEGACY, TO BE REFACTORED**
- [x] Migrations created and applied
- [x] Superuser created
- [x] Authentication: Login page
- [x] Authentication: Signup page
- [x] Authentication: Password reset request page
- [x] Authentication: Logout functionality
- [x] Logo integration (light/dark variants)
- [x] Favicon setup
- [x] Theme toggle (dark/light mode)
- [x] Base templates with TailwindCSS
- [x] Dashboard UI (responsive, toggleable sidebar)
- [x] Dashboard stats cards (Net Worth, Total Accounts, Categories)
- [x] Dashboard accounts snapshot with balances
- [x] Dashboard quick action buttons
- [x] Categories: List/tree view (responsive)
- [x] Categories: Create category form
- [x] Categories: Edit category
- [x] Categories: Delete category with validation
- [x] Categories: Title case storage
- [x] Accounts: List page (responsive card grid) - **LEGACY, TO BE REFACTORED**
- [x] Accounts: Create account form (dashboard button functional) - **LEGACY, TO BE REFACTORED**
- [x] Accounts: Edit account details - **LEGACY, TO BE REFACTORED**
- [x] Accounts: Delete account with validation - **LEGACY, TO BE REFACTORED**
- [x] Accounts: Account detail page with information - **LEGACY, TO BE REFACTORED**
- [x] Accounts: Upload/update account picture - **LEGACY, TO BE REFACTORED**
- [x] Accounts: Color customization - **LEGACY, TO BE REFACTORED**
- [x] Accounts: Toggle status (active/archived) - **LEGACY, TO BE REFACTORED**
- [x] Accounts: Name and institution stored as-is (no automatic title case) - **LEGACY, TO BE REFACTORED**
- [x] **Account Refactoring Plan Created** (docs/ACCOUNT_REFACTORING_PLAN.md)
- [x] **FDD Updated** with specialized account types
- [x] **SDD Updated** with new ERD and table structure
- [x] **Account Refactoring - Simplified Approach Implemented:**
  - [x] Created BaseAccount abstract model in core/models.py
  - [x] Renamed Account → BankAccount (inherits from BaseAccount)
  - [x] Renamed AccountBalance → BankAccountBalance
  - [x] Updated table names: accounts → bank_accounts, account_balances → bank_account_balances
  - [x] Limited account types to bank-specific: savings, checking, current, salary
  - [x] Created empty apps: creditcards/, wallets/, cash/ (not in INSTALLED_APPS yet)
  - [x] Updated all views, forms, admin references to use BankAccount
  - [x] Data migration created and applied (converted 'Savings' → 'savings')
  - [x] Updated schema.sql to reflect new structure
  - [x] Migration guide created (MIGRATION_COMMANDS.md)
- [x] **Account Detail Page Enhancements:**
  - [x] Eye icon to toggle account number visibility (masked ↔ full)
  - [x] Copy icon to copy account number to clipboard
  - [x] Visual feedback on copy (checkmark icon)
- [x] **Navigation Improvements:**
  - [x] Created shared header/sidebar component (templates/includes/header_sidebar.html)
  - [x] Added hamburger menu for mobile/desktop navigation
  - [x] Implemented collapsible sidebar with overlay for mobile
  - [x] Active menu item highlighting
  - [x] Updated all account pages to use shared navigation
  - [x] Consistent header and sidebar across Dashboard, Accounts, Categories
- [x] **Button Text Fix:** Create Account button now displays text properly

## 🚧 In Progress
- [ ] **Future: Implement specialized account models** in creditcards/, wallets/, cash/ apps
  - Status: Foundation complete, empty apps created
  - Next: Implement when needed (later milestone)

## 📋 TODO - Priority Order

### 🔥 Account Model Foundation - ✅ COMPLETED
**Objective:** Create foundation for specialized account types

**Phase 1: Preparation** ✅
- [x] Create detailed refactoring plan
- [x] Update FDD with specialized account structures
- [x] Update SDD with new ERD and tables
- [x] Document risks and mitigation strategies

**Phase 2: Foundation Implementation** ✅
- [x] Create BaseAccount abstract model in core/models.py
- [x] Refactor Account → BankAccount (inherits BaseAccount)
- [x] Refactor AccountBalance → BankAccountBalance
- [x] Update table names in schema.sql
- [x] Limit ACCOUNT_TYPE_CHOICES to bank types only (savings, checking, current, salary)
- [x] Create empty apps: creditcards/, wallets/, cash/
- [x] Update all views to use BankAccount
- [x] Update all forms to use BankAccountForm
- [x] Update admin to use BankAccountAdmin
- [x] Create and apply migrations
- [x] Data migration: convert capitalized types to lowercase
- [x] Remove .title() normalization from save method
- [x] Update dashboard to use BankAccount

**Phase 3: Credit Cards Implementation** ✅ COMPLETED
- [x] Implement CreditCard model in creditcards/ app
  - [x] Created CreditCard model inheriting from BaseAccount
  - [x] Added encrypted card_number and cvv fields (EncryptedCharField)
  - [x] Mandatory fields: institution, credit_limit, billing_day, due_day, expiry_date
  - [x] Card type choices: Visa, Mastercard, RuPay, American Express
  - [x] Methods: available_credit(), amount_owed(), can_delete()
- [x] Created CreditCardBalance materialized table
- [x] Added 'creditcards' to INSTALLED_APPS
- [x] Created migrations and applied successfully
- [x] Updated schema.sql with credit_cards and credit_card_balances tables
- [x] **CRUD Operations:**
  - [x] CreditCardForm with validation (card number 13-19 digits, CVV 3-4 digits)
  - [x] creditcard_list view with stats (total limit, available credit, amount owed)
  - [x] creditcard_create view with balance initialization
  - [x] creditcard_edit view with opening balance sync
  - [x] creditcard_delete view with ProtectedError handling
  - [x] creditcard_detail view with transaction/transfer history tabs
  - [x] creditcard_toggle_status view
- [x] **Templates:**
  - [x] creditcard_list.html (responsive grid, 3 stat cards, card type icons)
  - [x] creditcard_form.html (multi-section form, card number auto-formatting)
  - [x] creditcard_detail.html (eye/copy icons for sensitive data, tabbed history)
  - [x] creditcard_confirm_delete.html
- [x] **UI Enhancements:**
  - [x] Card number auto-formatting with spaces (JavaScript, frontend only)
  - [x] Eye/copy icons for card number and CVV viewing
  - [x] CVV field preservation in edit mode (shows ••• placeholder)
  - [x] Institution name stored as-is (no auto-capitalization)
  - [x] Ordinal suffixes for Billing/Due Day (1st, 2nd, 3rd, etc.)
  - [x] 2 decimal places for Available Credit and Amount Owed
- [x] **Bug Fixes:**
  - [x] Opening balance synchronization with CreditCardBalance
  - [x] Form styling consistency with BankAccountForm
- [x] URL patterns configured in creditcards/urls.py
- [x] Admin interface registered (CreditCardAdmin)

**Phase 3A-3G: Credit Card Integration** 🚧 IN PROGRESS
See detailed breakdown below in "Credit Card Integration - Full System Integration" section

**Phase 4: Future - Other Specialized Apps** 🔜
- [ ] Implement DigitalWallet model in wallets/ app
- [ ] Implement CashAccount model in cash/ app

---

### 1️⃣ Categories (CRUD) - ✅ COMPLETED
- [x] Categories list/tree view (desktop + mobile responsive)
- [x] Create category form
- [x] Edit category
- [x] Delete category (with subcategory checks)
- [x] Category color picker
- [x] Category icon support
- [ ] Seed default categories for new users
- [ ] Category reassignment when deleting (for transactions - pending transaction model)


### 2️⃣ Accounts (CRUD) - ✅ COMPLETED
- [x] Accounts list page (desktop + mobile responsive)
- [x] Create new account form (dashboard button functional)
- [x] Account type selection with icons
- [x] Edit account details
- [x] Delete account (with transaction dependency checks)
- [x] Account details page with transaction history placeholder
- [x] Upload/update account picture
- [x] Account balance display and calculations
- [x] Account status (active/inactive)
- [x] Account number visibility toggle (eye icon)
- [x] Copy account number to clipboard functionality
- [x] Shared header/sidebar navigation on all account pages
- [x] Name field stored as-is (no automatic title case)

### 3️⃣ Transactions & Ledger System - 🚧 IN PROGRESS
**CURRENT PHASE: Foundation - Models & Services**

**Specifications:**
- Transaction type: `income`/`expense` enum (user-friendly)
- Payment methods: UPI, Card, Netbanking, Cash, Wallet, IMPS, NEFT, RTGS, Cheque, Other
- Datetime storage: IST (via Django TIME_ZONE='Asia/Kolkata')
- GenericForeignKey: Polymorphic account references (BankAccount now, others later)
- Double-entry ledger: Separate Income Control & Expense Control accounts
- Materialized balances: Atomic updates via BankAccountBalance

**Phase 1A: Activity Logging Foundation** ✅ COMPLETED
- [x] Create ActivityLog model (activity/models.py)
  - GenericForeignKey for tracking any model
  - JSON field for change tracking
  - IP address and user agent capture
  - IST timestamp
- [x] Create activity logging utilities (activity/utils.py)
  - log_activity() helper function
  - track_model_changes() for field-level diffs
- [x] Update activity/admin.py with ActivityLogAdmin
- [x] Create migration for activity app
- [x] Test: python manage.py makemigrations activity && migrate activity

**Phase 1B: Ledger Models (Core Double-Entry)** ✅ COMPLETED
- [x] Create ControlAccount model (ledger/models.py)
  - Income Control Account (synthetic ledger account)
  - Expense Control Account (synthetic ledger account)
  - Only 2 instances should exist
- [x] Create JournalEntry model (ledger/models.py)
  - Links to user, occurred_at (IST), memo
  - validate_balanced() method (postings sum to zero)
  - One-to-one with Transaction model
- [x] Create Posting model (ledger/models.py)
  - GenericForeignKey to any account type
  - Signed amount (positive=debit, negative=credit)
  - posting_type enum (debit/credit)
  - Links to JournalEntry
- [x] Create LedgerService class (ledger/services.py)
  - create_simple_entry() for income/expense transactions
  - create_transfer_entry() for account transfers
  - _update_account_balance() for atomic balance updates
- [x] Update ledger/admin.py with model admins
- [x] Create management command: create_control_accounts.py
- [x] Create migration for ledger app
- [x] Test: python manage.py makemigrations ledger && migrate ledger
- [x] Test: python manage.py create_control_accounts
- [x] Update schema.sql with new tables (activity_logs, control_accounts, journal_entries, postings)

**Phase 1C: Transaction Model** ✅ COMPLETED
- [x] Create Transaction model (transactions/models.py)
  - datetime_ist, transaction_type (income/expense), amount (positive)
  - GenericForeignKey to account (BankAccount, etc.)
  - method_type enum (UPI, Card, Netbanking, Cash, Wallet, IMPS/NEFT/RTGS, Cheque, Other)
  - purpose (TextField), category (FK to Category)
  - journal_entry (OneToOne to JournalEntry)
  - Soft delete via deleted_at
  - Validation: amount > 0, category type matches transaction type
- [x] Update Transaction form (transactions/forms.py)
  - Date/time fields for IST datetime
  - Account selector (currently BankAccount only)
  - Category dropdown (filtered by type)
  - Method type selector
  - Amount and purpose fields
- [x] Update transactions/admin.py with TransactionAdmin
- [x] Create migration for transactions app
- [x] Test: python manage.py makemigrations transactions && migrate transactions
- [x] Update schema.sql with transactions table
- [x] Database constraint update: Consolidated IMPS/NEFT/RTGS payment methods

**Phase 1D: Transaction Views & Templates** ✅ COMPLETED
- [x] Create transaction_list view (transactions/views.py)
  - Filter by date range, account, category, type
  - Pagination (20 per page)
  - Search by purpose
  - Exclude soft-deleted
- [x] Create transaction_create view (transactions/views.py)
  - Use LedgerService to create JournalEntry + Postings
  - Update BankAccountBalance atomically
  - Log activity via activity.utils.log_activity()
  - Redirect to transaction list on success
- [x] Create transaction_edit view (transactions/views.py)
  - Load existing transaction
  - Update transaction + journal entry
  - Log activity with field changes
- [x] Create transaction_delete view (transactions/views.py)
  - Soft delete (set deleted_at)
  - Log activity
- [x] Create transaction list template (templates/transactions/transaction_list.html)
  - Responsive table/card layout
  - Filter panel (date, account, category, type)
  - Search bar
  - Pagination controls
  - Income/Expense visual distinction
- [x] Create transaction form template (templates/transactions/transaction_form.html)
  - Date/time picker
  - Account selector
  - Category dropdown (filtered by JS based on transaction type)
  - Custom CategorySelectWidget for data-type attributes
  - Amount input with validation
  - Purpose textarea
- [x] Create transaction confirm delete template (templates/transactions/transaction_confirm_delete.html)
- [x] Update transactions/urls.py with URL patterns
- [x] Update main urls.py to include transactions URLs
- [x] Update LedgerService.create_simple_entry() signature to match view usage
- [x] Fix category dropdown rendering with proper data-type attributes
- [x] Capitalize category labels (remove "Type: " prefix)

**Phase 1E: Transfers Implementation** ✅ COMPLETED
- [x] Create Transfer model (transfers/models.py)
  - Links two accounts via GenericForeignKey
  - Amount, method_type, memo, datetime_ist
  - OneToOne with JournalEntry
  - Soft delete support
  - Validation: user ownership, from ≠ to
  - skip_validation parameter in save()
- [x] Create TransferForm (transfers/forms.py)
  - Converted from ModelForm to regular Form
  - Custom from_account/to_account ModelChoiceFields
  - Validation: from ≠ to, amount > 0
  - clean() method for datetime and account setup
- [x] Create transfer views (transfers/views.py)
  - transfer_create using LedgerService.create_transfer_entry()
  - Unpacks tuple return: (journal_entry, from_balance, to_balance)
  - skip_validation=True on save
  - Activity logging with correct parameters (obj, request)
  - transfer_delete (soft delete with balance reversal)
- [x] Create transfer templates
  - transfer_form.html with "Add Transaction Instead" toggle
  - transfer_confirm_delete.html
- [x] Update transfers/urls.py and main urls.py
- [x] Update transfers/admin.py with TransferAdmin
- [x] Create and apply migrations
- [x] Update schema.sql with transfers table
- [x] **Unified Transactions/Transfers View:**
  - [x] Modified transaction_list view for dual-mode operation (transactions/transfers)
  - [x] Query parameter-based view switching (?view=transfers)
  - [x] Conditional filtering and data display
  - [x] Tab navigation in transaction_list.html
  - [x] Separate action buttons (Add Transaction + Add Transfer)
  - [x] Transfer-specific filters (from_account, to_account)
  - [x] Conditional table rendering for transactions vs transfers
  - [x] Mobile card views for both types
  - [x] Updated pagination to preserve view parameter
  - [x] Updated empty states for both views
  - [x] Dashboard "Transfer Money" button links to ?view=transfers
  - [x] Form toggle buttons between transaction/transfer forms
  - [x] Fixed template syntax errors (pluralize filter, missing endif)
  - [x] Fixed navigation links in header and sidebar
- [x] **Bug Fixes:**
  - [x] Fixed "Transfer has no user" error - check user_id before validation
  - [x] Converted TransferForm from ModelForm to Form to avoid GenericFK validation
  - [x] Fixed LedgerService tuple unpacking in view
  - [x] Fixed log_activity parameters (obj instead of content_object)
  - [x] Removed orphaned journal entries from failed attempts
  - [x] Fixed navigation links (header.html and sidebar.html)

**Phase 1D+: Transaction Bug Fixes** ✅ COMPLETED
- [x] Fixed Transaction model validation
  - Added user_id check in clean() method
  - Added skip_validation parameter to save()
- [x] Fixed TransactionForm
  - Removed GenericFK fields from Meta.fields
  - Removed hidden field widget assignments
  - Set GenericFK fields directly in view from cleaned_data
- [x] Fixed transaction_create view
  - Get account and datetime_ist from cleaned_data
  - Set GenericFK fields from account object
  - Use skip_validation=True on save
  - Fixed log_activity parameter (obj instead of content_object)
- [x] Fixed transaction_edit view
  - Fixed log_activity parameter
- [x] Fixed transaction_delete view
  - Added balance reversal logic
  - Wrapped in db_transaction.atomic()
  - Calculate reverse delta (income: -amount, expense: +amount)
  - Update account balance using LedgerService
  - Import db_transaction to avoid select_for_update error
- [x] SQL patch commands added for restoring soft-deleted transactions

**Phase 1F: Integration & Testing** ✅ COMPLETED
- [x] Update dashboard view to show recent transactions
  - Added month-to-date income/expense calculations
  - Added recent transactions query (last 10)
  - Display in dashboard with relative timestamps
- [x] Update account detail page to show transaction history
  - Added tabbed interface (Transactions/Transfers)
  - Separate pagination for each tab (20 per page)
  - Desktop table + mobile card responsive layouts
  - Transaction/transfer direction indicators
- [x] Update category.can_delete() to check transaction usage
  - Check for transactions using the category
  - Check for child categories
- [x] Update BankAccount.can_delete() to check transaction usage
  - Check for transactions linked to account
  - Check for transfers (both from and to)
- [x] **Deletion Safety with User-Friendly Errors:**
  - Added ProtectedError exception handling in category_delete view
  - Added ProtectedError exception handling in account_delete view
  - Show friendly messages instead of Django error pages
- [x] **Template Tag System:**
  - Created transaction_tags template library
  - Custom filters: get_account(), get_transfer_from_account(), get_transfer_to_account()
  - is_outgoing_transfer() filter for transfer direction detection
- [x] **Dashboard UI Refinements:**
  - Removed Categories card from overview
  - Made Total Accounts card clickable (links to accounts page)
  - Removed redundant Accounts section
  - Category names displayed in capitalized format
- [x] Make "Transfer Money" dashboard button functional
- [x] Update schema.sql with all new tables
- [ ] **Integration Testing:**
  - [ ] Create income transaction → verify balance increase
  - [ ] Create expense transaction → verify balance decrease
  - [ ] Create transfer → verify both balances update
  - [ ] Delete transaction → verify balance reverses correctly
  - [ ] Delete transfer → verify both balances reverse correctly
  - [ ] Verify journal entries sum to zero
  - [ ] Verify activity logs created for all operations
  - [ ] Test soft delete restoration via SQL patch
  - [ ] Test category filtering in transaction form
  - [ ] Test account filtering in transaction list
  - [ ] Test date range filtering
  - [ ] Test pagination with view parameter preservation
  - [ ] Test tab switching between transactions/transfers
  - [ ] Test form toggle buttons
  - [ ] Test navigation links throughout app
  - [ ] Test mobile responsiveness for all transaction/transfer pages
  - [ ] Verify GenericForeignKey works with BankAccount
  - [ ] Test validation: category type matches transaction type
  - [ ] Test validation: amount > 0
  - [ ] Test validation: from ≠ to for transfers
  - [ ] Test edge cases: missing category, missing account
  - [ ] Test concurrent balance updates (race conditions)

**Phase 1G: Documentation & Cleanup**
- [ ] Update README.md with transaction features
- [ ] Update FDD if needed
- [ ] Update SDD if needed
- [ ] Add inline code documentation
- [ ] Test error handling and edge cases

---

### 3️⃣B Credit Card Integration - Full System Integration
**Objective:** Integrate credit cards throughout the application for complete functionality

**Specifications:**
- Credit cards appear in same dropdown as bank accounts
- Emoji indicators for account types (🏦 Bank, 💳 Credit Card)
- Bill payment (Bank → Credit Card) reduces credit card debt
- Net Worth = Bank balances + Investments (does NOT subtract credit card debt)
- Combined "Accounts & Cards" page with separate sections

**Phase 3A: Transaction & Transfer Integration** 🔜 NEXT
- [ ] Update TransactionForm (transactions/forms.py)
  - [ ] Create helper function to get all accounts (banks + credit cards)
  - [ ] Add emoji prefix to account choices (🏦 for banks, 💳 for cards)
  - [ ] Update account field to use combined queryset
  - [ ] Ensure GenericForeignKey handles both BankAccount and CreditCard
- [ ] Update TransferForm (transfers/forms.py)
  - [ ] Update from_account field with combined queryset + emojis
  - [ ] Update to_account field with combined queryset + emojis
  - [ ] Support Bank → Credit Card (bill payments reduce debt)
  - [ ] Support Credit Card → Bank (refunds/reversals increase debt)
  - [ ] Support Credit Card → Credit Card (balance transfers)
- [ ] Update transaction_create view
  - [ ] Handle ContentType for both BankAccount and CreditCard
  - [ ] Set correct GenericFK fields based on account type
- [ ] Update transfer_create view
  - [ ] Handle mixed account types in transfers
  - [ ] Verify ledger service works with CreditCard
- [ ] Test credit card transactions
  - [ ] Create expense on credit card (debt increases)
  - [ ] Create income on credit card (cashback/refund, debt decreases)
- [ ] Test credit card transfers
  - [ ] Bank → Credit Card bill payment (bank ↓, debt ↓)
  - [ ] Credit Card → Bank refund (debt ↑, bank ↑)

**Phase 3B: Dashboard Integration**
- [ ] Update dashboard view (core/views.py)
  - [ ] Keep Net Worth calculation for banks only (no debt subtraction)
  - [ ] Update Total Accounts card to show "X Banks • Y Cards"
  - [ ] Make Total Accounts card clickable (link to accounts page)
  - [ ] Include credit card transactions in Recent Transactions section
- [ ] Update dashboard template (templates/dashboard/dashboard.html)
  - [ ] Update Total Accounts card display (show bank/card breakdown)
  - [ ] Ensure recent transactions show credit card transactions
  - [ ] Update "Add Account" button to show choice modal
- [ ] Create account type choice modal
  - [ ] Modal with two options: "Add Bank Account" and "Add Credit Card"
  - [ ] Link to respective create forms
  - [ ] Responsive design with icons

**Phase 3C: Navigation & Combined Accounts Page**
- [ ] Rename "Accounts" to "Accounts & Cards" in navigation
  - [ ] Update header.html menu item
  - [ ] Update sidebar.html menu item
  - [ ] Update active state detection
- [ ] Update account_list view (accounts/views.py)
  - [ ] Query both BankAccount and CreditCard models
  - [ ] Pass both querysets to template separately
  - [ ] Calculate stats for both types
- [ ] Update account_list template (templates/accounts/account_list.html)
  - [ ] Add section headers: "Bank Accounts" and "Credit Cards"
  - [ ] Display bank accounts in first section with 🏦 emoji
  - [ ] Display credit cards in second section with 💳 emoji
  - [ ] Show appropriate stats for each section
  - [ ] Keep separate action buttons for each type
  - [ ] Responsive grid layout for both sections
- [ ] Update breadcrumbs/page titles throughout app

**Phase 3D: Account Detail Page Enhancement**
- [ ] Verify BankAccount detail page (accounts/account_detail.html)
  - [ ] Ensure transfers to/from credit cards display correctly
  - [ ] Test transaction tags with mixed account types
  - [ ] Verify emoji indicators show in transaction history
- [ ] Verify CreditCard detail page (creditcards/creditcard_detail.html)
  - [ ] Already has transaction/transfer tabs
  - [ ] Test with actual transactions from Phase 3A
  - [ ] Ensure emoji indicators work
- [ ] Add account type badges where needed

**Phase 3E: Ledger Service Verification**
- [ ] Test LedgerService.create_simple_entry() with CreditCard
  - [ ] Expense on credit card (balance becomes more negative = debt increases)
  - [ ] Income on credit card (cashback/refund = debt decreases)
  - [ ] Verify CreditCardBalance updates correctly
- [ ] Test LedgerService.create_transfer_entry() with credit cards
  - [ ] Bank → Credit Card: bank ↓, credit card debt ↓ (less negative)
  - [ ] Credit Card → Bank: credit card debt ↑ (more negative), bank ↑
  - [ ] Credit Card → Credit Card: one debt ↓, other debt ↑
- [ ] Verify LedgerService._update_account_balance() handles CreditCardBalance
  - [ ] Atomic updates with select_for_update()
  - [ ] Correct balance calculations
- [ ] Test edge cases
  - [ ] Credit card with positive balance (overpayment)
  - [ ] Large payment reducing debt to zero
  - [ ] Payment exceeding debt (creating positive balance)

**Phase 3F: Comprehensive Testing**
- [ ] Transaction Tests
  - [ ] Create expense transaction on credit card
  - [ ] Verify CreditCardBalance becomes more negative
  - [ ] Verify available_credit() decreases
  - [ ] Verify amount_owed() increases
  - [ ] Create income transaction (refund) on credit card
  - [ ] Verify debt decreases
- [ ] Transfer Tests
  - [ ] Bank → Credit Card (₹10,000 bill payment)
    - [ ] Bank balance decreases by ₹10,000
    - [ ] Credit card debt decreases by ₹10,000 (less negative)
    - [ ] Available credit increases by ₹10,000
  - [ ] Credit Card → Bank (₹5,000 refund)
    - [ ] Credit card debt increases by ₹5,000 (more negative)
    - [ ] Bank balance increases by ₹5,000
  - [ ] Credit Card → Credit Card (balance transfer)
    - [ ] Both balances update correctly
- [ ] Dashboard Tests
  - [ ] Verify Net Worth excludes credit card debt
  - [ ] Verify Total Accounts shows "X Banks • Y Cards"
  - [ ] Verify recent transactions include credit card transactions
  - [ ] Test account type choice modal
- [ ] Combined Accounts Page Tests
  - [ ] Both sections display correctly
  - [ ] Stats calculated correctly for each type
  - [ ] Emoji indicators show properly
  - [ ] Responsive design works on mobile
- [ ] Deletion Tests
  - [ ] Try deleting credit card with transactions (should fail)
  - [ ] Verify ProtectedError shows friendly message
- [ ] Edge Cases
  - [ ] Credit card with positive balance (overpayment)
  - [ ] Multiple cards with mixed balances
  - [ ] Decimal precision (2 decimal places)
  - [ ] Large numbers formatting

**Phase 3G: Documentation & Cleanup**
- [ ] Update FDD (docs/fdd/v1.md)
  - [ ] Document credit card integration
  - [ ] Update account selection specifications
  - [ ] Document emoji indicators
  - [ ] Update navigation structure
- [ ] Update SDD (docs/sdd/v1.md)
  - [ ] Update ERD with credit card relationships
  - [ ] Document GenericForeignKey usage with multiple account types
  - [ ] Update data flow diagrams
- [ ] Update TODO.md
  - [ ] Mark all Phase 3A-3G tasks as completed
  - [ ] Update "In Progress" section
- [ ] Update README.md
  - [ ] Add Credit Cards feature section
  - [ ] Document account types
  - [ ] Add usage examples
- [ ] Code cleanup
  - [ ] Add/update docstrings for new functions
  - [ ] Remove any debug code
  - [ ] Ensure consistent code formatting
  - [ ] Add inline comments for complex logic

---

### 4️⃣ Investments - MEDIUM PRIORITY
**Models First:**
- [ ] Investment model (stock/mutual fund details)
- [ ] Investment transaction model (buy/sell)
- [ ] Portfolio holdings calculation
- [ ] P&L calculation logic
- [ ] Current value tracking
- [ ] Create migrations for investment models

**Then UI (Desktop + Mobile Responsive):**
- [ ] Portfolio overview page
- [ ] Investment list with current values
- [ ] Add investment form
- [ ] Buy/Sell transaction form
- [ ] Investment details page with transaction history
- [ ] P&L reports (realized/unrealized)
- [ ] Holdings summary

### 5️⃣ Fixed Deposits (FD) - MEDIUM PRIORITY
**Models First:**
- [ ] FD model (amount, rate, tenure, maturity date)
- [ ] Interest calculation logic
- [ ] Maturity tracking
- [ ] Auto-credit to account on maturity (signal)
- [ ] Create migrations for FD models

**Then UI (Desktop + Mobile Responsive):**
- [ ] FD list page with maturity info
- [ ] Create FD form
- [ ] Edit FD details
- [ ] FD details page with interest breakdown
- [ ] Maturity alerts/notifications
- [ ] Premature closure handling

### 6️⃣ Loans - MEDIUM PRIORITY
**Models First:**
- [ ] Loan model (principal, rate, tenure, EMI)
- [ ] EMI calculation logic
- [ ] Payment schedule generation
- [ ] Interest calculation (reducing balance)
- [ ] Outstanding balance tracking
- [ ] Create migrations for loan models

**Then UI (Desktop + Mobile Responsive):**
- [ ] Loan list page with EMI info
- [ ] Create loan form
- [ ] Edit loan details
- [ ] Loan details page with amortization schedule
- [ ] EMI payment recording
- [ ] Prepayment/foreclosure handling
- [ ] Outstanding balance display

## 📋 Additional Features - Low to Medium Priority

### Password Reset Completion
- [ ] Password reset confirmation view
- [ ] Password reset confirmation template
- [ ] Token validation logic
- [ ] Email configuration for production

### Dashboard Enhancements
- [ ] Income vs Expense chart (last 6 months)
- [ ] Spend by category pie/bar chart (MTD)
- [ ] Date range filters
- [ ] Account type filters
- [ ] Category filters
- [ ] Export dashboard data (PDF/CSV)
- [ ] Recent transactions widget (last 10)
- [ ] Upcoming EMI/FD maturity alerts

### Reports Module
- [ ] Income vs Expense report with charts
- [ ] Category-wise spending report
- [ ] Account-wise balance sheet
- [ ] Monthly/Yearly summary reports
- [ ] Cashflow statement
- [ ] Tax reports (interest income, capital gains)
- [ ] PDF/Excel export functionality

### Transfers Module
- [ ] Enhance transfer functionality in transactions
- [ ] Transfer history page
- [ ] Recurring/scheduled transfers
- [ ] Transfer templates (frequent transfers)

## 📋 TODO - Low Priority

### Settings & Preferences
- [ ] User profile page
- [ ] Change password
- [ ] Update email
- [ ] Currency settings
- [ ] Date format settings
- [ ] Notification preferences

### Activity Log
- [ ] Activity tracking model
- [ ] Activity log page
- [ ] User action logging
- [ ] Login history

### Data Management
- [ ] Import transactions (CSV)
- [ ] Export all data
- [ ] Backup functionality
- [ ] Data cleanup utilities

### Mobile Responsiveness
- [ ] Mobile-optimized navigation
- [ ] Touch-friendly UI elements
- [ ] Responsive tables
- [ ] Mobile transaction entry

### Performance
- [ ] Database query optimization
- [ ] Add database indexes
- [ ] Caching strategy
- [ ] Lazy loading for large datasets

## 🐛 Known Issues
- None currently

## 🔮 Future Enhancements
- [ ] Budgeting module
- [ ] Bill reminders
- [ ] Recurring transactions
- [ ] Multi-currency support
- [ ] Bank statement import/parsing
- [ ] Mobile app (PWA)
- [ ] Two-factor authentication
- [ ] API for third-party integrations
- [ ] Dark mode auto-switch based on time
- [ ] Telegram/Email notifications

---
**Last Updated:** 24 November 2025
