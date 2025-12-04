import os
import time
import requests
from mcp.server.fastmcp import FastMCP

DD_API_KEY = os.getenv("DD_API_KEY")
DD_APP_KEY = os.getenv("DD_APP_KEY")
DD_SITE = os.getenv("DD_SITE", "datadoghq.com")

if not (DD_API_KEY and DD_APP_KEY):
    raise SystemExit("DD_API_KEY and DD_APP_KEY must be set")

def dd_get(path: str, params: dict | None = None):
    url = f"https://api.{DD_SITE}{path}"
    headers = {
        "DD-API-KEY": DD_API_KEY,
        "DD-APPLICATION-KEY": DD_APP_KEY,
    }
    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

mcp = FastMCP("retail_lab_datadog")

@mcp.tool()
async def get_metric_timeseries(metric: str, hours: int = 1, query_filter: str = "env:retail-lab") -> dict:
    """Get Datadog metric timeseries for a given metric over last N hours."""
    now = int(time.time())
    start = now - hours * 3600
    q = f"sum:{metric}{{{query_filter}}}.rollup(sum,60)"
    data = dd_get("/api/v1/query", {"from": start, "to": now, "query": q})
    return data

@mcp.tool()
async def get_checkout_success_rate(hours: int = 1) -> str:
    """Calculate checkout success rate over last N hours."""
    now = int(time.time())
    start = now - hours * 3600

    q_total = "sum:retail.checkout.requests{env:retail-lab}.as_count()"
    q_good = "sum:retail.checkout.requests{env:retail-lab,status:success}.as_count()"

    total = dd_get("/api/v1/query", {"from": start, "to": now, "query": q_total})
    good = dd_get("/api/v1/query", {"from": start, "to": now, "query": q_good})

    def last_point(series):
        if not series or not series[0].get("pointlist"):
            return 0.0
        return series[0]["pointlist"][-1][1] or 0.0

    total_v = last_point(total.get("series", []))
    good_v = last_point(good.get("series", []))

    if total_v == 0:
        return "No checkout traffic in this period."

    rate = 100.0 * good_v / total_v
    return f"Checkout success rate over last {hours}h is approximately {rate:.2f}% (good={good_v}, total={total_v})."

@mcp.tool()
async def list_slos() -> dict:
    """List SLOs from Datadog."""
    return dd_get("/api/v1/slo", {})

if __name__ == "__main__":
    mcp.run(transport="stdio")
