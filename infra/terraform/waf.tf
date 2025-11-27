resource "azurerm_public_ip" "appgw" {
  name                = "appgw-public-ip"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_application_gateway" "appgw" {
  name                = var.appgw_name
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  sku {
    name = "WAF_v2"
    tier = "WAF_v2"
  }
  gateway_ip_configuration {
    name      = "appgw-ip-config"
    subnet_id = azurerm_subnet.waf.id
  }
  frontend_ip_configuration {
    name                 = "appgw-frontend-ip"
    public_ip_address_id = azurerm_public_ip.appgw.id
  }
  waf_configuration {
    enabled            = true
    firewall_mode      = "Prevention"
    rule_set_type      = "OWASP"
    rule_set_version   = "3.2"
  }
}
