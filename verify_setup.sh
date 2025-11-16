#!/bin/bash
# Setup verification script for Financio project

echo "=== Financio Setup Verification ==="
echo ""

# Check if virtual environment exists
if [ -d "financio_suite/.venv" ]; then
    echo "✓ Virtual environment exists"
else
    echo "✗ Virtual environment not found"
fi

# Activate virtual environment and run checks
cd financio_suite
source .venv/bin/activate 2>/dev/null || true

# Check Django version
echo ""
echo "=== Installed Packages ==="
pip show django | grep Version

# Check all apps are recognized
echo ""
echo "=== Custom Django Apps ==="
python manage.py shell -c "from django.conf import settings; apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django.contrib')]; [print(f'  ✓ {app}') for app in apps]" 2>/dev/null

# Run system checks
echo ""
echo "=== Django System Check ==="
python manage.py check

# Check database connection
echo ""
echo "=== Database Status ==="
python manage.py showmigrations --plan | head -5

echo ""
echo "=== Setup verification complete! ==="
echo ""
echo "To run the development server:"
echo "  cd financio_suite"
echo "  source .venv/bin/activate"
echo "  python manage.py runserver"
