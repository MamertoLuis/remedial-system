# UBUNTU_DEPLOYMENT_CHECKLIST.md

## Django Banking System (Ubuntu + Gunicorn + PostgreSQL)

---

# 0️⃣ Pre-Deployment Assumptions

* Ubuntu 22.04 LTS
* Python 3.11+
* PostgreSQL installed
* Project follows your AGENTS.md architecture
* `.env` file exists

---

# 1️⃣ System Preparation

## Update system

```bash
sudo apt update
sudo apt upgrade -y
```

---

## Install required packages

```bash
sudo apt install python3-pip python3-venv \
postgresql postgresql-contrib \
build-essential libpq-dev -y
```

---

# 2️⃣ Create Dedicated System User (Important)

Never run Django as root.

```bash
sudo adduser django
sudo usermod -aG www-data django
```

Switch user:

```bash
su - django
```

---

# 3️⃣ Setup Project Directory

```bash
mkdir ~/apps
cd ~/apps
git clone <your-repo>
cd project
```

---

# 4️⃣ Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

# 5️⃣ Configure Environment Variables

Create `.env`:

```
DEBUG=False
SECRET_KEY=super-secret-key
ALLOWED_HOSTS=yourdomain.com,server_ip

DB_NAME=bankdb
DB_USER=bankuser
DB_PASSWORD=securepassword
DB_HOST=localhost
DB_PORT=5432
```

---

# 6️⃣ PostgreSQL Setup

Switch to postgres user:

```bash
sudo -u postgres psql
```

Create DB:

```sql
CREATE DATABASE bankdb;
CREATE USER bankuser WITH PASSWORD 'securepassword';
ALTER ROLE bankuser SET client_encoding TO 'utf8';
ALTER ROLE bankuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE bankuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bankdb TO bankuser;
\q
```

---

# 7️⃣ Django Production Settings

Ensure:

```python
DEBUG = False

ALLOWED_HOSTS = ["yourdomain.com", "server_ip"]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

---

# 8️⃣ Collect Static Files

```bash
python manage.py collectstatic
```

Must succeed before starting Gunicorn.

---

# 9️⃣ Apply Migrations

```bash
python manage.py migrate
```

---

# 🔟 Create Superuser

```bash
python manage.py createsuperuser
```

---

# 1️⃣1️⃣ Test Gunicorn Manually

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Test from browser:

```
http://server_ip:8000
```

If working → proceed.

---

# 1️⃣2️⃣ Create Gunicorn Systemd Service (Production-Ready)

Create:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add:

```ini
[Unit]
Description=Gunicorn Django Application
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/apps/project
ExecStart=/home/django/apps/project/venv/bin/gunicorn \
          config.wsgi:application \
          --workers 3 \
          --bind unix:/home/django/apps/project/gunicorn.sock \
          --timeout 60

[Install]
WantedBy=multi-user.target
```

Reload:

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

Check status:

```bash
sudo systemctl status gunicorn
```

---

# 1️⃣3️⃣ Firewall Configuration

Allow HTTP:

```bash
sudo ufw allow 8000
sudo ufw enable
```

If using Nginx later:

```bash
sudo ufw allow 'Nginx Full'
```

---

# 1️⃣4️⃣ Security Hardening (Minimum Required)

### Disable root SSH login

```bash
sudo nano /etc/ssh/sshd_config
```

Set:

```
PermitRootLogin no
PasswordAuthentication no  (if using SSH keys)
```

Restart:

```bash
sudo systemctl restart ssh
```

---

### Install Fail2Ban

```bash
sudo apt install fail2ban -y
```

---

# 1️⃣5️⃣ Performance Tuning (Small VPS)

If 2GB RAM:

Edit PostgreSQL config:

```
shared_buffers = 256MB
```

Restart:

```bash
sudo systemctl restart postgresql
```

---

# 1️⃣6️⃣ Logging Setup

Ensure Gunicorn logs are accessible:

Add to systemd service:

```
StandardOutput=journal
StandardError=journal
```

View logs:

```bash
journalctl -u gunicorn -f
```

---

# 1️⃣7️⃣ Backup Strategy (Critical for Banking)

Daily DB backup:

```bash
pg_dump bankdb > bankdb_$(date +%F).sql
```

Automate via cron:

```bash
crontab -e
```

Add:

```
0 2 * * * pg_dump bankdb > /home/django/backups/bankdb_$(date +\%F).sql
```

---

# 1️⃣8️⃣ Final Go-Live Checklist

* [ ] DEBUG = False
* [ ] SECRET_KEY not default
* [ ] ALLOWED_HOSTS correct
* [ ] collectstatic run
* [ ] Migrations applied
* [ ] Gunicorn running
* [ ] PostgreSQL secured
* [ ] Firewall enabled
* [ ] SSH hardened
* [ ] Daily backup configured
* [ ] Logs monitored

---

# 1️⃣9️⃣ Common Deployment Mistakes

❌ Running as root
❌ Leaving DEBUG=True
❌ Not running collectstatic
❌ Not configuring ALLOWED_HOSTS
❌ No DB backups
❌ No firewall

---

# 2️⃣0️⃣ Optional (When System Grows)

Add:

* Nginx reverse proxy
* HTTPS (Certbot)
* Redis (if caching needed)
* Read replica DB (for heavy reporting)

Not needed initially.

---

# Final Philosophy for Rural Banking Deployment

> Keep it simple.
> Keep it stable.
> Keep it auditable.
> Avoid unnecessary moving parts.

