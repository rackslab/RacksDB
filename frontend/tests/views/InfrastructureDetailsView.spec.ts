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

  test('toggles between 2D and 3D representations', async () => {
    infrastructuresMock.mockResolvedValueOnce([])
    infrastructureImageSvgMock.mockResolvedValueOnce(
      new Blob(['<svg></svg>'], { type: 'image/svg+xml' })
    )

    const wrapper = mount(InfrastructureDetailsView, {
      props: { name: 'core' },
      global: {
        stubs: {
          BreadCrumbs: true,
          Dialog: true,
          DialogPanel: true,
          InfrastructureTable: true,
          InfrastructureScene3D: true
        }
      }
    })
    await flushPromises()

    const [button2d, button3d] = wrapper.findAll('[aria-label="Representation"] button')
    expect(button2d.attributes('aria-pressed')).toBe('true')
    expect(wrapper.find('img').exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'InfrastructureScene3D' }).exists()).toBe(false)

    await button3d.trigger('click')
    expect(button3d.attributes('aria-pressed')).toBe('true')
    expect(wrapper.find('img').exists()).toBe(false)
    const scene = wrapper.findComponent({ name: 'InfrastructureScene3D' })
    expect(scene.exists()).toBe(true)
    expect(scene.props('infrastructureName')).toBe('core')

    await button2d.trigger('click')
    expect(wrapper.find('img').exists()).toBe(true)

    wrapper.unmount()
    expect(URL.revokeObjectURL).toHaveBeenCalled()
  })
})
