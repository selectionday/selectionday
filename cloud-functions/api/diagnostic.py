from flask import Flask
import sys
import traceback

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def diagnostic(path):
    try:
        import maths_data

        return (
            "DIAGNOSTIC OK | "
            "maths_data import works | "
            f"Python: {sys.version}"
        )

    except Exception:
        return (
            "DIAGNOSTIC FAILED\n\n"
            + traceback.format_exc()
        ), 500