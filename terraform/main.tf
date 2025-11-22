# Configure the Azure Provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# 1. Create a Resource Group
# The location for this resource group is now being pulled from the variables file.
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.resource_group_location
}

# 2. Create a Storage Account for Blob Storage
# This resource correctly inherits its location from the resource group.
resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# 3. Create a PostgreSQL Server
resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = var.postgres_server_name
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  version                = "14"
  delegated_subnet_id    = null
  private_dns_zone_id    = null
  administrator_login    = "psqladmin"
  administrator_password = var.postgresql_password
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
  zone                   = null
  lifecycle {
    ignore_changes = [
      zone,
    ]
  }
}


# 4. Create an Azure AI Search Service
resource "azurerm_search_service" "search" {
  name                = var.search_service_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "basic"
}

# 5. Create Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_service_name
  location            = "eastus2"
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "OpenAI"
  sku_name            = "S0"
}

# 6. Deploy GPT-4o Model
resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-05-13"
  }
  scale {
    type = "Standard"
  }
}
