/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'

import InfrastructureDetailsView from '@/views/InfrastructureDetailsView.vue'

const infrastructuresMock = vi.fn()
const infrastructureImageSvgMock = vi.fn()

vi.mock('@/plugins/http', () => ({
  useHttp: () => ({})
}))

vi.mock('@/composables/RacksDBAPI', () => ({
  useRacksDBAPI: () => ({
    infrastructures: infrastructuresMock,
    infrastructureImageSvg: infrastructureImageSvgMock
  })
}))

describe('InfrastructureDetailsView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('loads infrastructure details and image blob', async () => {
    infrastructuresMock.mockResolvedValueOnce([
      { name: 'core', layout: [], racks: [], dimensions: { width: 0, depth: 0 } }
    ])
    infrastructureImageSvgMock.mockResolvedValueOnce(
      new Blob(['<svg></svg>'], { type: 'image/svg+xml' })
    )

    const wrapper = mount(InfrastructureDetailsView, {
      props: { name: 'core' },
      global: {
        stubs: { BreadCrumbs: true, Dialog: true, DialogPanel: true, InfrastructureTable: true }
      },
      attachTo: document.body
    })

    await flushPromises()
    await nextTick()

    expect(infrastructuresMock).toHaveBeenCalled()
    expect(infrastructureImageSvgMock).toHaveBeenCalledWith('core')
  })
})
