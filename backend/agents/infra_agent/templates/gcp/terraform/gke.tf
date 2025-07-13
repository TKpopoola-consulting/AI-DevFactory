resource "google_container_cluster" "primary" {
  name     = "${var.app_name}-gke"
  location = var.region
  
  remove_default_node_pool = true
  initial_node_count       = 1

  node_pool {
    name       = "default-pool"
    node_count = 1

    node_config {
      machine_type = "e2-medium"
      disk_size_gb = 100
    }
  }
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "${google_container_cluster.primary.name}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.node_count

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 100
  }
}