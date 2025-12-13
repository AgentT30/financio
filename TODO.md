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

- [x] **Fixed Deposits - Phase 5: Dashboard Integration**
  - Status: Phases 1-7 complete, all 48 tests passing
  - Next: Investments module

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

**Phase 3A-3G: Credit Card Integration** ✅ COMPLETED
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

### 3️⃣ Transactions & Ledger System - ✅ COMPLETED

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
  - \_update_account_balance() for atomic balance updates
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
- [x] **Integration Testing:**
  - [x] Create income transaction → verify balance increase
  - [x] Create expense transaction → verify balance decrease
  - [x] Create transfer → verify both balances update
  - [x] Delete transaction → verify balance reverses correctly
  - [x] Delete transfer → verify both balances reverse correctly
  - [x] Verify journal entries sum to zero
  - [x] Verify activity logs created for all operations
  - [x] Test soft delete restoration via SQL patch
  - [x] Test category filtering in transaction form
  - [x] Test account filtering in transaction list
  - [x] Test date range filtering
  - [x] Test pagination with view parameter preservation
  - [x] Test tab switching between transactions/transfers
  - [x] Test form toggle buttons
  - [x] Test navigation links throughout app
  - [x] Test mobile responsiveness for all transaction/transfer pages
  - [x] Verify GenericForeignKey works with BankAccount
  - [x] Test validation: category type matches transaction type
  - [x] Test validation: amount > 0
  - [x] Test validation: from ≠ to for transfers
  - [x] Test edge cases: missing category, missing account
  - [x] Test concurrent balance updates (race conditions)

**Phase 1G: Documentation & Cleanup** ✅ COMPLETED

- [x] Update README.md with transaction features
- [x] Update FDD if needed
- [x] Update SDD if needed
- [x] Add inline code documentation
- [x] Test error handling and edge cases

---

### 3️⃣B Credit Card Integration - Full System Integration

**Objective:** Integrate credit cards throughout the application for complete functionality

**Specifications:**

- Credit cards appear in same dropdown as bank accounts
- Emoji indicators for account types (🏦 Bank, 💳 Credit Card)
- Bill payment (Bank → Credit Card) reduces credit card debt
- Net Worth = Bank balances + Investments (does NOT subtract credit card debt)
- Combined "Accounts & Cards" page with separate sections

**Phase 3A: Transaction & Transfer Integration** ✅ COMPLETED

- [x] Created core/utils.py with helper functions
  - [x] get_all_accounts_with_emoji() - Returns banks + credit cards with emoji prefixes
  - [x] get_account_from_compound_value() - Extracts account from "id|modelname" format
  - [x] get_account_choices_for_form() - Returns Django form choices
- [x] Update TransactionForm (transactions/forms.py)
  - [x] Changed account field from ModelChoiceField to ChoiceField
  - [x] Uses unified dropdown with emoji indicators (🏦 Bank, 💳 Credit Card)
  - [x] Added clean_account() method to extract actual account object
  - [x] Edit mode support: reconstructs compound value from GenericFK
- [x] Update TransferForm (transfers/forms.py)
  - [x] Updated from_account field with combined queryset + emojis
  - [x] Updated to_account field with combined queryset + emojis
  - [x] Added clean_from_account() and clean_to_account() methods
  - [x] Supports Bank → Credit Card (bill payments reduce debt)
  - [x] Supports Credit Card → Bank (refunds/reversals increase debt)
  - [x] Supports Credit Card → Credit Card (balance transfers)
- [x] Update transaction views (transactions/views.py)
  - [x] transaction_create: Gets account from form.cleaned_data, sets GenericFK
  - [x] transaction_edit: Fixed GenericFK field names, reverse-and-recreate pattern
  - [x] Wrapped in db_transaction.atomic() for select_for_update() compatibility
- [x] Update transfer views (transfers/views.py)
  - [x] transfer_create: Already compatible with GenericFK from form
  - [x] No changes needed - form handles everything
- [x] Update LedgerService (ledger/services.py)
  - [x] \_update_account_balance() now supports both BankAccount and CreditCard
  - [x] Uses CreditCardBalance for credit cards (parallel to BankAccountBalance)
  - [x] Account type detection via **class**.**name**
- [x] Bug Fixes
  - [x] Fixed FieldError: Changed deleted_at to status='active' in core/utils.py
  - [x] Fixed transaction_edit: Corrected GenericFK field names (account_content_type/account_object_id)
  - [x] Fixed transaction_edit: Account field not populating in form (removed incorrect initial override)
  - [x] Fixed transaction_edit: Missing arguments error in \_update_account_balance()
  - [x] Fixed transaction_edit: Reverse-and-recreate pattern with proper balance reversal
  - [x] Fixed transaction_edit: ControlAccount balance update error (skip ControlAccounts)
  - [x] Fixed transaction_edit: Protected foreign key error (unlink before delete)
  - [x] Added db_transaction.atomic() wrapper for select_for_update() compatibility
- [x] Created recalculate_balances management command (ledger/management/commands/)
  - [x] Recalculates all account balances from ledger postings
  - [x] Only counts postings from active transactions/transfers
  - [x] --dry-run flag to preview changes
  - [x] --cleanup-orphans flag to delete orphaned journal entries
  - [x] Shows detailed before/after balance comparison
  - [x] Safe to run anytime for balance verification/correction
- [x] Testing completed
  - [x] Create expense on credit card (debt increases) ✓
  - [x] Create income on credit card (cashback/refund, debt decreases) ✓
  - [x] Edit transaction with account change ✓
  - [x] Bank → Credit Card bill payment (bank ↓, debt ↓) ✓
  - [x] Credit Card → Bank refund (debt ↑, bank ↑) ✓
  - [x] Balance recalculation from ledger ✓
  - [x] Orphaned journal entry cleanup ✓

**Phase 3B: Dashboard Integration** ✅ COMPLETED

- [x] Update dashboard view (core/views.py)
  - [x] Updated Net Worth calculation for banks only (excludes credit card debt)
  - [x] Added status='active' filter for bank accounts
  - [x] Count banks and credit cards separately (total_banks, total_cards)
  - [x] Added clear comments explaining Net Worth excludes credit card debt
- [x] Update dashboard template (templates/dashboard/dashboard.html)
  - [x] Updated Total Accounts card display ("X Banks • Y Cards" format)
  - [x] Total Accounts card already clickable (links to accounts page)
  - [x] Recent transactions automatically show credit card transactions with emoji indicators
- [x] Create account type choice modal
  - [x] Modal with two options: "🏦 Add Bank Account" and "💳 Add Credit Card"
  - [x] Links to respective create forms (account_create and /creditcards/create/)
  - [x] Responsive design with icons and hover effects
  - [x] Click outside or Escape key to close
  - [x] Smooth animations and transitions
- [x] Enhanced transaction template tags (transaction_tags.py)
  - [x] Updated get_account() to include emoji indicators
  - [x] Updated get_transfer_from_account() to include emoji indicators
  - [x] Updated get_transfer_to_account() to include emoji indicators
  - [x] Emojis: 🏦 for BankAccount, 💳 for CreditCard
  - [x] Applies across entire application automatically

**Phase 3C: Navigation & Combined Accounts Page** ✅ COMPLETED

- [x] Rename "Accounts" to "Accounts & Cards" in navigation
  - [x] Update header.html menu item
  - [x] Update sidebar.html menu item
  - [x] Update header_sidebar.html component
  - [x] Update dashboard.html navigation
  - [x] Update active state detection
- [x] Update account_list view (accounts/views.py)
  - [x] Query both BankAccount and CreditCard models
  - [x] Pass both querysets to template separately (bank_accounts, credit_cards)
  - [x] Calculate bank stats (active_banks_count, archived_banks_count, total_bank_balance)
  - [x] Calculate credit card stats (active_cards_count, archived_cards_count, total_credit_limit, total_available_credit, total_amount_owed)
  - [x] Iterate through active cards to sum available_credit() and amount_owed()
- [x] Update account_list template (templates/accounts/account_list.html)
  - [x] Page title updated to "Accounts & Cards"
  - [x] Created two-section layout with separate headers
  - [x] Bank Accounts section with 🏦 emoji header
  - [x] Credit Cards section with 💳 emoji header
  - [x] Bank stats: "X active • Y archived • ₹Z total"
  - [x] Credit card stats: "X active • Y archived" + 3 stat cards (Total Limit, Available Credit, Amount Owed)
  - [x] Separate action buttons ("Add Bank Account" and "Add Credit Card")
  - [x] Responsive grid layout for both sections (1-2-3 column responsive)
  - [x] Separate empty states for each section
  - [x] Dark mode support throughout
  - [x] Menu ID prefixes to avoid conflicts (menu-bank-, menu-card-)
  - [x] Credit card URLs use direct paths (/creditcards/...)

**Phase 3D: Account Detail Page Enhancement** ✅ COMPLETED

- [x] Verify BankAccount detail page (accounts/account_detail.html)
  - [x] Ensure transfers to/from credit cards display correctly (GenericForeignKey filtering works)
  - [x] Test transaction tags with mixed account types (emoji indicators working via template tags)
  - [x] Verify emoji indicators show in transaction history (🏦 for BankAccount, 💳 for CreditCard)
- [x] Verify CreditCard detail page (creditcards/creditcard_detail.html)
  - [x] Already has transaction/transfer tabs (confirmed working)
  - [x] Test with actual transactions from Phase 3A (GenericForeignKey filtering works)
  - [x] Ensure emoji indicators work (confirmed via template tags)
- [x] Add account type badges where needed
  - [x] Added 🏦 Bank Account badge to account_detail.html header
  - [x] Added 💳 Credit Card badge to creditcard_detail.html header
  - [x] Used consistent badge styling with blue for bank accounts, purple for credit cards

**Phase 3E: Ledger Service Verification** ✅ COMPLETED

- [x] Create comprehensive test plan (PHASE_3E_TEST_PLAN.md)
- [x] Test LedgerService.create_simple_entry() with CreditCard
  - [x] Test 1.1: Expense on credit card (balance becomes more negative = debt increases)
  - [x] Test 1.2: Income on credit card (cashback/refund = debt decreases)
  - [x] Verify CreditCardBalance updates correctly
- [x] Test LedgerService.create_transfer_entry() with credit cards
  - [x] Test 2.1: Bank → Credit Card (bank ↓, credit card debt ↓ = less negative)
  - [x] Test 2.2: Credit Card → Bank (credit card debt ↑ = more negative, bank ↑)
  - [x] Test 2.3: Credit Card → Credit Card (one debt ↓, other debt ↑)
- [x] Verify LedgerService.\_update_account_balance() handles CreditCardBalance
  - [x] Test 3.1: Atomic updates with select_for_update() (race condition prevention)
  - [x] Test 3.2: Correct balance type selection (BankAccountBalance vs CreditCardBalance)
- [x] Test edge cases
  - [x] Test 4.1: Credit card with positive balance (overpayment scenario)
  - [x] **CRITICAL FIX**: Added insufficient balance validation for bank accounts
    - [x] TransferForm: Validates bank account has sufficient balance before transfer
    - [x] TransactionForm: Validates bank account has sufficient balance before expense
    - [x] Credit cards exempt from validation (can go more negative)
    - [x] User-friendly error messages with current balance and requested amount
  - [x] Test 4.2: Large payment reducing debt to zero (exact payment)
  - [x] Test 4.3: Multiple small transactions (decimal precision verification)
  - [x] Test 4.4: Large numbers formatting (₹99,999.99 display)
- [x] Test error handling
  - [x] Test 5.1: Delete credit card with transactions (should fail gracefully)
  - [x] Test 5.2: Invalid account type handling

**Phase 3F: Comprehensive Testing** ✅ COMPLETED

- [x] Transaction Tests
  - [x] Create expense transaction on credit card
  - [x] Verify CreditCardBalance becomes more negative
  - [x] Verify available_credit() decreases
  - [x] Verify amount_owed() increases
  - [x] Create income transaction (refund) on credit card
  - [x] Verify debt decreases
- [x] Transfer Tests
  - [x] Bank → Credit Card (₹10,000 bill payment)
    - [x] Bank balance decreases by ₹10,000
    - [x] Credit card debt decreases by ₹10,000 (less negative)
    - [x] Available credit increases by ₹10,000
  - [x] Credit Card → Bank (₹5,000 refund)
    - [x] Credit card debt increases by ₹5,000 (more negative)
    - [x] Bank balance increases by ₹5,000
  - [x] Credit Card → Credit Card (balance transfer)
    - [x] Both balances update correctly
- [x] Dashboard Tests
  - [x] Verify Net Worth excludes credit card debt
  - [x] Verify Total Accounts shows "X Banks • Y Cards"
  - [x] Verify recent transactions include credit card transactions
  - [x] Test account type choice modal
- [x] Combined Accounts Page Tests
  - [x] Both sections display correctly
  - [x] Stats calculated correctly for each type
  - [x] Emoji indicators show properly
  - [x] Responsive design works on mobile
- [x] Deletion Tests
  - [x] Try deleting credit card with transactions (should fail)
  - [x] Verify ProtectedError shows friendly message
- [x] Edge Cases
  - [x] Credit card with positive balance (overpayment)
  - [x] Multiple cards with mixed balances
  - [x] Decimal precision (2 decimal places)
  - [x] Large numbers formatting
- [x] Bug Fixes
  - [x] Fixed dashboard and account list balance calculations to use get_current_balance() method
  - [x] Handles missing balance records gracefully (falls back to opening_balance)

**Phase 3G: Documentation & Cleanup** ✅ COMPLETED

- [x] Update FDD (docs/fdd/v1.md)
  - [x] Document credit card integration
  - [x] Update account selection specifications
  - [x] Document emoji indicators
  - [x] Update navigation structure
  - [x] Document Indian number formatting
  - [x] Document balance calculation robustness
  - [x] Add Phase 3F testing section
- [x] Update SDD (docs/sdd/v1.md)
  - [x] Update ERD with credit card relationships
  - [x] Document GenericForeignKey usage with multiple account types
  - [x] Document balance materialization strategy
  - [x] Add validation and testing section
  - [x] Update Django app layout with current implementation
- [x] Update TODO.md
  - [x] Mark all Phase 3A-3F tasks as completed
  - [x] Update "In Progress" section
- [x] Update README.md
  - [x] Add Credit Cards feature section
  - [x] Document account types
  - [x] Add usage examples
  - [x] Update feature list
- [x] Code cleanup - Part 1: Docstrings
  - [x] Add/update docstrings for core utilities (core/utils.py)
  - [x] Add/update docstrings for ledger service (ledger/services.py)
  - [x] Add/update docstrings for template filters (core/templatetags/indian_numbers.py)
  - [x] Add/update docstrings for views (core/views.py, accounts/views.py)
  - [x] Add/update docstrings for forms (transactions/forms.py, transfers/forms.py)
  - [x] Add/update docstrings for models (accounts/models.py, creditcards/models.py)
  - [x] Add/update docstrings for management commands (recalculate_balances.py)
- [x] Code cleanup - Part 2: Debug code removal
  - [x] Removed debug print statements from authn/views.py
  - [x] Removed unused BankAccountBalance import from core/views.py
  - [x] Verified no commented-out code blocks
- [x] Code cleanup - Part 3: Code formatting
  - [x] Removed trailing whitespace from all Python files in Phase 3 directories
  - [x] Verified consistent import organization (PEP 8: stdlib, Django, third-party, local)
  - [x] Verified consistent indentation (4 spaces)
- [x] Code cleanup - Part 4: Inline comments
  - [x] Added comments explaining compound value reconstruction in forms
  - [x] Added comments for GenericFK comparison logic (same-account validation)
  - [x] Added comments for balance validation differences (BankAccount vs CreditCard)
  - [x] Added comments for double-entry reversal logic in transaction edits/deletes
  - [x] Added comments for select_for_update() race condition prevention
  - [x] Added comments for available credit calculation with examples
  - [x] Added comments for opening balance sync conditions

---

### 4️⃣ Investments - MEDIUM PRIORITY - ✅ COMPLETED

**Phase 1: Investment Models** - ✅ COMPLETED

- [x] Implement `Broker` model (user, name, broker_user_id, demat_account_number)
- [x] Implement `Investment` model (stock/mutual fund details, linked to Broker)
- [x] Implement `InvestmentTransaction` model (buy/sell, quantity, price, fees)
- [x] Define logic for Portfolio holdings and P&L calculation (weighted average price)
- [x] Implement current value tracking (manual update for now)
- [x] Create migrations for investment models

**Phase 2: Investment UI** - ✅ COMPLETED

- [x] Portfolio Overview (Total Value, Total P&L, Total Invested)
- [x] Investment List (grouped by Broker, with summary stats)
- [x] Investment Detail View (Transaction History, P&L, Quantity)
- [x] Add/Edit Broker Forms
- [x] Add/Edit Investment Forms
- [x] Buy/Sell Transaction Forms
- [x] "Back to Investments" navigation button

**Phase 3: Dashboard Integration** - ✅ COMPLETED

- [x] Add Portfolio Value to Net Worth (Bank + FD + Investments)
- [x] Show Investment count in "Total Accounts" card
- [x] Navigation updates (Header & Sidebar)

**Phase 4: UI Refinements** - ✅ COMPLETED

- [x] Unified "Smart Form" for Investment Creation & Transaction Addition
- [x] Added "Transaction Type" (Buy/Sell) to unified form
- [x] Added "Delete Asset" button to Investment Detail page
- [x] Auto-delete investment when last transaction is deleted
- [x] Added "Back to Investment List" button on Detail page
- [x] Added helper text "Click on a stock to see transactions" in List view
- [x] Form improvements:
  - [x] Removed pre-filled 0 values for Price and Fees
  - [x] Added "Today", "Yesterday", "Day before yesterday" date shortcuts
  - [x] Enforced integer input for quantities

### 5️⃣ Fixed Deposits (FD) - ✅ COMPLETED

**Objective:** Implement standalone FD tracking module (informational only, NO transaction/ledger integration)

**Key Specifications:**

- FDs are **standalone models** (do NOT inherit from BaseAccount)
- FDs do **NOT appear** in transaction/transfer account dropdowns
- Interest entered **manually** during FD creation (maturity_amount field)
- NO automatic interest calculation or ledger postings
- Dashboard net worth includes maturity amounts of **active FDs only**
- Status workflow: active → archived (via "Mark as Matured" button)

**Phase 1: Models & Admin** - ✅ COMPLETED

- [x] Create FixedDeposit model in fds/models.py
  - [x] Fields: user, name, institution, fd_number, principal_amount, interest_rate
  - [x] Fields: compounding_frequency, tenure_months, opened_on, maturity_date
  - [x] Fields: maturity_amount, auto_renewal, status, notes, color, timestamps
  - [x] Status choices: 'active', 'archived'
  - [x] Validation: maturity_date > opened_on, maturity_amount ≥ principal_amount
  - [x] Methods: can_delete(), days_to_maturity(), is_matured()
  - [x] Added get_maturity_badge_info() for badge display logic
  - [x] Added get_interest_earned() helper method
- [x] Register FixedDeposit in fds/admin.py
- [x] Update schema.sql with fixed_deposits table
- [x] Create and apply migrations

**Phase 2: Forms & Validation** - ✅ COMPLETED

- [x] Create FixedDepositForm in fds/forms.py
- [x] All fields with TailwindCSS styling (dark mode)
- [x] Date pickers for opened_on and maturity_date
- [x] Validation: principal > 0, interest_rate 0-100%, maturity_date > opened_on
- [x] Validation: maturity_amount ≥ principal_amount
- [x] Validation: tenure_months > 0
- [x] Help texts for each field
- [x] Field-level validation methods (clean_field methods)
- [x] Form-level validation in clean() method
- [x] Disabled editing for archived FDs

**Phase 3: Views & URLs** - ✅ COMPLETED

- [x] fd_list view (fds/views.py)
  - [x] List active + archived FDs
  - [x] Stats card: total FDs, total principal, total maturity amount (active only)
  - [x] Maturity status badges (green/orange/gray based on dates)
  - [x] Responsive grid layout
- [x] fd_create view
  - [x] Create FD with all fields
  - [x] Activity logging
  - [x] Redirect to FD list on success
- [x] fd_detail view
  - [x] Show all FD information
  - [x] "Mark as Matured" button (if active and past maturity date)
  - [x] Edit/Delete action buttons
- [x] fd_edit view
  - [x] Update FD details
  - [x] Activity logging with field changes
  - [x] Prevent editing if archived
- [x] fd_delete view
  - [x] Confirmation modal
  - [x] Activity logging
  - [x] Hard delete (no dependencies to check)
- [x] fd_mark_matured view
  - [x] Set status='archived' (irreversible)
  - [x] Activity logging
  - [x] Redirect to FD list with success message
- [x] Create fds/urls.py with 6 URL patterns
- [x] Register in main urls.py

**Phase 4: Templates** - ✅ COMPLETED

- [x] fd_list.html
  - [x] Responsive grid (3 columns desktop, 1 mobile)
  - [x] 3 stat cards (Total FDs, Total Principal, Total Maturity - active only)
  - [x] Maturity badges (green/orange/gray)
  - [x] 3-dot action menus
  - [x] Indian number formatting
  - [x] Action buttons: View, Edit, Delete
- [x] fd_form.html
  - [x] Sectioned form (Basic Info, FD Details, Financial Info, Additional Details)
  - [x] All 14 fields with dark mode styling
  - [x] Status field added (required)
  - [x] Consistent styling with other forms
- [x] fd_detail.html
  - [x] All FD information displayed
  - [x] 3 summary cards (Principal, Interest Earned, Maturity Amount)
  - [x] Days to maturity calculation (fixed invalid 'abs' filter)
  - [x] Conditional "Mark as Matured" button
  - [x] Color-coded status badge
- [x] fd_confirm_delete.html
  - [x] Delete confirmation modal
  - [x] Show FD name and institution
- [x] Bug Fixes:
  - [x] Fixed context variable mismatch (fds → fixed_deposits)
  - [x] Fixed stats unpacking (stats dict → individual variables)
  - [x] Fixed invalid template filter (abs → removed)

**Phase 5: Dashboard Integration** - ✅ COMPLETED

- [x] Update dashboard view (core/views.py)
  - [x] Query active FDs for user
  - [x] Sum maturity_amount for active FDs
  - [x] Add to net_worth total
- [x] Update dashboard template (optional)
  - [x] Add FD count to stats (if desired)
  - [x] Or keep existing "Total Accounts" card unchanged

**Phase 6: Navigation & Polish** - ✅ COMPLETED

- [x] Add "Fixed Deposits" menu item to header/sidebar
  - [x] Links to /fds/
  - [x] Active state detection
  - [x] Replaced "Categories" with "Fixed Deposits"
  - [x] Bank/institution icon added
- [x] Test responsive design (mobile/tablet/desktop)
- [x] Test all CRUD operations
- [x] Test maturity badge logic (all 3 scenarios)
- [x] Dashboard header/sidebar consistency fixed

**Phase 7: Documentation & Cleanup** - ✅ COMPLETED

- [x] Schema.sql updated with fixed_deposits table
- [x] Comprehensive test plan created (48 test cases)
- [x] All tests passing (docs/testing/FixedDeposits_Testing.md)
- [x] Activity logging verified (create, edit, delete, mark as matured)
- [x] Error handling tested
- [x] TODO.md updated
- [x] Section 5 marked as completed

**Testing Summary:**

- ✅ 48/48 tests passed
- ✅ All CRUD operations working
- ✅ Form validation complete
- ✅ Maturity badge logic verified
- ✅ Activity logging functional
- ✅ UI responsive across devices
- ✅ Dark mode working
- ✅ Ready for Phase 5 (Dashboard Integration)

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

### 7️⃣ Investment Module - Security & Permissions Testing

**Objective:** Verify user isolation and access control for the Investments module

**Test Cases (from docs/testing/Investments_Testing.md - Section 10):**

- [ ] **Test 10.1: User Isolation - Investments**

  - Login as User A, create investment
  - Logout, login as User B
  - Try to access User A's investment URL directly
  - Expected: 404 or 403 error, User B cannot view User A's investment

- [ ] **Test 10.2: User Isolation - Brokers**

  - Login as User A, create broker
  - Logout, login as User B
  - Try to access User A's broker URL directly
  - Expected: 404 or 403 error, User B cannot view/edit User A's broker

- [ ] **Test 10.3: User Isolation - Transactions**

  - Login as User A, create transaction
  - Logout, login as User B
  - Try to edit/delete User A's transaction URL directly
  - Expected: 404 or 403 error, User B cannot modify User A's transaction

- [ ] **Test 10.4: Unauthorized Access**
  - Logout (not authenticated)
  - Try to access investment list, broker list, etc.
  - Expected: Redirect to login page, Cannot access any investment pages

**Priority:** Medium (security is important but basic @login_required decorators should already provide protection)

**Notes:**

- All views already use @login_required decorator
- All queries filter by request.user
- Need to verify with actual multi-user testing

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
- [ ] **Balance Recalculation UI** (Admin/Settings page)
  - [ ] Create admin/settings page for balance management
  - [ ] Add "Recalculate Balances" button with confirmation modal
  - [ ] Show dry-run preview before applying changes
  - [ ] Display before/after balance comparison
  - [ ] Option to cleanup orphaned journal entries
  - [ ] Activity logging for balance recalculations
  - [ ] Success/error feedback messages
  - Note: Management command already exists at `ledger/management/commands/recalculate_balances.py`

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

**Last Updated:** 25 November 2025
