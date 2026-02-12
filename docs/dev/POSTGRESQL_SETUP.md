# PostgreSQL Setup Guide for Remedial Recovery Management System

## Database Setup

### 1. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Or if using Docker
docker run --name postgres-remedial \
  -e POSTGRES_DB=remedial_db \
  -e POSTGRES_USER=remedial_user \
  -e POSTGRES_PASSWORD=remedial_password \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Create Database and User
```sql
-- Connect to PostgreSQL
sudo -u postgres psql

-- Create database
CREATE DATABASE remedial_db;

-- Create user with password
CREATE USER remedial_user WITH PASSWORD 'remedial_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE remedial_db TO remedial_user;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO remedial_user;

-- Grant all on all tables in public schema (can be more restrictive)
GRANT ALL ON ALL TABLES IN SCHEMA public TO remedial_user;

-- Grant all on sequences (for auto-increment fields)
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO remedial_user;

-- Grant all on all functions in public schema
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO remedial_user;

\q
```

### 3. Configure Remote Access (if needed)
Edit `/etc/postgresql/15/main/postgresql.conf`:
```ini
listen_addresses = '*'
```

Edit `/etc/postgresql/15/main/pg_hba.conf`:
```ini
# Allow remote connections
host    all             all             0.0.0.0/0               md5
```

### 4. Restart PostgreSQL
```bash
sudo systemctl restart postgresql
```

## Django Configuration Update

### 1. Install PostgreSQL Adapter
```bash
source .venv/bin/activate
pip install psycopg[binary]
```

### 2. Update Django Settings
Replace SQLite configuration in `remedial_project/settings.py`:

```python
# PostgreSQL configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'remedial_db',
        'USER': 'remedial_user',
        'PASSWORD': 'remedial_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

### 3. Set Environment Variables
Update `.env` file:
```env
DATABASE_URL=postgresql://remedial_user:remedial_password@localhost:5432/remedial_db
```

## Migration Process

### 1. Backup Current Database (Optional)
```bash
source .venv/bin/activate
python manage.py dumpdata > backup.json
```

### 2. Clean Database
```bash
# Drop all tables and recreate schema
python manage.py flush
```

### 3. Recreate Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Load Data (if backed up)
```bash
python manage.py loaddata backup.json
```

## Connection Testing

### 1. Test Connection
```bash
# Test Django database connection
source .venv/bin/activate
python manage.py dbshell
```

### 2. Verify All Models
```python
python manage.py shell
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> cursor.execute("SELECT version();")
>>> print(cursor.fetchone())
```

## Production Considerations

### 1. Connection Pooling
```python
# settings.py - use connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'remedial_db',
        'USER': 'remedial_user',
        'PASSWORD': 'remedial_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,  # Persistent connections
    }
}
```

### 2. Database Settings for Performance
```python
# Optional performance tuning
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c timezone=UTC'
}
```

### 3. Security Hardening
```sql
-- Create restricted user for production
CREATE USER remedial_app WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE remedial_db TO remedial_app;
GRANT USAGE ON SCHEMA public TO remedial_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO remedial_app;
```

## Troubleshooting

### Common Issues:
1. **Connection Timeout**: Increase `connect_timeout` in Django settings
2. **Permission Denied**: Check user privileges and database ownership
3. **Database Not Found**: Verify DATABASE_URL matches actual database name

### Testing Commands:
```bash
# Test connection from command line
psql -h localhost -U remedial_user -d remedial_db -c "SELECT 1;"

# Check PostgreSQL status
systemctl status postgresql

# Check port listening
netstat -tlnp | grep 5432
```

This setup provides a complete PostgreSQL configuration for the remedial recovery management system with proper security and performance considerations.