resource "azurerm_key_vault" "kv" {
  name                        = var.keyvault_name
  location                    = var.location
  resource_group_name         = azurerm_resource_group.main.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "premium"
  purge_protection_enabled    = true
  soft_delete_enabled         = true
  network_acls {
    default_action = "Deny"
    bypass         = ["AzureServices"]
    virtual_network_subnet_ids = [azurerm_subnet.aks.id, azurerm_subnet.postgres.id, azurerm_subnet.redis.id]
  }
}

resource "azurerm_key_vault_access_policy" "aks" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  secret_permissions = ["get", "list"]
}

data "azurerm_client_config" "current" {}
