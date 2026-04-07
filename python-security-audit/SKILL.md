---
name: python-security-audit
description: >
  Use when user requests "security review", "audit security", "check for
  vulnerabilities" in a Python project, or when python-code-review
  identifies auth, payment, or PII handling code needing a security pass.
  NOT automatic — must be explicitly requested or offered by python-code-review.
---

# Security Audit for Python Applications

You are a security expert reviewing Python server applications.
Your job is to identify vulnerabilities before they reach production, with
particular focus on OWASP Top 10 risks adapted for the Python ecosystem.

## Prerequisites

**This skill builds on [`security-audit-principles`] and [`python-dev`]**.

Apply all rules from:
- **`security-audit-principles`**: OWASP Top 10 vulnerability categories and severity assessment, security audit workflow and reporting format, why security audits matter and cost of production discovery
- **`python-dev`**: Python safety patterns, type hints, input validation, testing practices

Then apply the Python-specific security audit patterns below.

## Workflow

Follow the `security-audit-principles` workflow (Steps 1–4). Python-specific Step 3 example:

```
🔴 CRITICAL — views.py:42
SQL Injection: query built with string formatting allows arbitrary SQL
execution. Attacker can dump the database or modify records.

Suggested fix:
  Use parameterized query:
  cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
```

Step 2 uses the Python Security Checklist below in place of the generic OWASP categories.

**If no CRITICAL findings:**
> "✅ No critical vulnerabilities found. [N warnings / notes listed above.]
> Consider addressing warnings for defense-in-depth."

---

## Security Checklist

### 🔴 A01 — Injection (OWASP #1)

**SQL Injection** — never build queries with string formatting:
```python
# ❌ BAD: SQL injection vulnerability
cursor.execute(f"SELECT * FROM users WHERE name = '{request.args['name']}'")

# ✅ GOOD: Parameterized query (psycopg2 / sqlite3)
cursor.execute('SELECT * FROM users WHERE name = %s', (request.args['name'],))

# ✅ GOOD: SQLAlchemy ORM (parameterized automatically)
user = session.query(User).filter(User.name == name).first()

# ✅ GOOD: SQLAlchemy Core with text() — still must bind params
from sqlalchemy import text
result = session.execute(text('SELECT * FROM users WHERE name = :name'), {'name': name})
```

**Command Injection** — never pass user input to a shell:
```python
import os, subprocess

# ❌ BAD: Attacker can inject: "file.jpg; rm -rf /"
os.system(f"convert {request.form['filename']} output.pdf")
subprocess.run(request.form['cmd'], shell=True)

# ✅ GOOD: Validate input strictly; pass as list (no shell)
import re
filename = request.form['filename']
if not re.fullmatch(r'[\w.-]+', filename):
    raise ValueError('Invalid filename')
subprocess.run(['convert', filename, 'output.pdf'])
```

**Template Injection** — never render user content as a Jinja2 template:
```python
from flask import render_template_string

# ❌ BAD: User controls template source — can execute arbitrary Python
render_template_string(request.args['tmpl'])

# ✅ GOOD: Render a fixed template, pass user input as context variable
render_template_string('<h1>Hello {{ name }}</h1>', name=request.args['name'])
# Or better: use a file-based template
render_template('greeting.html', name=request.args['name'])
```

**LDAP / XML Injection** — sanitize input before building queries:
- Use a validated LDAP library (e.g., `python-ldap` with parameterized filters)
- Parse XML with `defusedxml` to prevent XXE attacks (`lxml` is not safe by default)

### 🔴 A02 — Broken Authentication (OWASP #2)

**Hardcoded secrets:**
```python
# ❌ BAD: Secret in source code
SECRET_KEY = 'my-super-secret-key'
DATABASE_URL = 'postgresql://admin:password@localhost/mydb'

# ✅ GOOD: Load from environment with python-dotenv
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.environ['SECRET_KEY']   # fails fast if missing
DATABASE_URL = os.environ['DATABASE_URL']
```

**Weak password hashing:**
```python
import hashlib

# ❌ BAD: MD5 / SHA-1 are trivially reversible
hashed = hashlib.md5(password.encode()).hexdigest()
hashed = hashlib.sha1(password.encode()).hexdigest()

# ✅ GOOD: bcrypt (cost factor >= 12)
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
valid = bcrypt.checkpw(password.encode(), hashed)

# ✅ ALSO GOOD: argon2-cffi (preferred for new projects)
from argon2 import PasswordHasher
ph = PasswordHasher()
hashed = ph.hash(password)
ph.verify(hashed, password)   # raises VerifyMismatchError on failure
```

**Missing rate limiting on auth endpoints:**
```python
# ❌ BAD: No rate limiting — credential stuffing trivial
@app.route('/login', methods=['POST'])
def login():
    ...

# ✅ GOOD: Apply rate limiting with slowapi (Flask) or django-ratelimit
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

@app.route('/login', methods=['POST'])
@limiter.limit('10/15minute')
def login():
    ...
```

**JWT vulnerabilities:**
```python
import jwt

# ❌ BAD: No algorithm pinning (algorithm confusion attack)
payload = jwt.decode(token, secret, options={'verify_signature': False})

# ❌ BAD: No expiry set — tokens are valid forever
token = jwt.encode({'user_id': user_id}, secret)

# ✅ GOOD: Explicit algorithm, expiry, strong secret
from datetime import datetime, timedelta, timezone
token = jwt.encode(
    {'user_id': user_id, 'exp': datetime.now(timezone.utc) + timedelta(minutes=15)},
    os.environ['JWT_SECRET'],
    algorithm='HS256',
)
payload = jwt.decode(token, os.environ['JWT_SECRET'], algorithms=['HS256'])
```

**Session fixation in Flask / Django:**
- Call `session.regenerate()` or equivalent after login
- In Flask: use `flask-login`; in Django: call `request.session.cycle_key()` post-login

### 🔴 A03 — Broken Access Control (OWASP #3)

**Missing authentication decorator (IDOR):**
```python
# ❌ BAD: Any unauthenticated user can delete any order
@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    Order.query.filter_by(id=order_id).delete()
    db.session.commit()

# ✅ GOOD: Require login; verify ownership before operation
from flask_login import login_required, current_user

@app.route('/orders/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    db.session.delete(order)
    db.session.commit()
```

**Path traversal:**
```python
import os

# ❌ BAD: Attacker requests ../../etc/passwd
filename = request.args['filename']
with open(os.path.join('/uploads', filename)) as f:
    return f.read()

# ✅ GOOD: Resolve and validate path is within the upload directory
from pathlib import Path
base = Path('/uploads').resolve()
target = (base / filename).resolve()
if not str(target).startswith(str(base)):
    abort(400, 'Invalid path')
with target.open() as f:
    return f.read()
```

**Mass assignment via model constructors:**
```python
# ❌ BAD: Attacker sends { "is_admin": true } in JSON body
user = User(**request.json)

# ✅ GOOD: Allowlist via Pydantic / marshmallow schema
from pydantic import BaseModel

class UpdateProfileSchema(BaseModel):
    name: str
    email: str
    # is_admin is not in schema — Pydantic will reject unknown fields by default
    model_config = {'extra': 'forbid'}

data = UpdateProfileSchema.model_validate(request.json)
user.name = data.name
user.email = data.email
```

### 🔴 A04 — Cryptographic Failures (OWASP #4)

**`pickle` deserialisation of untrusted data (CRITICAL — RCE):**
```python
import pickle

# ❌ CRITICAL: Arbitrary code execution — never deserialize untrusted data
obj = pickle.loads(request.data)

# ✅ GOOD: Use JSON or a safe schema-validated format
import json
from pydantic import BaseModel
raw = json.loads(request.data)
obj = SafeSchema.model_validate(raw)
```

**`yaml.load()` without Loader:**
```python
import yaml

# ❌ BAD: Executes arbitrary Python via !!python/object tags
data = yaml.load(user_input)

# ✅ GOOD: Use safe_load — disables arbitrary object construction
data = yaml.safe_load(user_input)
```

**Insecure random for tokens:**
```python
import random

# ❌ BAD: random module is predictable — not suitable for security tokens
reset_token = str(random.getrandbits(128))

# ✅ GOOD: secrets module (cryptographically secure)
import secrets
reset_token = secrets.token_hex(32)   # 256 bits of randomness
api_key = secrets.token_urlsafe(32)
```

**Sensitive data in logs:**
```python
import logging

# ❌ BAD: Logs full user object — exposes password hash, tokens, PII
logging.debug('Authenticated user: %s', user.__dict__)

# ✅ GOOD: Log only safe identifiers
logging.info('User authenticated: user_id=%s', user.id)
```

### 🔴 A05 — Security Misconfiguration (OWASP #5)

**`DEBUG=True` in production:**
```python
# ❌ BAD: Shows full stack traces and interactive debugger to any visitor
app = Flask(__name__)
app.config['DEBUG'] = True

# ✅ GOOD: Driven by environment variable, defaults to False
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
# Django equivalent:
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
```

**Verbose error messages:**
```python
# ❌ BAD: Stack trace leaks file paths and library versions
@app.errorhandler(500)
def server_error(e):
    return str(e), 500

# ✅ GOOD: Log server-side; return generic message
@app.errorhandler(500)
def server_error(e):
    app.logger.exception('Unhandled error')
    return {'error': 'Internal server error'}, 500
```

**Missing security headers:**
```python
# ❌ BAD: No security headers — clickjacking, MIME sniffing, XSS risks
app = Flask(__name__)

# ✅ GOOD: Use flask-talisman (sets HSTS, CSP, X-Frame-Options, etc.)
from flask_talisman import Talisman
Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': "'self'",
})
# Django: install django-csp and add to MIDDLEWARE
```

**Permissive CORS:**
```python
from flask_cors import CORS

# ❌ BAD: Any origin can make cross-origin requests
CORS(app, origins='*')

# ✅ GOOD: Explicit allowlist
CORS(app, origins=['https://app.example.com', 'https://admin.example.com'])
```

### 🟡 A06 — Vulnerable and Outdated Components (OWASP #6)

Run dependency audits:
```bash
# Identify known CVEs
pip audit

# Or use safety (older ecosystem tool)
safety check

# Show all outdated packages
pip list --outdated
```

**Flag for review:**
- Any package with HIGH or CRITICAL severity in `pip audit`
- Packages with no release activity in >2 years
- Transitive dependencies with security advisories

**Note:** `pip audit fix` may pull in breaking changes — always review the diff before committing.

### 🟡 A07 — Mass Assignment / Arbitrary Attribute Setting (OWASP #7 equivalent)

**`setattr` with user-supplied keys:**
```python
# ❌ BAD: Attacker sends { "is_admin": true, "role": "superuser" }
for key, value in request.json.items():
    setattr(user, key, value)

# ✅ GOOD: Only update known, safe attributes
UPDATABLE_FIELDS = {'name', 'email', 'bio'}
for key, value in request.json.items():
    if key in UPDATABLE_FIELDS:
        setattr(user, key, value)
```

**Arbitrary `**kwargs` unpacking from user input:**
```python
# ❌ BAD: User controls constructor arguments — can set any field
User(**request.json)

# ✅ GOOD: Validate first with Pydantic; unpack only validated fields
data = UpdateProfileSchema.model_validate(request.json)
User(**data.model_dump())
```

### 🟡 A08 — SSRF (Server-Side Request Forgery)

**Fetching user-supplied URLs without allowlist:**
```python
import requests

# ❌ BAD: Attacker can hit http://169.254.169.254/latest/meta-data/
@app.route('/fetch')
def fetch():
    url = request.args['url']
    return requests.get(url).text

# ✅ GOOD: Validate against explicit allowlist
ALLOWED_PREFIXES = ('https://api.example.com/', 'https://cdn.example.com/')

@app.route('/fetch')
def fetch():
    url = request.args['url']
    if not url.startswith(ALLOWED_PREFIXES):
        abort(400, 'URL not allowed')
    return requests.get(url, timeout=5).text
```

**Open redirect:**
```python
# ❌ BAD: Attacker: ?next=https://evil.com/phish
next_url = request.args.get('next')
return redirect(next_url)

# ✅ GOOD: Only allow relative paths
from urllib.parse import urlparse

def is_safe_redirect(url):
    parsed = urlparse(url)
    return not parsed.netloc and not parsed.scheme

next_url = request.args.get('next', '/')
return redirect(next_url if is_safe_redirect(next_url) else '/')
```

### 🔵 Defense in Depth

- **Input validation**: Use `pydantic` or `marshmallow` schemas at every external boundary (HTTP, message queues, file uploads)
- **Rate limiting**: Apply `slowapi` (Flask) or `django-ratelimit` to all authentication, registration, and expensive operations
- **Least privilege**: Use a dedicated DB user per service with only required permissions; never use a superuser at runtime
- **Audit logging**: Log all authentication attempts (success and failure), authorization failures, and access to PII/payment data — include user ID, timestamp, action, resource
- **Dependency scanning**: Run `pip audit` in CI; fail on HIGH/CRITICAL findings
- **Secret validation**: Use `python-dotenv` and validate required secrets are present at startup; fail fast rather than running insecurely

---

## Python Security Features

**Leverage these ecosystem tools:**

| Tool | Purpose | Notes |
|------|---------|-------|
| `secrets` | Cryptographically secure random tokens, API keys | Built-in; prefer over `random` for any security use |
| `hashlib` + `hmac` | Hashing and message authentication | Use for checksums; never for password storage |
| `bcrypt` | Password hashing | Cost factor >= 12 |
| `argon2-cffi` | Password hashing (preferred for new projects) | State-of-the-art; use `argon2.PasswordHasher` |
| `pydantic` | Input validation with type enforcement | `model_config = {'extra': 'forbid'}` strips unknown fields |
| `marshmallow` | Schema-based serialization / validation | Alternative to Pydantic; good for SQLAlchemy integration |
| `python-dotenv` | Load `.env` files into `os.environ` | Always validate required vars at startup |
| `defusedxml` | Safe XML parsing (prevents XXE) | Drop-in replacement for stdlib `xml.*` |
| `bandit` | Static analysis for common security issues | Run in CI: `bandit -r src/` |
| `pip audit` | Dependency vulnerability scanning | Replaces `safety check` for CVE detection |
| `flask-talisman` | Security headers for Flask | Sets HSTS, CSP, X-Frame-Options in one call |
| `django-csp` | Content Security Policy for Django | Add to `MIDDLEWARE`; configure per-view |
| `slowapi` | Rate limiting for Flask | Based on `limits`; supports Redis backend |

---

## Common Pitfalls

| Mistake | Impact | Fix |
|---------|--------|-----|
| String-formatting SQL queries | SQL injection — full database compromise | Use parameterized queries (`%s` placeholders) or ORM |
| `pickle.loads()` on untrusted data | Remote code execution — total system compromise | Use JSON + Pydantic schema validation |
| `yaml.load()` without `Loader` | Arbitrary Python object construction | Always use `yaml.safe_load()` |
| `os.system()` or `shell=True` with user input | Command injection — arbitrary OS commands | Validate input; use `subprocess.run` with list args |
| `random` module for tokens | Predictable tokens enable account takeover | Use `secrets.token_hex(32)` for all security tokens |
| `DEBUG=True` in production | Interactive debugger and stack traces exposed | Drive from `os.environ`; default to `False` |
| Logging full objects with PII | PII and secrets exposed in log aggregators | Log only safe identifiers (user_id, email); redact sensitive fields |
| Unpacking `request.json` into model constructor | Mass assignment, privilege escalation | Validate with Pydantic/marshmallow schema first |

---

## Severity Assignment Decision Flow

```mermaid
flowchart TD
    Finding_detected((Finding detected))
    Exploitable_remotely_{Exploitable remotely?}
    Leads_to_data_breach_or_RCE_{Leads to data breach or RCE?}
    Requires_authentication_{Requires authentication?}
    CRITICAL[CRITICAL]
    WARNING[WARNING]
    NOTE[NOTE]
    Finding_detected --> Exploitable_remotely_
    Exploitable_remotely_ -->|yes| Leads_to_data_breach_or_RCE_
    Exploitable_remotely_ -->|"no (local only)"| NOTE
    Leads_to_data_breach_or_RCE_ -->|yes| CRITICAL
    Leads_to_data_breach_or_RCE_ -->|no| Requires_authentication_
    Requires_authentication_ -->|"yes (auth required)"| WARNING
    Requires_authentication_ -->|"no (unauthenticated)"| CRITICAL
```

---

## Skill Chaining

**Invoked by:** [`python-code-review`] when reviewing auth/payment/PII handling (offered as option, not automatic)

**Invokes:** None (terminal skill in the chain)

**Can be invoked independently:** User says "security review", "audit security", or explicitly invokes for security-critical Python implementations

**Works alongside:** `python-code-review` — while python-code-review catches general quality and logic issues, this skill focuses specifically on OWASP Top 10 security vulnerabilities
