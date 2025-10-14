/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'

// Mock API composable
const datacentersMock = vi.fn()
const infrastructuresMock = vi.fn()

vi.mock('@/plugins/http', () => ({
  useHttp: () => ({})
}))

vi.mock('@/composables/RacksDBAPI', () => ({
  useRacksDBAPI: () => ({
    datacenters: datacentersMock,
    infrastructures: infrastructuresMock
  })
}))

import HomeViewCards from '@/components/HomeViewCards.vue'

describe('HomeViewCards', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('loads and displays datacenters and infrastructures', async () => {
    datacentersMock.mockResolvedValueOnce([
      { name: 'paris', rooms: [], tags: ['prod'] },
      { name: 'london', rooms: [], tags: ['test'] }
    ])

    infrastructuresMock.mockResolvedValueOnce([
      { name: 'core', description: 'Core infrastructure', tags: ['compute'] },
      { name: 'edge', description: 'Edge infrastructure', tags: ['network'] }
    ])

    const wrapper = mount(HomeViewCards)

    await flushPromises()
    await nextTick()

    expect(wrapper.text()).toContain('2 datacenter')
    expect(wrapper.text()).toContain('2 infrastructure')
    expect(wrapper.text()).toContain('paris')
    expect(wrapper.text()).toContain('london')
    expect(wrapper.text()).toContain('core')
    expect(wrapper.text()).toContain('edge')
  })

  test('displays singular form for single items', async () => {
    datacentersMock.mockResolvedValueOnce([{ name: 'paris', rooms: [], tags: [] }])

    infrastructuresMock.mockResolvedValueOnce([
      { name: 'core', description: 'Core infrastructure', tags: [] }
    ])

    const wrapper = mount(HomeViewCards)

    await flushPromises()
    await nextTick()

    expect(wrapper.text()).toContain('1 datacenter')
    expect(wrapper.text()).toContain('1 infrastructure')
  })

  test('displays tags for datacenters and infrastructures', async () => {
    datacentersMock.mockResolvedValueOnce([{ name: 'paris', rooms: [], tags: ['prod', 'eu'] }])

    infrastructuresMock.mockResolvedValueOnce([
      { name: 'core', description: 'Core infrastructure', tags: ['compute', 'storage'] }
    ])

    const wrapper = mount(HomeViewCards)

    await flushPromises()
    await nextTick()

    expect(wrapper.text()).toContain('#prod')
    expect(wrapper.text()).toContain('#eu')
    expect(wrapper.text()).toContain('#compute')
    expect(wrapper.text()).toContain('#storage')
  })
})
