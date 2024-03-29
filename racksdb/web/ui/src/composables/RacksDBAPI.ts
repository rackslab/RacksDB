/* Copyright (c) 2022-2024 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later */

import type { AxiosInstance } from 'axios'

export interface Datacenter {
  name: string
  rooms: Array<DatacenterRoom>
  tags: any
  location?: DatacenterLocation
}

export interface DatacenterLocation {
  longitude: number
  latitude: number
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
  room: string
  name: string
  fillrate: number
}

export interface Infrastructure {
  name: string
  description: string
  tags: []
  layout: [
    {
      rack: string
      nodes: [NodeEquipment]
      network: [NetworkEquipment]
      storage: [StorageEquipment]
      misc: [MiscEquipment]
    }
  ]
}

export interface NodeEquipmentType {
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

export interface NetworkEquipmentType {
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

export interface StorageEquipmentType {
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

export interface MiscEquipmentType {
  id: string
  model: string
  height: number
  width: number
}

export interface NodeEquipment {
  type: NodeEquipmentType
  position: {
    height: number
    width: number
  }
  rack: string
  name: string
  slot: number
  tags: []
}

export interface NetworkEquipment {
  type: NetworkEquipmentType
  position: {
    height: number
    width: number
  }
  tags: []
  rack: string
  name: string
  slot: number
}

export interface StorageEquipment {
  type: StorageEquipmentType
  position: {
    height: number
    width: number
  }
  tags: []
  rack: string
  name: string
  slot: number
}

export interface MiscEquipment {
  type: MiscEquipmentType
  position: {
    height: number
    width: number
  }
  tags: []
  rack: string
  name: string
  slot: number
}

export function useRacksDBAPI(http: AxiosInstance) {
  async function racksDBGet(ressource: string): Promise<any> {
    try {
      const response = await http.get(ressource)
      return response.data
    } catch (error: any) {
      console.error(`Error getting ${ressource}`, error)
      throw error
    }
  }

  async function racksDBIMGPOST(resource: string): Promise<any> {
    try {
      const response = await http.post(resource)
      return response.data
    } catch (error: any) {
      console.error('Error', error)
      throw error
    }
  }

  async function datacenters(): Promise<Array<Datacenter>> {
    const response = (await racksDBGet('datacenters')) as Datacenter[]
    return response
  }

  async function infrastructures(): Promise<Array<Infrastructure>> {
    const response = (await racksDBGet('infrastructures')) as Infrastructure[]
    return response
  }

  async function racks(): Promise<Array<Rack>> {
    const response = (await racksDBGet('racks')) as Rack[]
    return response
  }

  async function infrastructureImageSvg(infrastructure: string): Promise<Blob> {
    return new Blob([await racksDBIMGPOST(`/draw/infrastructure/${infrastructure}.svg`)], {
      type: 'image/svg+xml'
    })
  }

  async function roomImageSvg(room: string): Promise<Blob> {
    return new Blob([await racksDBIMGPOST(`/draw/room/${room}.svg`)], {
      type: 'image/svg+xml'
    })
  }

  return { racksDBGet, datacenters, infrastructures, racks, infrastructureImageSvg, roomImageSvg }
}
