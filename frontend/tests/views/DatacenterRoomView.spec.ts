/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import DatacenterRoomView from '@/views/DatacenterRoomView.vue'

const datacentersMock = vi.fn()
const infrastructuresMock = vi.fn()
const roomImageSvgMock = vi.fn()

vi.mock('@/plugins/http', () => ({
  useHttp: () => ({})
}))

vi.mock('@/composables/RacksDBAPI', () => ({
  useRacksDBAPI: () => ({
    datacenters: datacentersMock,
    infrastructures: infrastructuresMock,
    roomImageSvg: roomImageSvgMock
  })
}))

describe('DatacenterRoomView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const flushPromises = () => new Promise((resolve) => setTimeout(resolve))

  test('lists racks for the selected room and filters with input', async () => {
    infrastructuresMock.mockResolvedValueOnce([{ name: 'core', layout: [] }])

    datacentersMock.mockResolvedValueOnce([
      {
        name: 'paris',
        rooms: [
          {
            name: 'roomA',
            rows: [
              {
                racks: [
                  { name: 'R01', fillrate: 0.1 },
                  { name: 'R02', fillrate: 0 }
                ]
              }
            ]
          }
        ]
      }
    ])

    roomImageSvgMock.mockResolvedValueOnce(new Blob(['<svg></svg>'], { type: 'image/svg+xml' }))

    const wrapper = mount(DatacenterRoomView, {
      props: {
        datacenterName: 'paris',
        datacenterRoom: 'roomA'
      },
      global: {
        stubs: {
          BreadCrumbs: true,
          DatacenterListInfrastructures: true
        }
      }
    })

    await flushPromises()
    await nextTick()

    // Initially, both racks are present
    expect(wrapper.findAll('tbody tr').length).toBeGreaterThan(0)

    // Filter by name
    const input = wrapper.find('input[type="text"]')
    await input.setValue('R01')
    await nextTick()

    // Only one rack should remain visible in filtered table
    const rows = wrapper.findAll('tbody tr')
    // Count rows with real rack entries (skip possible empty state rows)
    const rackRows = rows.filter((tr) => tr.findAll('td').length === 3)
    expect(rackRows.length).toBe(1)
  })
})
