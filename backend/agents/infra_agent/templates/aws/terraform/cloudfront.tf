resource "google_sql_database_instance" "main" {
  name             = "${var.app_name}-sql"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_network
    }
  }
}

resource "google_sql_database" "app_db" {
  name     = var.db_name
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "app_user" {
  name     = var.db_user
  instance = google_sql_database_instance.main.name
  password = var.db_password
}