# Azure CLI script for AKS, ACR, VNet provisioning
RG=constructos-rg
LOCATION=eastus
VNET=constructos-vnet
AKS=constructos-aks
ACR=constructosacr

az group create --name $RG --location $LOCATION
az network vnet create --resource-group $RG --name $VNET --address-prefix 10.0.0.0/16
az network vnet subnet create --resource-group $RG --vnet-name $VNET --name aks-subnet --address-prefix 10.0.1.0/24
az acr create --resource-group $RG --name $ACR --sku Premium --location $LOCATION
az aks create \
  --resource-group $RG \
  --name $AKS \
  --node-count 3 \
  --enable-private-cluster \
  --network-plugin azure \
  --vnet-subnet-id $(az network vnet subnet show --resource-group $RG --vnet-name $VNET --name aks-subnet --query id -o tsv) \
  --enable-managed-identity \
  --enable-aad \
  --enable-rbac \
  --generate-ssh-keys
az aks update -n $AKS -g $RG --attach-acr $ACR
