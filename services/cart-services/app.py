import os
import time
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

cart_items = []

DD_API_KEY = os.getenv("DD_API_KEY")
DD_SITE = os.getenv("DD_SITE", "datadoghq.com")


def send_dd_metric(metric_name: str, value: float, tags: list[str] | None = None, metric_type: str = "count"):
    """
    Fire-and-forget Datadog metric sender using HTTP API.
    """
    if not DD_API_KEY:
        return

    if tags is None:
        tags = []

    payload = {
        "series": [
            {
                "metric": metric_name,
                "points": [[int(time.time()), value]],
                "type": metric_type,
                "tags": tags,
            }
        ]
    }

    def _send():
        try:
            url = f"https://api.{DD_SITE}/api/v1/series"
            headers = {
                "Content-Type": "application/json",
                "DD-API-KEY": DD_API_KEY,
            }
            requests.post(url, json=payload, headers=headers, timeout=2)
        except Exception:
            # Don't break user traffic if metrics fail
            pass

    threading.Thread(target=_send, daemon=True).start()


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "cart-service"}), 200


@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    name = data.get("name", "unknown")
    qty = data.get("qty", 1)

    if not item_id:
        send_dd_metric(
            "retail.cart.add_to_cart",
            1,
            tags=[
                "env:retail-lab",
                "service:cart-service",
                "status:error",
                "reason:missing_item_id",
            ],
        )
        return jsonify({"error": "item_id is required"}), 400

    cart_items.append({"item_id": item_id, "name": name, "qty": qty})

    send_dd_metric(
        "retail.cart.add_to_cart",
        1,
        tags=[
            "env:retail-lab",
            "service:cart-service",
            "status:success",
        ],
    )

    return jsonify(
        {
            "message": "item added",
            "cart_size": len(cart_items),
            "items": cart_items,
        }
    ), 200


@app.route("/cart", methods=["GET"])
def get_cart():
    return jsonify({"items": cart_items, "count": len(cart_items)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
