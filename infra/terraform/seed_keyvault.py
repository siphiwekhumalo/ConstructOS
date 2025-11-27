# Example: Key Vault seed script (Python)
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

key_vault_url = os.environ["KEYVAULT_URI"]
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)

# Upload initial secrets
client.set_secret("postgres-admin", "ChangeMe123!")
client.set_secret("django-secret-key", "your-django-secret-key")
client.set_secret("redis-password", "your-redis-password")
print("Secrets uploaded to Key Vault.")
