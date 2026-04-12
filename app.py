from flask import Flask
from routes.partidos import partidos_bp

app = Flask(__name__)

app.register_blueprint(partidos_bp)


@app.route("/")
def home():
    return "Hola"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
