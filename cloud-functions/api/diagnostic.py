from flask import Flask
import os

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def diagnostic(path):
    results = []

    for root, dirs, files in os.walk("/var/user"):
        for file in files:
            if file == "selectionday.db":
                results.append(os.path.join(root, file))

    if results:
        return "DB FOUND | " + " | ".join(results)

    return "DB NOT FOUND"