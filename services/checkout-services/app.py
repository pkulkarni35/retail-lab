import os
import time
import threading
import requests
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

DD_API_KEY = os.getenv("DD_API_KEY")
DD_SITE = os.getenv("DD_SITE", "datadoghq.com")


def send_dd_metric(metric_name: str, value: float, tags: list[str] | None = None, metric_type: str = "count"):
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
            pass

    threading.Thread(target=_send, daemon=True).start()


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "checkout-service"}), 200


@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "guest")
    cart_total = data.get("cart_total")

    if cart_total is None:
        send_dd_metric(
            "retail.checkout.requests",
            1,
            tags=[
                "env:retail-lab",
                "service:checkout-service",
                "status:error",
                "reason:missing_cart_total",
            ],
        )
        return jsonify({"error": "cart_total is required"}), 400

    latency_ms = random.randint(50, 500)
    time.sleep(latency_ms / 1000.0)

    if random.random() < 0.1:
        send_dd_metric(
            "retail.checkout.requests",
            1,
            tags=[
                "env:retail-lab",
                "service:checkout-service",
                "status:failed",
            ],
        )
        send_dd_metric(
            "retail.checkout.latency_ms",
            latency_ms,
            tags=[
                "env:retail-lab",
                "service:checkout-service",
                "status:failed",
            ],
            metric_type="gauge",
        )
        return jsonify(
            {
                "status": "failed",
                "reason": "checkout_error",
                "user_id": user_id,
                "cart_total": cart_total,
                "latency_ms": latency_ms,
            }
        ), 500

    send_dd_metric(
        "retail.checkout.requests",
        1,
        tags=[
            "env:retail-lab",
            "service:checkout-service",
            "status:success",
        ],
    )
    send_dd_metric(
        "retail.checkout.latency_ms",
        latency_ms,
        tags=[
            "env:retail-lab",
            "service:checkout-service",
            "status:success",
        ],
        metric_type="gauge",
    )

    return jsonify(
        {
            "status": "success",
            "order_id": f"order_{random.randint(100000, 999999)}",
            "user_id": user_id,
            "cart_total": cart_total,
            "latency_ms": latency_ms,
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
