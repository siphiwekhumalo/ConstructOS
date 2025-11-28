resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  sku                 = "Premium"
  admin_enabled       = false
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_name
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "constructos"
  kubernetes_version  = "1.28.3"
  default_node_pool {
    name       = "nodepool1"
    node_count = 3
    vm_size    = "Standard_DS3_v2"
    vnet_subnet_id = azurerm_subnet.aks.id
  }
  identity {
    type = "SystemAssigned"
  }
  network_profile {
    network_plugin = "azure"
    network_policy = "azure"
  }
  api_server_access_profile {
    enable_private_cluster = true
  }
  role_based_access_control {
    enabled = true
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "user" {
  name                  = "userpool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = "Standard_DS3_v2"
  node_count            = 2
  vnet_subnet_id        = azurerm_subnet.aks.id
  mode                  = "User"
}
