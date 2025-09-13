from flask import Flask
from pages import bp

run = Flask(__name__)
run.register_blueprint(bp)

if __name__ == "__main__":
    run.run(host="localhost", port=8080, debug=True)