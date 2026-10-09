# UDAAN — Student + Subject Teacher Portal

UDAAN is a Flask-based academic portal with role-specific dashboards for students, class teachers, subject teachers, and support staff.

## Technology stack

- **Backend:** Python 3.10+ and Flask
- **Database:** SQLite for local development; MySQL is supported when explicitly configured
- **Authentication:** Flask server-side sessions and Werkzeug password hashing
- **Frontend:** HTML templates, CSS, and vanilla JavaScript
- **Configuration:** environment variables loaded with python-dotenv
- **Tests:** Python unittest and Flask's test client

## Run locally (Windows)

1. Install Python 3.10 or newer.
2. Open a terminal in the repository root.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env`. For local development, `DB_ENGINE=sqlite` is the default. Keep `FLASK_DEBUG=0`.
6. Initialize/seed a **disposable local demo database only**:

   ```powershell
   py database/seed_demo_data.py
   ```

   The seeder refuses to run over a database containing users unless `--reset` is explicitly supplied. **Never use `--reset` with real or valuable data.**

7. Start the server:

   ```powershell
   py app.py
   ```

8. Open http://127.0.0.1:5000. Do not open the HTML files directly or use Live Server; the app relies on Flask routes, templates, and APIs.

## MySQL

Set `DB_ENGINE=mysql` and configure `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` in your untracked `.env`. The app intentionally fails if the selected database is unavailable rather than silently writing to another database. Create the schema using the project's database initialization workflow before running the app.

## Tests

Run:

```powershell
py -m unittest tests_backend.py
```

The current test suite has not been verified in this environment. Ensure tests use a disposable test database before running them; do not point tests at a database containing real records.

## Security and deployment notes

- Never commit `.env`, production credentials, or real student data.
- Production must set a strong random `SECRET_KEY`, `FLASK_ENV=production`, and `DB_ENGINE=mysql` as appropriate.
- Run behind a production WSGI server and HTTPS reverse proxy; do not expose Flask's development server to the internet.
- Before storing real student records, complete CSRF protection for cookie-authenticated state-changing routes, login rate limiting, and the authorization regression tests for cross-class marks and cross-student tickets.
- Treat demo seed data as synthetic. Do not use it on production databases.

## Project structure

- `app.py` — Flask routes, session authentication, authorization, and APIs
- `config.py` — environment-driven configuration
- `database/db.py` — database connections and query helpers
- `database/seed_demo_data.py` — demo data seeder
- `templates/` — Flask-rendered pages
- `static/` — CSS and JavaScript assets
- `tests_backend.py` — backend tests
