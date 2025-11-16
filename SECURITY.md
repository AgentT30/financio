# Security Configuration Guide

## Environment Variables Setup

### For Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Generate a new encryption key:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

3. Update `.env` with your keys:
   - `SECRET_KEY` - Django secret key (generate new for production)
   - `FIELD_ENCRYPTION_KEY` - Fernet encryption key from step 2

### For Production/Docker

1. Set environment variables in your deployment platform or docker-compose:
   ```yaml
   environment:
     - SECRET_KEY=${SECRET_KEY}
     - FIELD_ENCRYPTION_KEY=${FIELD_ENCRYPTION_KEY}
     - DEBUG=False
   ```

2. **NEVER commit `.env` file to git** - It's already in `.gitignore`

## What Gets Encrypted

The `FIELD_ENCRYPTION_KEY` is used to encrypt:
- Account numbers (full number)
- Any other sensitive financial data added in future

## Key Safety

⚠️ **IMPORTANT**: 
- Keep your encryption keys secure
- Never commit encryption keys to git
- Use different keys for dev/staging/production
- If you lose the encryption key, encrypted data cannot be recovered
- Changing the key will make existing encrypted data unreadable

## Files That Are Safe to Commit

✅ **Safe to commit:**
- `settings.py` (now uses environment variables)
- `.env.example` (template only, no real keys)
- All model files
- Migration files

❌ **NEVER commit:**
- `.env` (contains actual keys)
- Local database files
- Media uploads

## Verify Your Setup

Run this to make sure environment variables are loaded:
```bash
python manage.py check
```

If you see "System check identified no issues" - you're good to go!
