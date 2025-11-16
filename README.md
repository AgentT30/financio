# Financio - Personal Finance Management System

A self-hosted personal finance management application built with Django, PostgreSQL, TailwindCSS, and Vanilla JavaScript.

## Project Overview

Financio is designed to help users track and manage their personal finances, including:
- Multiple account types (Bank, Credit Card, Wallet, Cash, FD, Loans)
- Income and expense transactions
- Transfers between accounts
- Investment tracking (Stocks and Mutual Funds)
- Fixed deposits and loans management
- Financial reports and analytics
- Activity logging

## Tech Stack

- **Backend**: Django 5.2.8 (Python)
- **Database**: PostgreSQL 16
- **Frontend**: TailwindCSS + Vanilla JavaScript (AJAX)
- **Deployment**: Docker Compose
- **Theme**: Dark mode (default) with light mode toggle

## Project Structure

```
financio/
├── documents/              # FDD and SDD documentation
│   ├── fdd/v1.md
│   └── sdd/v1.md
├── financio_suite/         # Django project root
│   ├── manage.py
│   ├── financio_suite/     # Project settings
│   ├── core/               # Shared utilities
│   ├── authn/              # Authentication
│   ├── accounts/           # Account management
│   ├── transactions/       # Transaction tracking
│   ├── ledger/             # Double-entry ledger
│   ├── transfers/          # Account transfers
│   ├── categories/         # Transaction categories
│   ├── investments/        # Investment management
│   ├── fds/                # Fixed deposits
│   ├── loans/              # Loan tracking
│   ├── reports/            # Financial reports
│   ├── activity/           # Activity logging
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

- **core**: Shared utilities, middleware, and common templates
- **authn**: User authentication (signup, login, logout, password management)
- **accounts**: Account management for different account types
- **transactions**: Transaction recording and management
- **ledger**: Double-entry ledger implementation
- **transfers**: Fund transfers between accounts
- **categories**: Transaction categorization
- **investments**: Stock and mutual fund investment tracking
- **fds**: Fixed deposit management
- **loans**: Loan tracking and EMI recording
- **reports**: Financial analytics and reporting
- **activity**: User activity logging
- **ui**: Shared UI components and templates

## Key Features (Planned)

### Authentication
- Email/password login and signup
- 2-week session timeout
- Password change functionality

### Accounts
- Support for multiple account types
- Masked account numbers (last 4 digits visible)
- Balance tracking
- Account archival

### Transactions
- Credit (income) and debit (expense) tracking
- Multiple payment methods (UPI, Card, Netbanking, Cash, Wallet)
- Category-based classification
- Date range filtering and search

### Investments
- Instrument management (Stocks/Mutual Funds)
- Trade recording (Buy/Sell/Dividend/Fees)
- FIFO lot tracking
- Portfolio holdings view

### Reports
- Net worth tracking
- Income vs Expense analysis
- Spend by category
- Account balance summaries

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

## Next Steps

1. ✅ Django project setup and app skeleton creation
2. 🔄 Database schema design and model creation
3. ⏳ Authentication system implementation
4. ⏳ Account management module
5. ⏳ Transaction tracking system
6. ⏳ Dashboard and reporting
7. ⏳ Frontend UI with TailwindCSS

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
