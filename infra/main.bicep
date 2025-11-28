param location string = 'eastus'
param aksName string = 'constructos-aks'
param acrName string = 'constructosacr'
param vnetName string = 'constructos-vnet'

resource vnet 'Microsoft.Network/virtualNetworks@2022-07-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: { addressPrefixes: [ '10.0.0.0/16' ] }
    subnets: [
      { name: 'aks-subnet'; properties: { addressPrefix: '10.0.1.0/24' } }
      { name: 'db-subnet'; properties: { addressPrefix: '10.0.2.0/24' } }
      { name: 'bastion-subnet'; properties: { addressPrefix: '10.0.3.0/24' } }
    ]
  }
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: acrName
  location: location
  sku: { name: 'Premium' }
  properties: { adminUserEnabled: false }
}

resource aks 'Microsoft.ContainerService/managedClusters@2023-01-01' = {
  name: aksName
  location: location
  properties: {
    kubernetesVersion: '1.28.3'
    dnsPrefix: 'constructos'
    networkProfile: {
      networkPlugin: 'azure'
      networkPolicy: 'azure'
      serviceCidr: '10.0.4.0/24'
      dnsServiceIP: '10.0.4.10'
      dockerBridgeCidr: '172.17.0.1/16'
      podCidr: '10.244.0.0/16'
      outboundType: 'userDefinedRouting'
    }
    apiServerAccessProfile: { enablePrivateCluster: true }
    agentPoolProfiles: [
      {
        name: 'nodepool1'
        count: 3
        vmSize: 'Standard_DS3_v2'
        vnetSubnetID: vnet.properties.subnets[0].id
        osType: 'Linux'
        mode: 'System'
      }
    ]
    identity: { type: 'SystemAssigned' }
    enableRBAC: true
  }
}
