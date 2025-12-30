# Fin Tracker

A small personal finance tracker that supports recording, viewing, updating, searching and visualizing expenses.

**Features**
- **Add Expense:** record amount, category, date, and notes (`fintrack.py`).
- **View Expenses:** list and filter recorded expenses.
- **Update / Delete:** modify or remove existing records.
- **Search Expenses:** search by text, date, or category.
- **GUI:** desktop interface implemented in `fin_gui.py` using `tkinter` and `ttkbootstrap`.
- **Analytics / Charts:** category and monthly expense visualizations using `matplotlib` (`fin_analytics.py`).
- **Database-backed:** persistent storage via the DB connector in `db/db/db_connect.py`.
- **Tests:** basic unit tests in `test_fintrack.py`.

**Technologies Used**
- **Language:** Python 3
- **GUI:** `tkinter` + `ttkbootstrap`
- **Charts:** `matplotlib`
- **Database driver:** `psycopg2` (PostgreSQL)
- **Standard libs:** `datetime`, `os`, and others from the Python stdlib

**Quick Start**
1. Install Python 3.8+.
2. Install dependencies:

```bash
pip install psycopg2-binary matplotlib ttkbootstrap
```

3. Configure your PostgreSQL connection in `db/db/db_connect.py`.
4. Run the app:

```bash
python main.py
```

**Notes**
- If you prefer a different DB adapter (or use local SQLite for quick tests), adjust `db/db/db_connect.py` accordingly.
- Want more detail in this README? Tell me which sections to expand (install, config, examples, screenshots).

**Database (details)**
- **Connector file:** the project uses `db/db/db_connect.py` to create a DB connection.
- **Driver:** `psycopg2` (PostgreSQL). The current connector uses the following default parameters:

```python
import psycopg2

def get_connection():
	conn = psycopg2.connect(
		host="localhost",
		database="fintrack_db",
		user="postgres",
		password="pass123"
	)
	return conn
```

- **What to change:** update the host, database, user, and password in `db/db/db_connect.py` to match your PostgreSQL instance, or replace the connection construction to read from environment variables.
- **Security note:** don't commit production credentials. Prefer using environment variables or a local configuration file excluded from version control. Example using env vars:

```python
import os
import psycopg2

def get_connection():
	return psycopg2.connect(
		host=os.getenv('FIN_DB_HOST', 'localhost'),
		database=os.getenv('FIN_DB_NAME', 'fintrack_db'),
		user=os.getenv('FIN_DB_USER', 'postgres'),
		password=os.getenv('FIN_DB_PASS')
	)
```

- **Quick DB setup:** create the database and user before running the app:

```bash
# (psql)
CREATE DATABASE fintrack_db;
-- create user / set password and grant privileges as needed
```

- **Troubleshooting:** if `get_connection()` returns `None` or prints an error, verify PostgreSQL is running and credentials are correct.
