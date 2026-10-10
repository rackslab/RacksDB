/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

import InfrastructureScene3D from '@/components/InfrastructureScene3D.vue'

const infrastructureGltfMock = vi.fn()

vi.mock('@/plugins/http', () => ({
  useHttp: () => ({})
}))

vi.mock('@/composables/RacksDBAPI', () => ({
  useRacksDBAPI: () => ({
    infrastructureGltf: infrastructureGltfMock
  })
}))

vi.mock('three', () => {
  class Vector3 {
    x = 0
    y = 0
    z = 0
    set(x: number, y: number, z: number) {
      this.x = x
      this.y = y
      this.z = z
      return this
    }
    copy() {
      return this
    }
  }
  return {
    Scene: class {
      add() {}
      background = null
    },
    Color: class {
      setHex() {}
    },
    PerspectiveCamera: class {
      position = new Vector3()
      aspect = 1
      updateProjectionMatrix() {}
    },
    WebGLRenderer: class {
      domElement = document.createElement('canvas')
      outputColorSpace = ''
      capabilities = { getMaxAnisotropy: () => 1 }
      setSize() {}
      setPixelRatio() {}
      dispose() {}
      render() {}
    },
    SRGBColorSpace: 'srgb',
    AmbientLight: class {},
    HemisphereLight: class {},
    DirectionalLight: class {
      position = new Vector3()
    },
    Box3: class {
      isEmpty() {
        return true
      }
      setFromObject() {
        return this
      }
      getCenter() {
        return new Vector3()
      }
      getSize() {
        return new Vector3()
      }
    },
    Vector3,
    Raycaster: class {
      setFromCamera() {}
      intersectObjects() {
        return []
      }
    },
    Vector2: class {
      x = 0
      y = 0
    }
  }
})

vi.mock('three/examples/jsm/controls/OrbitControls.js', () => ({
  OrbitControls: class {
    enableDamping = true
    target = { copy() {} }
    update() {}
    dispose() {}
  }
}))

vi.mock('three/examples/jsm/loaders/GLTFLoader.js', () => ({
  GLTFLoader: class {
    parse(_json: string, _path: string, onLoad: (gltf: { scene: object }) => void) {
      onLoad({
        scene: {
          traverse() {},
          children: []
        }
      })
    }
  }
}))

describe('InfrastructureScene3D', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('loads gltf on mount', async () => {
    infrastructureGltfMock.mockResolvedValueOnce({
      asset: { version: '2.0' },
      buffers: [{ uri: 'data:application/octet-stream;base64,AA==', byteLength: 1 }]
    })

    mount(InfrastructureScene3D, {
      props: { infrastructureName: 'mercury' },
      attachTo: document.body
    })

    await flushPromises()

    expect(infrastructureGltfMock).toHaveBeenCalledWith('mercury')
  })

  test('toggles fullscreen and camera mode', async () => {
    infrastructureGltfMock.mockResolvedValueOnce({
      asset: { version: '2.0' },
      buffers: [{ uri: 'data:application/octet-stream;base64,AA==', byteLength: 1 }]
    })

    const wrapper = mount(InfrastructureScene3D, {
      props: { infrastructureName: 'mercury' },
      attachTo: document.body
    })

    await flushPromises()

    expect(wrapper.attributes('data-fullscreen')).toBe('false')
    expect(wrapper.attributes('data-camera-mode')).toBe('free')

    await wrapper.get('button:last-child').trigger('click')
    expect(wrapper.attributes('data-fullscreen')).toBe('true')

    const orbitButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Orbit racks'))
    await orbitButton!.trigger('click')
    expect(wrapper.attributes('data-camera-mode')).toBe('turntable')
  })

  test('shows error when gltf fetch fails', async () => {
    infrastructureGltfMock.mockRejectedValueOnce({
      response: { data: { description: 'Unable to find infrastructure fail in database' } }
    })

    const wrapper = mount(InfrastructureScene3D, {
      props: { infrastructureName: 'fail' },
      attachTo: document.body
    })

    await flushPromises()

    expect(wrapper.text()).toContain('Unable to find infrastructure fail in database')
  })
})
