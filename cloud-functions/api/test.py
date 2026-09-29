from flask import Flask, request

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def test(path):
    return f"EDGEONE PYTHON FUNCTION WORKS | Flask path: /{path} | URL path: {request.path}"