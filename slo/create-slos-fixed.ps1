# ==== CONFIG ====
$apiKey = "41914f06e722da82ff95614929053344Y"
$appKey = "e6b425a10996773f0a4ff32fc4a2a8f35817b7dd"
$ddSite = "datadoghq.com"   # change to datadoghq.eu etc. if needed

$baseUri = "https://api.$ddSite/api/v1/slo"

$headers = @{
    "DD-API-KEY"        = $apiKey
    "DD-APPLICATION-KEY" = $appKey
    "Content-Type"       = "application/json"
}

# ==== 1) Checkout Availability SLO ====
$checkoutSloBody = @"
{
  "name": "Checkout Availability â€“ Retail Lab",
  "type": "metric",
  "description": "Percent of successful checkout requests out of total in env:retail-lab.",
  "tags": [
    "env:retail-lab",
    "service:checkout-service",
    "slo:availability",
    "slo:retail-lab"
  ],
  "query": {
    "numerator": "sum:retail.checkout.requests{env:retail-lab,status:success}.as_count()",
    "denominator": "sum:retail.checkout.requests{env:retail-lab}.as_count()"
  },
  "thresholds": [
    {
      "timeframe": "7d",
      "target": 99.0,
      "warning": 99.5
    }
  ]
}
"@

Write-Host "Creating Checkout Availability SLO..."
$checkoutResp = Invoke-RestMethod -Method Post -Uri $baseUri -Headers $headers -Body $checkoutSloBody
$checkoutResp


# ==== 2) Payment Availability SLO ====
$paymentSloBody = @"
{
  "name": "Payment Availability â€“ Retail Lab",
  "type": "metric",
  "description": "Percent of successful payment requests out of total in env:retail-lab.",
  "tags": [
    "env:retail-lab",
    "service:payment-service",
    "slo:availability",
    "slo:retail-lab"
  ],
  "query": {
    "numerator": "sum:retail.payment.requests{env:retail-lab,status:success}.as_count()",
    "denominator": "sum:retail.payment.requests{env:retail-lab}.as_count()"
  },
  "thresholds": [
    {
      "timeframe": "7d",
      "target": 99.0,
      "warning": 99.5
    }
  ]
}
"@

Write-Host "Creating Payment Availability SLO..."
$paymentResp = Invoke-RestMethod -Method Post -Uri $baseUri -Headers $headers -Body $paymentSloBody
$paymentResp


# ==== 3) Cart Add-to-Cart SLO ====
$cartSloBody = @"
{
  "name": "Cart Add-to-Cart â€“ Retail Lab",
  "type": "metric",
  "description": "Percent of successful add-to-cart events out of total in env:retail-lab.",
  "tags": [
    "env:retail-lab",
    "service:cart-service",
    "slo:availability",
    "slo:retail-lab"
  ],
  "query": {
    "numerator": "sum:retail.cart.add_to_cart{env:retail-lab,status:success}.as_count()",
    "denominator": "sum:retail.cart.add_to_cart{env:retail-lab}.as_count()"
  },
  "thresholds": [
    {
      "timeframe": "7d",
      "target": 99.0,
      "warning": 99.5
    }
  ]
}
"@

Write-Host "Creating Cart Add-to-Cart SLO..."
$cartResp = Invoke-RestMethod -Method Post -Uri $baseUri -Headers $headers -Body $cartSloBody
$cartResp


# ==== 4) Retail Observability â€“ Overall SLO ====
# Combined SLO across Cart + Checkout + Payment:
#   good = sum of all success events across all three
#   total = sum of all events across all three

$retailObsSloBody = @"
{
  "name": "Retail Observability â€“ Overall",
  "type": "metric",
  "description": "Overall success across cart, checkout, and payment in env:retail-lab (combined SLI).",
  "tags": [
    "env:retail-lab",
    "slo:retail-observability",
    "slo:retail-lab",
    "service-group:retail-lab-all"
  ],
  "query": {
    "numerator": "sum:retail.checkout.requests{env:retail-lab,status:success}.as_count() + sum:retail.payment.requests{env:retail-lab,status:success}.as_count() + sum:retail.cart.add_to_cart{env:retail-lab,status:success}.as_count()",
    "denominator": "sum:retail.checkout.requests{env:retail-lab}.as_count() + sum:retail.payment.requests{env:retail-lab}.as_count() + sum:retail.cart.add_to_cart{env:retail-lab}.as_count()"
  },
  "thresholds": [
    {
      "timeframe": "7d",
      "target": 99.0,
      "warning": 99.5
    }
  ]
}
"@

Write-Host "Creating Retail Observability â€“ Overall SLO..."
$retailObsResp = Invoke-RestMethod -Method Post -Uri $baseUri -Headers $headers -Body $retailObsSloBody
$retailObsResp

