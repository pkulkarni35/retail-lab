from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/items")
def items():
    sample_inventory = [
        {"id": 1, "name": "Shoe", "stock": 10},
        {"id": 2, "name": "T-Shirt", "stock": 25},
    ]
    return jsonify(sample_inventory)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
