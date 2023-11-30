import type { AxiosInstance } from 'axios'

export interface Datacenter {
  name: string
  rooms: Array<DatacenterRoom>
  tags: any
}
  
export interface DatacenterRoom {
  name: string
  dimensions: {
  width: number
  depth: number
  }
  rows: [
    {
      racks: [
        {
          name: string
          fillrate: number
        }
      ]
      nbracks: number
    }
  ]
}

export interface Rack {
  room: String
  name: String
  nodes: [
    {
      infrastructure: String
    }
  ]
}

export interface Infrastructure {
  name: string
  description: string
  layout: [
    {
      rack: string
      nodes: [NodeEquipment]
      network: [NetworkEquipment]
      storage: [StorageEquipment]
    }
  ]
}

export interface NodeEquipment {
  type: {
    id: string
    model: string
    height: number
    width: number
    specs: string
    cpu: {
      sockets: number
      model: string
      specs: string
      cores: number
    }
    ram: {
      dimm: number
      size: number
    }
    storage: [
      {
        type: string
        model: string
        size: number
      }
    ]
    netifs: [
      {
        type: string
        bandwidth: number
      }
    ]
  }
  rack: string
  name: string
  slot: number
}

export interface NetworkEquipment {
  type: {
    id: string
    model: string
    height: number
    width: number
    netifs: [
      {
        type: string
        bandwidth: number
        number: number
      }
    ]
  }
  tags: []
  rack: string
  name: string
  slot: number
}

export interface StorageEquipment {
  type: {
    id: string
    model: string
    height: number
    width: number
    disks: [
      {
        type: string
        size: number
        model: string
        number: number
      }
    ]
  }
  tags: []
  rack: string
  name: string
  slot: number
}
