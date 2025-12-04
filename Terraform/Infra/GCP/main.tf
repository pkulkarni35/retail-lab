terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_v2_service" "cart" {
  name     = "cart-service"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.image_cart

      ports {
        container_port = 8080
      }

      env {
        name  = "SERVICE_NAME"
        value = "cart-service"
      }

      env {
        name  = "DD_API_KEY"
        value = var.dd_api_key
      }

      env {
        name  = "DD_SITE"
        value = var.dd_site
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_v2_service" "checkout" {
  name     = "checkout-service"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.image_checkout

      ports {
        container_port = 8080
      }

      env {
        name  = "SERVICE_NAME"
        value = "checkout-service"
      }

      env {
        name  = "DD_API_KEY"
        value = var.dd_api_key
      }

      env {
        name  = "DD_SITE"
        value = var.dd_site
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_v2_service" "payment" {
  name     = "payment-service"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.image_payment

      ports {
        container_port = 8080
      }

      env {
        name  = "SERVICE_NAME"
        value = "payment-service"
      }

      env {
        name  = "DD_API_KEY"
        value = var.dd_api_key
      }

      env {
        name  = "DD_SITE"
        value = var.dd_site
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_v2_job" "loadgen" {
  name     = "retail-loadgen-job"
  location = var.region

  template {
    template {
      containers {
        image = var.image_loadgen

        env {
          name  = "CART_URL"
          value = google_cloud_run_v2_service.cart.uri
        }

        env {
          name  = "CHECKOUT_URL"
          value = google_cloud_run_v2_service.checkout.uri
        }

        env {
          name  = "PAYMENT_URL"
          value = google_cloud_run_v2_service.payment.uri
        }
      }
    }
  }
}

