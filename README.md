# Fin Tracker

A browser-based personal expense tracker with daily logging and end-of-month reporting. Deploy to Netlify in minutes!

**What it does**
- Add, edit, and delete expenses from a web dashboard.
- Track today's spending separately from the current month's total.
- Show a monthly report with category breakdowns, daily totals, average spend, and busiest day.
- Store data locally in SQLite (or cloud database for persistence).

**Run it locally**
1. Install Python 3.8+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the web app:

```bash
python main.py
```

4. Open the app in your browser at `http://127.0.0.1:5000/`.

## Deploy to Netlify

1. Push this repo to GitHub.
2. Go to [netlify.com](https://netlify.com) and sign up.
3. Click **Add new site** → **Import an existing project**.
4. Select your GitHub repo.
5. Set environment variables:
   - `FIN_TRACK_SECRET`: Generate a strong random string
   - `FLASK_ENV`: `production`
6. Deploy!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup and alternatives.

**Project layout**
- `main.py` starts the Flask app locally.
- `app.py` contains the routes and page logic.
- `expense_store.py` manages the SQLite database in `data/expenses.db`.
- `netlify/functions/api.py` wraps the Flask app for Netlify Functions.
- `templates/` contains the dashboard, report, and edit pages.
- `static/styles.css` holds the UI styling.
