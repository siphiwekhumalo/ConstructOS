output "aks_cluster_name" { value = azurerm_kubernetes_cluster.aks.name }
output "acr_login_server" { value = azurerm_container_registry.acr.login_server }
output "postgres_fqdn" { value = azurerm_postgresql_flexible_server.pg.fqdn }
output "redis_hostname" { value = azurerm_redis_cache.redis.hostname }
output "keyvault_uri" { value = azurerm_key_vault.kv.vault_uri }
output "appgw_public_ip" { value = azurerm_public_ip.appgw.ip_address }
