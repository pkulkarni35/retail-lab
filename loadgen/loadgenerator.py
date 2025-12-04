import os
import random
import time
import threading
import requests

CART_URL = os.getenv("CART_URL")
CHECKOUT_URL = os.getenv("CHECKOUT_URL")
PAYMENT_URL = os.getenv("PAYMENT_URL")

if not (CART_URL and CHECKOUT_URL and PAYMENT_URL):
    raise SystemExit("Set CART_URL, CHECKOUT_URL, PAYMENT_URL env vars first")


def hit_cart():
    payload = {
        "item_id": f"sku-{random.randint(100,999)}",
        "name": "Shoe",
        "qty": random.randint(1, 3),
    }
    try:
        r = requests.post(
            f"{CART_URL}/cart/add",
            json=payload,
            timeout=3,
        )
        print("cart", r.status_code)
    except Exception as e:
        print("cart error", e)


def hit_checkout():
    payload = {
        "user_id": f"user-{random.randint(1,10)}",
        "cart_total": round(random.uniform(50, 300), 2),
    }
    try:
        r = requests.post(
            f"{CHECKOUT_URL}/checkout",
            json=payload,
            timeout=5,
        )
        print("checkout", r.status_code)
    except Exception as e:
        print("checkout error", e)


def hit_payment():
    payload = {
        "amount": round(random.uniform(10, 200), 2),
        "currency": "USD",
    }
    try:
        r = requests.post(
            f"{PAYMENT_URL}/pay",
            json=payload,
            timeout=5,
        )
        print("payment", r.status_code)
    except Exception as e:
        print("payment error", e)


def worker():
    while True:
        choice = random.choice([hit_cart, hit_checkout, hit_payment])
        choice()
        time.sleep(random.uniform(0.1, 0.7))


if __name__ == "__main__":
    # start a few threads for parallel load
    for _ in range(5):
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    print("Load generator running. Ctrl+C to stop.")
    while True:
        time.sleep(1)
