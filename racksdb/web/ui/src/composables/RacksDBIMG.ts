/* Copyright (c) 2022-2023 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later */

import type { AxiosInstance } from 'axios'

export function useRacksDBIMGAPI(http: AxiosInstance) {
  async function racksDBIMGGet(resource: string): Promise<ArrayBuffer> {
    try {
      const response = await http.post(resource)
      return response.data
    } catch (error: any) {
      console.error('Error', error)
      throw error
    }
  }

  async function infrastructureImageSvg(infrastructure: string): Promise<Blob> {
    return new Blob([await racksDBIMGGet(`/draw/infrastructure/${infrastructure}.svg`)], {
      type: 'image/svg+xml'
    })
  }

  async function roomImageSvg(room: string): Promise<Blob> {
    return new Blob([await racksDBIMGGet(`/draw/room/${room}.svg`)], {
      type: 'image/svg+xml'
    })
  }

  return { infrastructureImageSvg, roomImageSvg }
}
