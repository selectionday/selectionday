from flask import Flask

app = Flask(__name__)

@app.route("/")
def test():
    return "EDGEONE PYTHON FUNCTION WORKS"