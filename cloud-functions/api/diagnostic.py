from flask import Flask
import sqlite3
import os
import traceback

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def diagnostic(path):
    try:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "selectionday.db"
        )

        conn = sqlite3.connect(db_path)
        conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = conn.fetchall()
        conn.close()

        return f"DB OK | Path: {db_path} | Tables: {tables}"

    except Exception:
        return "DB FAILED\n\n" + traceback.format_exc(), 500