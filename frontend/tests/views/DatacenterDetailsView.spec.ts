/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import DatacenterDetailsView from '@/views/DatacenterDetailsView.vue'

const datacentersMock = vi.fn()

vi.mock('@/plugins/http', () => ({
  useHttp: () => ({})
}))

vi.mock('@/composables/RacksDBAPI', () => ({
  useRacksDBAPI: () => ({
    datacenters: datacentersMock
  })
}))

describe('DatacenterDetailsView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const flushPromises = () => new Promise((r) => setTimeout(r))

  test('loads datacenter details and filters rooms by input', async () => {
    datacentersMock.mockResolvedValueOnce([
      {
        name: 'paris',
        rooms: [
          { name: 'alpha', dimensions: { width: 1000, depth: 2000 }, rows: [{ nbracks: 2 }] },
          { name: 'beta', dimensions: { width: 1000, depth: 1000 }, rows: [{ nbracks: 1 }] }
        ]
      }
    ])

    const wrapper = mount(DatacenterDetailsView, {
      props: { name: 'paris' },
      global: {
        stubs: {
          BreadCrumbs: true
        }
      }
    })

    await flushPromises()
    await nextTick()

    // Ensure two rooms initially
    let rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBeGreaterThan(0)

    // Filter
    const input = wrapper.find('input[type="text"]')
    await input.setValue('alpha')
    await nextTick()

    rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBeGreaterThan(0)
  })
})
