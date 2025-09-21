from flask import Flask
from .pages import bp

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)