provider "azurerm" {
  features = {}
}

resource "azurerm_resource_group" "main" {
  name     = "constructos-rg"
  location = "East US"
}

resource "azurerm_virtual_network" "main" {
  name                = "constructos-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "postgres" {
  name                 = "postgres-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_subnet" "redis" {
  name                 = "redis-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.3.0/24"]
}

resource "azurerm_subnet" "waf" {
  name                 = "waf-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.4.0/24"]
}

resource "azurerm_container_registry" "acr" {
  name                = "constructosacr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Premium"
  admin_enabled       = false
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "constructos-aks"
  location            = azurerm_resource_group.main.location
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

resource "azurerm_key_vault" "akv" {
  name                = "constructos-akv"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "premium"
  purge_protection_enabled = true
  soft_delete_enabled = true
  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    virtual_network_subnet_ids = [azurerm_subnet.aks.id]
  }
}

resource "azurerm_postgresql_flexible_server" "db" {
  name                   = "constructos-db"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  administrator_login    = "constructosadmin"
  administrator_password = "${var.db_password}"
  storage_mb             = 32768
  sku_name               = "Standard_D2s_v3"
  version                = "13"
  zone_redundant         = true
  high_availability      = "ZoneRedundant"
  private_dns_zone_id    = azurerm_private_dns_zone.postgres.id
  delegated_subnet_id    = azurerm_subnet.postgres.id
}

resource "azurerm_redis_cache" "redis" {
  name                = "constructos-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 2
  family              = "P"
  sku_name            = "Premium"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  subnet_id           = azurerm_subnet.redis.id
}

resource "azurerm_application_gateway" "waf" {
  name                = "constructos-waf"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }
  gateway_ip_configuration {
    name      = "appgw-ip-config"
    subnet_id = azurerm_subnet.waf.id
  }
  waf_configuration {
    enabled            = true
    firewall_mode      = "Prevention"
    rule_set_type      = "OWASP"
    rule_set_version   = "3.2"
  }
}
