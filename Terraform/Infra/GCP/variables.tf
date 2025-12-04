variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "GCP region for Cloud Run"
  default     = "asia-south1"
}

variable "image_cart" {
  type        = string
  description = "Container image for cart-service"
}

variable "image_checkout" {
  type        = string
  description = "Container image for checkout-service"
}

variable "image_payment" {
  type        = string
  description = "Container image for payment-service"
}

variable "dd_api_key" {
  type        = string
  description = "Datadog API key"
  sensitive   = true
}

variable "dd_site" {
  type        = string
  description = "Datadog site domain"
  default     = "datadoghq.com"
}
variable "image_loadgen" {
  description = "Container image for the load generator Cloud Run job"
  type        = string
}


