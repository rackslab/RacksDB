/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: GPL-3.0-or-later
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import DatacentersView from '@/views/DatacentersView.vue'

// Mock router used by the view
vi.mock('vue-router', () => ({
  useRouter: () => ({
    resolve: () => ({ fullPath: '/datacenter/paris' })
  })
}))

// Mock HTTP plugin and API composable
const datacentersMock = vi.fn()
vi.mock('@/plugins/http', () => ({
  useHttp: () => ({})
}))
vi.mock('@/composables/RacksDBAPI', () => ({
  useRacksDBAPI: () => ({
    datacenters: datacentersMock
  })
}))

// Mock Leaflet to avoid DOM-heavy behavior
vi.mock('leaflet', () => {
  const addTo = () => ({})
  const on = () => ({})
  return {
    default: {
      map: () => ({ setView: () => ({ on, fitBounds: () => {} }) }),
      tileLayer: () => ({ addTo }),
      marker: () => ({ addTo: () => ({ bindPopup: () => {} }) }),
      latLngBounds: () => ({ extend: () => {} }),
      icon: () => ({})
    }
  }
})

describe('DatacentersView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const flushPromises = () => new Promise((resolve) => setTimeout(resolve))

  test('hides the map when no datacenter has a location', async () => {
    datacentersMock.mockResolvedValueOnce([
      { name: 'paris', rooms: [], location: undefined },
      { name: 'london', rooms: [], location: undefined }
    ])

    const wrapper = mount(DatacentersView, {
      global: {
        stubs: {
          BreadCrumbs: true
        }
      }
    })

    // Wait for onMounted async code
    await flushPromises()
    await nextTick()

    expect(wrapper.vm.showMap).toBe(false)
  })

  test('shows the map when at least one datacenter has a location', async () => {
    datacentersMock.mockResolvedValueOnce([
      {
        name: 'paris',
        rooms: [],
        location: { latitude: 48.85, longitude: 2.35 }
      },
      { name: 'london', rooms: [], location: undefined }
    ])

    const wrapper = mount(DatacentersView, {
      attachTo: document.body,
      global: {
        stubs: {
          BreadCrumbs: true
        }
      }
    })

    await flushPromises()
    await nextTick()

    expect(wrapper.vm.showMap).toBe(true)
  })
})
