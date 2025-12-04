output "cart_service_url" {
  description = "Public URL for cart-service"
  value       = google_cloud_run_v2_service.cart.uri
}

output "checkout_service_url" {
  description = "Public URL for checkout-service"
  value       = google_cloud_run_v2_service.checkout.uri
}

output "payment_service_url" {
  description = "Public URL for payment-service"
  value       = google_cloud_run_v2_service.payment.uri
}
