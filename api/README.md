# Expense Tracker API — start here

Everything is ready. You only need two double-clicks.

## Step 1 — setup (only once)

Double-click **`setup.bat`**

It finds Python, creates the virtual environment, and installs FastAPI.
When it says `SETUP DONE`, go to step 2.
If it says `SETUP FAILED`, copy the whole black window and send it to Claude.

## Step 2 — run the server

Double-click **`run.bat`**

Your browser opens on `http://127.0.0.1:8000/docs`.
You should see a page listing `GET /health`. Click it, click **Try it out**, click **Execute**.
You should get code `200` and `{"status": "ok"}`.

Leave the black window open while you work. It is the server.
Press `CTRL+C` in it to stop.

## Step 3 — your turn

Open `main.py`. At the bottom there is a task: write `GET /settings`.

Save the file. The server restarts by itself (watch the black window).
Refresh `/docs` and your new endpoint appears there.

## What each file is

| File | What it is |
|---|---|
| `main.py` | The server code. This is the only file you edit. |
| `requirements.txt` | The list of packages the project needs. |
| `setup.bat` | Creates `.venv` and installs the packages. Run once. |
| `run.bat` | Starts the server. Run every time you work. |
| `.venv/` | The installed packages. Never edit, never upload to GitHub. |
| `.gitignore` | Tells git which files to ignore. |

## If something breaks

Send Claude the text of the error, exactly as it is. Do not try to fix it first.
