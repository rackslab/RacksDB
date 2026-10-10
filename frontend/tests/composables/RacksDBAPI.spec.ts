/*
Copyright (c) 2025 Rackslab

This file is part of RacksDB.

SPDX-License-Identifier: MIT
*/

import { describe, test, expect, vi } from 'vitest'
import { useRacksDBAPI } from '@/composables/RacksDBAPI'

describe('useRacksDBAPI infrastructureGltf', () => {
  test('posts gltf draw endpoint with json response type', async () => {
    const post = vi.fn().mockResolvedValue({
      data: { asset: { version: '2.0' }, buffers: [] }
    })
    const http = { post, get: vi.fn() }
    const api = useRacksDBAPI(http as any)

    const result = await api.infrastructureGltf('mercury')

    expect(post).toHaveBeenCalledWith(
      '/draw/infrastructure/mercury.gltf',
      {},
      {
        responseType: 'json',
        headers: { Accept: 'model/gltf+json' }
      }
    )
    expect(result.asset.version).toBe('2.0')
  })
})
