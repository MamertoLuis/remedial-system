# SECURITY_HARDENING_GUIDE.md

## Django Banking System – Ubuntu Production Hardening

---

# 0️⃣ Security Philosophy

For a rural banking system:

> Reduce attack surface.
> Remove unnecessary services.
> Harden access.
> Log everything.
> Assume breach is possible.

Security must exist at **5 layers**:

1. OS
2. Network
3. Application
4. Database
5. Operational Process

---

# 1️⃣ Operating System Hardening (Ubuntu)

---

## ✅ 1.1 Disable Root Login

Edit:

```bash
sudo nano /etc/ssh/sshd_config
```

Set:

```
PermitRootLogin no
PasswordAuthentication no   # if using SSH keys
```

Restart:

```bash
sudo systemctl restart ssh
```

---

## ✅ 1.2 Use SSH Keys Only

Generate key on local machine:

```bash
ssh-keygen
```

Copy to server:

```bash
ssh-copy-id django@server_ip
```

Disable password authentication.

---

## ✅ 1.3 Enable Firewall (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8000
sudo ufw enable
```

Check:

```bash
sudo ufw status
```

---

## ✅ 1.4 Install Fail2Ban

```bash
sudo apt install fail2ban -y
```

Protects from brute-force SSH attacks.

---

## ✅ 1.5 Keep System Updated

```bash
sudo apt update
sudo apt upgrade -y
```

Set up unattended upgrades:

```bash
sudo apt install unattended-upgrades
```

---

# 2️⃣ Application-Level Hardening (Django)

---

## ✅ 2.1 Production Settings

In `settings.py`:

```python
DEBUG = False

ALLOWED_HOSTS = ["yourdomain.com"]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True  # if HTTPS enabled

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

---

## ✅ 2.2 Strong SECRET_KEY

Generate securely:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Store only in `.env`.

Never commit to Git.

---

## ✅ 2.3 Disable Admin for Public IP (Optional Advanced)

Restrict `/admin/` by IP:

```python
if not request.META['REMOTE_ADDR'] in allowed_ips:
    return HttpResponseForbidden()
```

Or protect via VPN.

---

## ✅ 2.4 Limit Login Attempts

Use:

```
django-axes
```

or custom lockout mechanism.

For banking systems, brute-force protection is essential.

---

## ✅ 2.5 Enforce Strong Password Policy

In `settings.py`:

```python
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]
```

Set minimum length ≥ 12.

---

## ✅ 2.6 Enable Audit Logging

Track:

* User
* Action
* Object
* Timestamp
* Tenant

Every workflow action must create an audit log entry.

---

# 3️⃣ Database Hardening (PostgreSQL)

---

## ✅ 3.1 Localhost Only

In `postgresql.conf`:

```
listen_addresses = 'localhost'
```

In `pg_hba.conf`:

```
host    all    all    127.0.0.1/32    md5
```

Restart:

```bash
sudo systemctl restart postgresql
```

---

## ✅ 3.2 Strong DB Password

Never use:

```
postgres / postgres
```

Use random 32+ character passwords.

---

## ✅ 3.3 Restrict Privileges

Do not use superuser DB role for Django.

Only:

```sql
GRANT ALL PRIVILEGES ON DATABASE bankdb TO bankuser;
```

---

## ✅ 3.4 Enable Logging

In `postgresql.conf`:

```
log_connections = on
log_disconnections = on
log_min_duration_statement = 1000
```

---

# 4️⃣ Gunicorn Hardening

---

## ✅ 4.1 Run as Non-Root

Systemd service must use:

```
User=django
Group=www-data
```

---

## ✅ 4.2 Limit Workers

Too many workers = memory exhaustion attack vector.

Use appropriate count.

---

## ✅ 4.3 Timeout Setting

```
--timeout 60
```

Prevents stuck workers.

---

# 5️⃣ HTTPS (Strongly Recommended)

Install Nginx + Certbot:

```bash
sudo apt install nginx certbot python3-certbot-nginx
```

Enable SSL:

```bash
sudo certbot --nginx
```

Force redirect HTTP → HTTPS.

---

# 6️⃣ File System Hardening

---

## ✅ 6.1 Proper Permissions

Project directory:

```bash
chmod -R 750 project
```

`.env`:

```bash
chmod 600 .env
```

---

## ✅ 6.2 Prevent Directory Listing

If using Nginx:

```
autoindex off;
```

---

# 7️⃣ Protect Against Common Attacks

---

## CSRF — Already Built-In

Ensure templates include:

```html
{% csrf_token %}
```

---

## XSS — Avoid Using `|safe`

Never mark user input as safe.

---

## SQL Injection — Use ORM Only

Never raw SQL unless necessary.

---

## Clickjacking

In settings:

```python
X_FRAME_OPTIONS = "DENY"
```

---

# 8️⃣ Backup Security

---

## Encrypt Backups

```bash
gpg -c bankdb_backup.sql
```

---

## Store Backups Offsite

* Separate machine
* Encrypted external drive
* Secure cloud bucket (if allowed)

Never store backups on same disk only.

---

# 9️⃣ Monitoring & Alerts

---

## Monitor:

* Failed login attempts
* High CPU usage
* Memory spikes
* DB connection spikes

Use:

* `htop`
* `journalctl`
* Optional: lightweight monitoring agent

---

# 🔟 Insider Threat Mitigation

For banking:

* Separate duties (maker/checker)
* Restrict admin rights
* Log deletions
* Require approval for critical workflows

---

# 1️⃣1️⃣ Production Readiness Checklist

* [ ] DEBUG=False
* [ ] HTTPS enabled
* [ ] Firewall active
* [ ] SSH hardened
* [ ] DB localhost only
* [ ] Strong passwords
* [ ] Audit logs enabled
* [ ] Backups encrypted
* [ ] Admin restricted
* [ ] Session cookies secure
* [ ] Fail2Ban active

---

# 1️⃣2️⃣ Advanced (Optional Bank-Grade)

* VPN-only access
* 2FA for admin users
* Database encryption at rest
* Encrypted swap
* Intrusion detection (OSSEC)
* Daily vulnerability scan

---

# Final Security Principle

For a rural banking system:

> Security failures are more expensive than downtime.

Harden early.
Audit often.
Keep architecture simple.

