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
    return jsonify({"status": "ok", "service": "payment-service"}), 200


@app.route("/pay", methods=["POST"])
def pay():
    data = request.get_json(silent=True) or {}
    amount = data.get("amount")
    currency = data.get("currency", "USD")

    if amount is None:
        send_dd_metric(
            "retail.payment.requests",
            1,
            tags=[
                "env:retail-lab",
                "service:payment-service",
                "status:error",
                "reason:missing_amount",
            ],
        )
        return jsonify({"error": "amount is required"}), 400

    if random.random() < 0.2:
        send_dd_metric(
            "retail.payment.requests",
            1,
            tags=[
                "env:retail-lab",
                "service:payment-service",
                "status:failed",
            ],
        )
        return jsonify(
            {
                "status": "failed",
                "reason": "payment_gateway_error",
                "amount": amount,
                "currency": currency,
            }
        ), 502

    send_dd_metric(
        "retail.payment.requests",
        1,
        tags=[
            "env:retail-lab",
            "service:payment-service",
            "status:success",
        ],
    )

    return jsonify(
        {
            "status": "success",
            "transaction_id": f"txn_{random.randint(100000, 999999)}",
            "amount": amount,
            "currency": currency,
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
