resource "azurerm_postgresql_flexible_server" "pg" {
  name                   = var.postgres_name
  resource_group_name    = azurerm_resource_group.main.name
  location               = var.location
  administrator_login    = "pgadmin"
  administrator_password = "ChangeMe123!" # Use Key Vault in production
  storage_mb             = 32768
  sku_name               = "Standard_D4s_v3"
  version                = "14"
  zone                   = "1"
  high_availability {
    mode = "ZoneRedundant"
  }
  private_dns_zone_id    = null
  delegated_subnet_id    = azurerm_subnet.postgres.id
}

resource "azurerm_redis_cache" "redis" {
  name                = var.redis_name
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 2
  family              = "P"
  sku_name            = "Premium"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  subnet_id           = azurerm_subnet.redis.id
}
