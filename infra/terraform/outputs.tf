output "service_urls" {
  description = "Адреси для доступу до сервісів:"
  value = {
    web_app    = "http://${azurerm_linux_virtual_machine.vm.public_ip_address}:8000"
    grafana    = "http://${azurerm_linux_virtual_machine.vm.public_ip_address}:3000"
    prometheus = "http://${azurerm_linux_virtual_machine.vm.public_ip_address}:9090"
  }
}

output "ssh_command" {
  description = "Команда для підключення по SSH:"
  value       = "ssh azureuser@${azurerm_linux_virtual_machine.vm.public_ip_address}"
}