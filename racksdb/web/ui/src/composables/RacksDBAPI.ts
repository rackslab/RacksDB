/* Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later */

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
