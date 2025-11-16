# Financio - Development TODO

## ✅ Completed
- [x] Django project setup with all apps
- [x] Database models: Categories (hierarchical, 3-level max)
- [x] Database models: Accounts (6 types with encryption)
- [x] Database models: AccountBalance (materialized table)
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

## 🚧 In Progress
- [ ] Dashboard UI implementation

## 📋 TODO - High Priority

### Dashboard
- [ ] Create navigation header component with menu links
- [ ] Create sidebar navigation component
- [ ] Overview cards (Net Worth, Income MTD, Expense MTD, Cash total)
- [ ] Accounts snapshot list with balances
- [ ] Recent transactions table (last 10)
- [ ] Quick action buttons
- [ ] User profile dropdown with logout
- [ ] Create dashboard view to calculate stats
- [ ] Query and display actual account data

### Transaction Models (Core Functionality)
- [ ] Create Transaction model (double-entry ledger)
- [ ] Create Ledger model (journal entries)
- [ ] Auto-create balancing ledger entries on transaction save
- [ ] Transaction categorization
- [ ] Add transaction validation logic
- [ ] Create migrations for transaction models

### Transaction UI
- [ ] Transaction list/history page
- [ ] Create transaction form (income/expense)
- [ ] Transfer between accounts form
- [ ] Split transaction support
- [ ] Transaction edit/delete functionality
- [ ] Transaction filters (date, category, account, type)

### Accounts Management
- [ ] Accounts list page
- [ ] Create new account form
- [ ] Edit account details
- [ ] Account details page with transaction history
- [ ] Account balance calculation
- [ ] Upload/update account picture

### Categories Management
- [ ] Categories list/tree view
- [ ] Create category form
- [ ] Edit category
- [ ] Delete category (with transaction reassignment)
- [ ] Seed default categories
- [ ] Category icons/colors

## 📋 TODO - Medium Priority

### Password Reset
- [ ] Password reset confirmation view
- [ ] Password reset confirmation template
- [ ] Token validation logic
- [ ] Email configuration for production

### Dashboard Enhancements
- [ ] Income vs Expense chart (last 6 months)
- [ ] Spend by category chart (MTD)
- [ ] Date range filters
- [ ] Account type filters
- [ ] Category filters
- [ ] Export data functionality

### Reports
- [ ] Income vs Expense report
- [ ] Category-wise spending report
- [ ] Account-wise balance sheet
- [ ] Monthly/Yearly summary
- [ ] Cashflow statement
- [ ] PDF export

### Investments (FDD Module)
- [ ] Investment model
- [ ] Portfolio view
- [ ] Buy/Sell transactions
- [ ] P&L calculation
- [ ] Holdings view

### Fixed Deposits (FDD Module)
- [ ] FD model
- [ ] FD list page
- [ ] Create FD form
- [ ] FD maturity tracking
- [ ] Interest calculation
- [ ] Auto-credit on maturity

### Loans (FDD Module)
- [ ] Loan model
- [ ] Loan list page
- [ ] EMI tracking
- [ ] Payment schedule
- [ ] Interest calculation

### Transfers Module
- [ ] Transfer model
- [ ] Account-to-account transfer form
- [ ] Transfer history
- [ ] Recurring transfers

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
