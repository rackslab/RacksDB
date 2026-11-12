/*
Copyright (c) 2026 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

import InfrastructureScene3D from '@/components/InfrastructureScene3D.vue'
import type { CameraMode, HoveredEquipment } from '@/lib/scene3d'

const infrastructureGlbMock = vi.fn()
const createViewerMock = vi.fn()
const viewerMock = { dispose: vi.fn(), resetCamera: vi.fn(), setMode: vi.fn() }

vi.mock('@/plugins/http', () => ({
  useHttp: () => ({})
}))

vi.mock('@/composables/RacksDBAPI', () => ({
  useRacksDBAPI: () => ({
    infrastructureGlb: infrastructureGlbMock
  })
}))

vi.mock('@/lib/scene3d', () => ({
  createViewer: createViewerMock
}))

describe('InfrastructureScene3D', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  test('creates viewer with glTF binary data', async () => {
    const data = new ArrayBuffer(8)
    infrastructureGlbMock.mockResolvedValueOnce(data)
    createViewerMock.mockResolvedValueOnce(viewerMock)
    const wrapper = mount(InfrastructureScene3D, { props: { infrastructureName: 'mercury' } })
    expect(wrapper.text()).toContain('Loading 3D representation')
    await flushPromises()
    expect(infrastructureGlbMock).toHaveBeenCalledWith('mercury')
    expect(createViewerMock).toHaveBeenCalledWith(
      expect.any(HTMLElement),
      data,
      expect.any(Function),
      expect.any(Function)
    )
    expect(wrapper.text()).not.toContain('Loading 3D representation')
    await wrapper.find('button[title="Reset view"]').trigger('click')
    expect(viewerMock.resetCamera).toHaveBeenCalled()
    wrapper.unmount()
    expect(viewerMock.dispose).toHaveBeenCalled()
  })

  test('toggles turntable camera mode', async () => {
    infrastructureGlbMock.mockResolvedValueOnce(new ArrayBuffer(8))
    createViewerMock.mockResolvedValueOnce(viewerMock)
    const wrapper = mount(InfrastructureScene3D, { props: { infrastructureName: 'mercury' } })
    await flushPromises()
    const onModeChange = createViewerMock.mock.calls[0][3] as (mode: CameraMode) => void
    const button = wrapper.find('button[title="Orbit around racks"]')
    expect(button.attributes('aria-pressed')).toBe('false')
    await button.trigger('click')
    expect(viewerMock.setMode).toHaveBeenLastCalledWith('turntable')
    // Viewer notifies mode changes, including switches to free mode on user clicks.
    onModeChange('turntable')
    await flushPromises()
    expect(button.attributes('aria-pressed')).toBe('true')
    await button.trigger('click')
    expect(viewerMock.setMode).toHaveBeenLastCalledWith('free')
    onModeChange('free')
    await flushPromises()
    expect(button.attributes('aria-pressed')).toBe('false')
    wrapper.unmount()
  })

  test('displays hovered equipment', async () => {
    infrastructureGlbMock.mockResolvedValueOnce(new ArrayBuffer(8))
    createViewerMock.mockResolvedValueOnce(viewerMock)
    const wrapper = mount(InfrastructureScene3D, { props: { infrastructureName: 'mercury' } })
    await flushPromises()
    const onHover = createViewerMock.mock.calls[0][2] as (eq: HoveredEquipment | null) => void
    onHover({ name: 'mecn0001', category: 'node', type: 'sm220bt', rack: 'R1-A01' })
    await flushPromises()
    expect(wrapper.text()).toContain('mecn0001')
    expect(wrapper.text()).toContain('rack R1-A01')
    onHover(null)
    await flushPromises()
    expect(wrapper.text()).not.toContain('mecn0001')
  })

  test('displays error when API fails', async () => {
    infrastructureGlbMock.mockRejectedValueOnce(new Error('HTTP 400'))
    const wrapper = mount(InfrastructureScene3D, { props: { infrastructureName: 'mercury' } })
    await flushPromises()
    expect(createViewerMock).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Unable to load 3D representation of infrastructure mercury')
    expect(wrapper.find('button').exists()).toBe(false)
  })

  test('disposes viewer created after unmount', async () => {
    let resolveData: (data: ArrayBuffer) => void = () => {}
    infrastructureGlbMock.mockReturnValueOnce(
      new Promise((resolve) => {
        resolveData = resolve
      })
    )
    createViewerMock.mockResolvedValueOnce(viewerMock)
    const wrapper = mount(InfrastructureScene3D, { props: { infrastructureName: 'mercury' } })
    wrapper.unmount()
    resolveData(new ArrayBuffer(8))
    await flushPromises()
    // Viewer is not created, or disposed immediately if it was.
    expect(createViewerMock.mock.calls.length).toBe(viewerMock.dispose.mock.calls.length)
  })

  test('toggles fullscreen', async () => {
    infrastructureGlbMock.mockResolvedValueOnce(new ArrayBuffer(8))
    createViewerMock.mockResolvedValueOnce(viewerMock)
    const wrapper = mount(InfrastructureScene3D, {
      props: { infrastructureName: 'mercury' },
      attachTo: document.body
    })
    await flushPromises()
    const element = wrapper.element as HTMLElement
    element.requestFullscreen = vi.fn().mockImplementation(async () => {
      Object.defineProperty(document, 'fullscreenElement', { value: element, configurable: true })
      document.dispatchEvent(new Event('fullscreenchange'))
    })
    await wrapper.find('button[title="Fullscreen"]').trigger('click')
    await flushPromises()
    expect(element.requestFullscreen).toHaveBeenCalled()
    expect(wrapper.find('button[title="Exit fullscreen"]').exists()).toBe(true)
    Object.defineProperty(document, 'fullscreenElement', { value: null, configurable: true })
    wrapper.unmount()
  })
})
