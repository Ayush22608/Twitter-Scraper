from flask import Flask, render_template, jsonify
from scraper import scrape_twitter

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run_script", methods=["GET"])
def run_script():
    result = scrape_twitter()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug=True)
