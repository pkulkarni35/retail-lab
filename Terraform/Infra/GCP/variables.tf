variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "asia-south1"
}

variable "image" {
  type = string
  # e.g. "asia-south1-docker.pkg.dev/retail-lab-praveen/repo/inventory:v1"
}
