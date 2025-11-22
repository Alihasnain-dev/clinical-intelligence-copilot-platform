output "openai_endpoint" {
  value       = azurerm_cognitive_account.openai.endpoint
  description = "The endpoint URL for the Azure OpenAI service."
}

output "openai_key" {
  value       = azurerm_cognitive_account.openai.primary_access_key
  description = "The primary access key for the Azure OpenAI service."
  sensitive   = true
}

output "openai_deployment_name" {
  value       = azurerm_cognitive_deployment.gpt4o.name
  description = "The name of the GPT-4o deployment."
}