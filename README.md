# Financio - Personal Finance Management System

A self-hosted personal finance management application built with Django, PostgreSQL, TailwindCSS, and Vanilla JavaScript.

## Project Overview

Financio is designed to help users track and manage their personal finances, including:
- Multiple account types (Bank Accounts, Credit Cards, Digital Wallets, Cash, FDs, Loans)
- Income and expense transactions with double-entry ledger
- Transfers between accounts (including cross-account-type transfers)
- Investment tracking (Stocks and Mutual Funds) - *Planned*
- Fixed deposits and loans management - *Planned*
- Financial reports and analytics - *Planned*
- Activity logging and audit trail
- Indian number formatting (X,XX,XXX)
- Dark/light theme support

## Tech Stack

- **Backend**: Django 5.2.8 (Python)
- **Database**: PostgreSQL 16
- **Frontend**: TailwindCSS + Vanilla JavaScript (AJAX)
- **Deployment**: Docker Compose
- **Theme**: Dark mode (default) with light mode toggle

## Project Structure

```
financio/
├── docs/                   # FDD and SDD documentation
│   ├── fdd/v1.md
│   └── sdd/v1.md
├── financio_suite/         # Django project root
│   ├── manage.py
│   ├── financio_suite/     # Project settings
│   ├── core/               # Shared utilities, BaseAccount model
│   ├── authn/              # Authentication
│   ├── accounts/           # Bank account management
│   ├── creditcards/        # Credit card management ✅
│   ├── transactions/       # Transaction tracking with GenericFK
│   ├── ledger/             # Double-entry ledger system
│   ├── transfers/          # Account transfers
│   ├── categories/         # Transaction categories
│   ├── investments/        # Investment management (planned)
│   ├── fds/                # Fixed deposits (planned)
│   ├── loans/              # Loan tracking (planned)
│   ├── wallets/            # Digital wallets (planned)
│   ├── cash/               # Cash accounts (planned)
│   ├── activity/           # Activity logging
│   ├── reports/            # Financial reports (planned)
│   ├── ui/                 # UI components
│   ├── templates/          # Django templates
│   ├── static/             # Static files (CSS, JS, images)
│   └── media/              # User uploads
├── db/                     # PostgreSQL data
├── requirements.txt        # Python dependencies
└── docker-compose.yml      # Docker configuration
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 16 (or use Docker)
- Virtual environment

### Local Development Setup

1. **Clone the repository** (if applicable)
   ```bash
   cd /path/to/financio
   ```

2. **Create and activate virtual environment**
   ```bash
   cd financio_suite
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Application: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Docker Setup

1. **Start PostgreSQL database**
   ```bash
   docker compose up db -d
   ```

2. **Start the web application**
   ```bash
   docker compose up webapp
   ```

## Django Apps

The project follows a modular architecture with the following apps:

### Implemented Apps

- **core**: Shared utilities, BaseAccount abstract model, middleware, template tags (indian_numbers)
- **authn**: User authentication (signup, login, logout, password management)
- **accounts**: Bank account management (savings/checking/current/salary accounts)
- **creditcards**: Credit card management with billing cycles and credit limits ✅
- **transactions**: Transaction recording with GenericForeignKey for polymorphic account references
- **ledger**: Double-entry ledger (JournalEntry, Postings, ControlAccounts, LedgerService)
- **transfers**: Fund transfers between accounts (supports cross-account-type transfers)
- **categories**: Hierarchical transaction categorization (income/expense)
- **activity**: User activity logging and change tracking
- **ui**: Shared UI components and templates

### Planned Apps

- **investments**: Stock and mutual fund investment tracking
- **fds**: Fixed deposit management
- **loans**: Loan tracking and EMI recording
- **wallets**: Digital wallet management (UPI apps, mobile wallets)
- **cash**: Cash account tracking
- **reports**: Financial analytics and reporting

## Key Features

### ✅ Implemented Features

#### Authentication
- Email/password login and signup
- Session management with 2-week timeout
- Password change functionality
- Secure session handling

#### Bank Accounts
- Support for savings, checking, current, and salary accounts
- Encrypted account number storage
- Masked account numbers (last 4 digits visible)
- Toggle visibility for sensitive data
- Copy to clipboard functionality
- Balance tracking with materialized balance tables
- Account archival (soft delete)
- Color customization and optional pictures

#### Credit Cards ✅
- Full credit card management system
- Support for Visa, Mastercard, RuPay, American Express
- Encrypted card number and CVV storage
- Credit limit and billing cycle tracking
- Available credit calculation
- Amount owed tracking (negative balance = debt)
- Card number auto-formatting (1234 5678 9012 3456)
- Toggle visibility for card details
- Integrated with transactions and transfers

#### Transactions
- Income and expense recording
- GenericForeignKey for polymorphic account references
- Support for bank accounts and credit cards
- Multiple payment methods (UPI, Card, Netbanking, Cash, Wallet, IMPS, NEFT, RTGS)
- Category-based classification
- Date/time tracking in IST
- Soft delete support
- Transaction history with filtering
- Emoji indicators for account types (🏬 Bank, 💳 Credit Card)

#### Double-Entry Ledger
- Journal entries with balanced postings
- Income and Expense control accounts
- Atomic balance updates with select_for_update()
- Balance recalculation from ledger: `python manage.py recalculate_balances`
- Activity logging for all operations

#### Transfers
- Transfer between any account types
- Bank → Bank, Bank → Credit Card, Credit Card → Credit Card, etc.
- Bill payment support (reduces credit card debt)
- Refund handling (credit card → bank)
- Unified view with transactions (tabbed interface)
- Validation prevents transfers between same account
- Insufficient balance validation for bank accounts

#### Categories
- Hierarchical category structure (3-level max)
- Income and expense categories
- Color customization
- Icon support
- Deletion protection (prevents deletion if in use)

#### Dashboard
- Net Worth calculation (bank balances only, excludes credit card debt)
- Total Accounts breakdown ("X Banks • Y Cards")
- Month-to-date Income and Expense
- Recent transactions (last 10) across all account types
- Account type choice modal for quick account creation
- Quick action buttons (New Transaction, Add Account, Transfer Money)

#### Combined Accounts & Cards Page
- Unified page showing both bank accounts and credit cards
- Separate sections with dedicated stats
- Bank stats: Total balance
- Credit card stats: Total limit, Available credit, Amount owed
- Responsive grid layout
- Emoji indicators for easy identification

#### UI/UX
- Dark mode (default) with light mode toggle
- Responsive design (mobile, tablet, desktop)
- Indian number formatting (X,XX,XXX)
- Configurable decimal display (integers for summaries, decimals for details)
- Collapsible sidebar navigation
- Toast notifications for user feedback

### 🚧 Planned Features

#### Investments
- Instrument management (Stocks/Mutual Funds)
- Trade recording (Buy/Sell/Dividend/Fees)
- FIFO lot tracking
- Portfolio holdings view
- P&L calculation (realized/unrealized)

#### Reports
- Net worth tracking over time
- Income vs Expense analysis
- Spend by category
- Account balance summaries
- Export functionality (PDF/CSV)

#### Digital Wallets
- UPI app integration (Google Pay, PhonePe, etc.)
- Mobile wallet management
- UPI ID tracking
- Linked mobile number

#### Cash Accounts
- Physical cash tracking
- Multiple cash locations
- Cash type categorization

#### Fixed Deposits
- FD tracking with maturity dates
- Interest calculation
- Maturity reminders
- Auto-renewal support

#### Loans
- Loan account management
- EMI tracking and payment recording
- Interest calculation
- Outstanding balance monitoring
- Prepayment calculator

## Configuration

### Settings Highlights

- **Timezone**: Asia/Kolkata (IST)
- **Database**: PostgreSQL (localhost for dev, 'db' for Docker)
- **Password Hashing**: Argon2 (recommended)
- **Session Timeout**: 2 weeks (1,209,600 seconds)
- **Static Files**: `/static/` (collected to `/staticfiles/`)
- **Media Files**: `/media/`

### Security

- CSRF protection enabled
- HttpOnly cookies
- Argon2 password hashing
- Minimum password length: 8 characters
- Masked sensitive data in UI

## Development Workflow

1. Create feature branch
2. Implement models in respective app
3. Create and run migrations
4. Implement views and templates
5. Add URL patterns
6. Write tests
7. Update documentation

## Implementation Status

### ✅ Completed Phases

1. **Phase 1: Foundation**
   - Django project setup and app skeleton
   - Database schema design
   - Authentication system
   - Base templates with TailwindCSS
   - Dark/light theme toggle

2. **Phase 2: Account Foundation**
   - BaseAccount abstract model
   - Bank account implementation
   - Account refactoring (Account → BankAccount)
   - Materialized balance tables

3. **Phase 3: Credit Card Integration** (Completed Nov 2025)
   - **3A**: Transaction & Transfer Integration
   - **3B**: Dashboard Integration
   - **3C**: Navigation & Combined Accounts Page
   - **3D**: Account Detail Page Enhancement
   - **3E**: Ledger Service Verification
   - **3F**: Comprehensive Integration Testing (8 test suites)
   - **3G**: Documentation & Cleanup (documentation complete, code cleanup pending)

### 🚧 Current Phase

**Phase 3G: Code Cleanup**
- Add/update docstrings
- Remove debug code
- Ensure consistent formatting
- Add inline comments

### 🔜 Next Phases

4. **Phase 4: Digital Wallets** - Implement wallet accounts
5. **Phase 5: Cash Accounts** - Implement cash tracking
6. **Phase 6: Investments** - Stock and mutual fund tracking
7. **Phase 7: FDs & Loans** - Fixed deposits and loan management
8. **Phase 8: Reports & Analytics** - Financial reporting dashboard

## Documentation

Detailed design documents are available in the `documents/` folder:
- **FDD (Functional Design Document)**: `/documents/fdd/v1.md`
- **SDD (System Design Document)**: `/documents/sdd/v1.md`

## Contributing

This is a personal project. If you'd like to contribute, please follow the coding standards and architecture outlined in the design documents.

## License

[Add your license here]

## Support

For issues or questions, refer to the FDD and SDD documentation.
