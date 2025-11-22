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
- [x] Accounts: Title case storage - **LEGACY, TO BE REFACTORED**
- [x] **Account Refactoring Plan Created** (docs/ACCOUNT_REFACTORING_PLAN.md)
- [x] **FDD Updated** with specialized account types
- [x] **SDD Updated** with new ERD and table structure

## 🚧 In Progress
- [ ] **MAJOR REFACTORING: Account Model Split** (see docs/ACCOUNT_REFACTORING_PLAN.md)
  - Status: Planning phase complete, awaiting user approval
  - Next: Begin Phase 2 implementation

## 📋 TODO - Priority Order

### 🔥 HIGH PRIORITY: Account Model Refactoring
**Objective:** Split unified Account model into specialized models across separate apps

**Phase 1: Preparation** ✅
- [x] Create detailed refactoring plan
- [x] Update FDD with specialized account structures
- [x] Update SDD with new ERD and tables
- [x] Document risks and mitigation strategies

**Phase 2: Create New Apps and Models** 🔜
- [ ] Create `creditcards` app
- [ ] Create `wallets` app
- [ ] Create `cash` app
- [ ] Create `core/models.py` with BaseAccount abstract model
- [ ] Define SavingsAccount model in `accounts/`
- [ ] Define CreditCard model in `creditcards/`
- [ ] Define DigitalWallet model in `wallets/`
- [ ] Define CashAccount model in `cash/`
- [ ] Define FixedDeposit model in `fds/`
- [ ] Define LoanAccount model in `loans/`
- [ ] Create balance models for each account type

**Phase 3: Update Settings and Register Apps**
- [ ] Add new apps to INSTALLED_APPS
- [ ] Register models in admin.py for each app
- [ ] Configure admin interfaces

**Phase 4: Data Migration Strategy**
- [ ] Run makemigrations for all new apps
- [ ] Create custom data migration script
- [ ] Test migration on database copy
- [ ] Implement rollback plan
- [ ] Create verification management command

**Phase 5: Update Views and URLs**
- [ ] Create unified AllAccountsListView in core/views.py
- [ ] Create SavingsAccount CRUD views
- [ ] Create CreditCard CRUD views
- [ ] Create DigitalWallet CRUD views
- [ ] Create CashAccount CRUD views
- [ ] Create FixedDeposit CRUD views
- [ ] Create LoanAccount CRUD views
- [ ] Update URL patterns (unified + type-specific routes)

**Phase 6: Update Templates**
- [ ] Create templates/accounts/all_accounts_list.html (unified view)
- [ ] Create savings account templates
- [ ] Create credit card templates
- [ ] Create digital wallet templates
- [ ] Create cash account templates
- [ ] Create FD templates
- [ ] Create loan templates

**Phase 7: Dashboard Integration**
- [ ] Update dashboard view to fetch all account types
- [ ] Update dashboard template to show categorized accounts
- [ ] Update account widgets and stats

**Phase 8: Update Forms**
- [ ] Create SavingsAccountForm
- [ ] Create CreditCardForm
- [ ] Create DigitalWalletForm
- [ ] Create CashAccountForm
- [ ] Create FixedDepositForm
- [ ] Create LoanAccountForm

**Phase 9: Ledger Integration (Future)**
- [ ] Update Posting model with GenericForeignKey
- [ ] Create helper functions for account resolution
- [ ] Update transaction logic to work with all account types

**Phase 10: Testing**
- [ ] Write unit tests for each account type
- [ ] Write integration tests for data migration
- [ ] Test CRUD operations for all types
- [ ] Test balance calculations
- [ ] Test GenericFK relationships

**Phase 11: Documentation**
- [ ] Create migration guide for users
- [ ] Update README with new architecture
- [ ] Document GenericFK usage patterns

**Phase 12: Deployment**
- [ ] Backup production database
- [ ] Deploy new code
- [ ] Run migrations
- [ ] Verify data integrity
- [ ] Monitor for issues
- [ ] Drop legacy tables after 1 week

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
- [x] Create new account form (make dashboard button functional)
- [x] Account type selection with icons
- [x] Edit account details
- [x] Delete account (with transaction dependency checks)
- [x] Account details page with transaction history placeholder
- [x] Upload/update account picture
- [x] Account balance display and calculations
- [x] Account status (active/inactive)

### 3️⃣ Transactions - HIGH PRIORITY
**Models First:**
- [ ] Create Transaction model (amount, date, description, type)
- [ ] Create Ledger model (double-entry bookkeeping - debit/credit entries)
- [ ] Implement auto-generation of balancing ledger entries
- [ ] Link transactions to categories and accounts
- [ ] Transaction validation logic (balance checks, date validation)
- [ ] Create migrations for transaction models
- [ ] Signal handlers for auto-updating AccountBalance

**Then UI (Desktop + Mobile Responsive):**
- [ ] Transaction list/history page with filters
- [ ] Create transaction form for income/expense (make dashboard button functional)
- [ ] Transfer between accounts form
- [ ] Transaction edit functionality
- [ ] Transaction delete with ledger cleanup
- [ ] Transaction filters (date range, category, account, type)
- [ ] Search functionality
- [ ] Pagination for large transaction lists

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
**Last Updated:** 16 November 2025
