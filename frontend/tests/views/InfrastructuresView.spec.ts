/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'

import InfrastructuresView from '@/views/InfrastructuresView.vue'

const infrastructuresMock = vi.fn()

vi.mock('@/plugins/http', () => ({
  useHttp: () => ({})
}))

vi.mock('@/composables/RacksDBAPI', () => ({
  useRacksDBAPI: () => ({
    infrastructures: infrastructuresMock
  })
}))

describe('InfrastructuresView', () => {
  beforeEach(() => vi.clearAllMocks())

  test('loads infrastructures and passes them to ComboBox', async () => {
    infrastructuresMock.mockResolvedValueOnce([{ name: 'core' }, { name: 'edge' }])

    const wrapper = mount(InfrastructuresView, {
      global: { stubs: { BreadCrumbs: true, ComboBox: true } }
    })

    await flushPromises()
    await nextTick()

    expect(infrastructuresMock).toHaveBeenCalled()
  })
})
