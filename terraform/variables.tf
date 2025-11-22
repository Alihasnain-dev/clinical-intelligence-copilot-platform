variable "resource_group_name" {
  type        = string
  description = "Name for the resource group that contains every component in this project."
  default     = "Clinical-Intelligence-Platform-RG"
}

variable "resource_group_location" {
  type        = string
  description = "The Azure region where the resources will be deployed."
  default     = "Central US"
}

variable "storage_account_name" {
  type        = string
  description = "Globally unique name for the storage account that hosts images, PDFs, and model artifacts."
  default     = "clinicaldatalake25"
}

variable "postgres_server_name" {
  type        = string
  description = "Name for the Azure PostgreSQL Flexible Server instance."
  default     = "clinical-db-server"
}

variable "search_service_name" {
  type        = string
  description = "Name for the Azure AI Search service that powers the RAG index."
  default     = "clinical-ai-search-service-2025"
}
variable "openai_service_name" {
  type        = string
  description = "Name for the Azure OpenAI service."
  default     = "clinical-openai-service-2025"
}

variable "postgresql_password" {
  type        = string
  description = "The password for the PostgreSQL administrator."
  sensitive   = true # This will prevent the password from being shown in logs
}
