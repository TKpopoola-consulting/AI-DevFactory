resource "google_cloud_run_service" "app" {
  name     = var.app_name
  location = var.region
  
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/${var.app_name}:latest"
        ports {
          container_port = 8080
        }
      }
      service_account_name = google_service_account.cloudrun.email
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_policy" "public" {
  location = google_cloud_run_service.app.location
  service  = google_cloud_run_service.app.name
  
  policy_data = data.google_iam_policy.public.policy_data
}

data "google_iam_policy" "public" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers"
    ]
  }
}

resource "google_service_account" "cloudrun" {
  account_id = "${var.app_name}-sa"
}